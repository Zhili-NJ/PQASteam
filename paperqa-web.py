import streamlit as st
import os
import pickle
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
openai_token = os.getenv('OPENAI_API_KEY')
os.environ["OPENAI_API_KEY"] = openai_token

from paperqa import Docs

#set the page title and icon
st.set_page_config(page_title="paper QA based on the project you created")

# list all pickle files in the directory
database_dir = './database/'  
all_files = os.listdir(database_dir)
all_programs = [file[:-4] for file in all_files if file.endswith('.pkl')]  # remove .pkl extension

# user selects the program (database)
program = st.selectbox('Choose a program:', ['Create new...'] + all_programs)

# create new program if selected
if program == 'Create new...':
    program = st.text_input('Enter the new program name:')
    if program:
        docs = Docs()
else:
    # load the selected program
    with open(Path(database_dir) / f"{program}.pkl", "rb") as f:
        docs = pickle.load(f)


# put the loading pdf function in sidebar
with st.sidebar:
    st.subheader("Your documents")
    uploaded_file = st.file_uploader(
        "Upload your PDFs here and click on 'Process'", accept_multiple_files=True)

    # process button
    if st.button('Process'):
        with st.spinner("Processing"):
            if uploaded_file is not None:
                for file in uploaded_file:
                    # write the uploaded file to a temporary location
                    with open("temp.pdf", "wb") as f:
                        f.write(file.getbuffer())

                    # add the file to the docs
                    docs.add("temp.pdf")

                    # remove the temporary file
                    os.remove("temp.pdf")
                       
                st.success("The PDF has been processed and added to the database.")
            else:
                st.error("Please upload a PDF.")

            # save the updated docs
            with open(Path(database_dir) / f"{program}.pkl", "wb") as f:
                pickle.dump(docs, f)

    
#stream conversation
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("what can I help with these papers?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        answer = docs.query(prompt)
        #print(type(answer))
        full_response += f"Answer: {answer.answer}\n"
        full_response += f"References: {answer.references}\n"
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})
