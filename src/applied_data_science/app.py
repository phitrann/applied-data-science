# # Adapted from https://docs.streamlit.io/knowledge-base/tutorials/build-conversational-apps#build-a-simple-chatbot-gui-with-streaming
# import os

# os.environ["HF_HOME"] = "/space/hotel/phit/personal/experiments/weights"
# os.environ["TORCH_HOME"] = "/space/hotel/phit/personal/experiments/weights"
# import base64
# import gc
# import random
# import tempfile
# import time
# import uuid

# import streamlit as st

# from client import RAGClient

# MODEL = "mistral"


# if "id" not in st.session_state:
#     st.session_state.id = uuid.uuid4()
#     st.session_state.file_cache = {}

# session_id = st.session_state.id
# client = None


# def reset_chat():
#     st.session_state.messages = []
#     st.session_state.context = None
#     gc.collect()


# def display_pdf(file):
#     # Opening file from file path

#     st.markdown("### PDF Preview")
#     base64_pdf = base64.b64encode(file.read()).decode("utf-8")

#     # Embedding PDF in HTML
#     pdf_display = f"""<iframe src="data:application/pdf;base64,{base64_pdf}" width="400" height="100%" type="application/pdf"
#                         style="height:100vh; width:100%"
#                     >
#                     </iframe>"""

#     # Displaying File
#     st.markdown(pdf_display, unsafe_allow_html=True)


# with st.sidebar:
#     uploaded_file = st.file_uploader("Choose your `.pdf` file", type="pdf")
#     if uploaded_file is not None:
#         with tempfile.NamedTemporaryFile() as temp_file, st.status(
#             "Processing document", expanded=False, state="running"
#         ):
#             with open(temp_file.name, "wb") as f:
#                 f.write(uploaded_file.getvalue())
#             file_key = f"{session_id}-{uploaded_file.name}"
#             st.write("Indexing...")
#             if file_key not in st.session_state.file_cache:
#                 client = RAGClient(files=temp_file.name)
#                 st.session_state.file_cache[file_key] = client
#             else:
#                 client = st.session_state.file_cache[file_key]
#             st.write("Complete, ask your questions...")

#         display_pdf(uploaded_file)


# col1, col2 = st.columns([6, 1])

# with col1:
#     st.header(f"Chat with Document")

# with col2:
#     st.button("Clear ↺", on_click=reset_chat)


# # Initialize chat history
# if "messages" not in st.session_state:
#     reset_chat()


# # Display chat messages from history on app rerun
# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])


# # Accept user input
# if prompt := st.chat_input("What's up?"):
#     if uploaded_file is None:
#         st.exception(FileNotFoundError("Please upload a document first!"))
#         st.stop()

#     # Add user message to chat history
#     st.session_state.messages.append({"role": "user", "content": prompt})
#     # Display user message in chat message container
#     with st.chat_message("user"):
#         st.markdown(prompt)

#     # Display assistant response in chat message container
#     with st.chat_message("assistant"):
#         message_placeholder = st.empty()
#         full_response = ""
#         # context = st.session_state.context

#         # Simulate stream of response with milliseconds delay
#         for chunk in client.stream(prompt):
#             full_response += chunk
#             message_placeholder.markdown(full_response + "▌")

#         message_placeholder.markdown(full_response)
#         # st.session_state.context = ctx

#     # Add assistant response to chat history
#     st.session_state.messages.append({"role": "assistant", "content": full_response})


import os
os.environ["HF_HOME"] = "/space/hotel/phit/personal/experiments/weights"
os.environ["TORCH_HOME"] = "/space/hotel/phit/personal/experiments/weights"


import base64
import gc
import random
import tempfile
import time
import uuid
import streamlit as st
import pandas as pd

from client import RAGClient

# Set page config
st.set_page_config(page_title="Job Recommendation System", layout="wide")

MODEL = "mistral"

# Read the JSONL data into a DataFrame
df = pd.read_json("/space/hotel/phit/personal/applied-data-science/data/crawl/vnw.jsonl", lines=True)


if "id" not in st.session_state:
    st.session_state.id = uuid.uuid4()
    st.session_state.file_cache = {}

session_id = st.session_state.id
client = None

def reset_chat():
    st.session_state.messages = []
    st.session_state.context = None
    gc.collect()

def display_pdf(file):
    base64_pdf = base64.b64encode(file.read()).decode("utf-8")
    pdf_display = f"""<iframe src="data:application/pdf;base64,{base64_pdf}" width="400" height="100%" type="application/pdf"
                        style="height:100vh; width:100%"
                    >
                    </iframe>"""
    st.markdown(pdf_display, unsafe_allow_html=True)

with st.sidebar:
    uploaded_file = st.file_uploader("Choose your `.pdf` file", type="pdf")
    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile() as temp_file, st.status(
            "Processing document", expanded=False, state="running"
        ):
            with open(temp_file.name, "wb") as f:
                f.write(uploaded_file.getvalue())
            file_key = f"{session_id}-{uploaded_file.name}"
            st.write("Indexing...")
            if file_key not in st.session_state.file_cache:
                client = RAGClient(files=temp_file.name)
                st.session_state.file_cache[file_key] = client
            else:
                client = st.session_state.file_cache[file_key]
            st.write("Complete, ask your questions...")

        display_pdf(uploaded_file)

st.title("Job Recommendation System")



# Instructions
with st.expander("See Instructions"):
    st.subheader("How to use the app")
    st.markdown("""
    - Step 1: Select a Python library of interest in the `Select a Partner tech used in the app` multi-select widget.
    - Step 2: Query results should appear after a short page refresh.
    """)
    
    st.subheader("Tips for searching")
    st.markdown("""
    - To retrieve apps built with LangChain OR Weaviate, make sure that the `Boolean Search` parameter in the sidebar is set to **OR**.
    - To retrieve apps built with LangChain AND Weaviate, make sure that the `Boolean Search` parameter in the sidebar is set to **AND**.
    """)

# Multi-select for partner tech
partner_techs = ["LangChain", "LlamaIndex", "AssemblyAI", "Weaviate", "Clarifai"]
selected_techs = st.multiselect("Select a Partner tech used in the app", partner_techs, default=partner_techs)


# Winning Entries Section
# st.subheader("Top recommendations")

def truncate_text(text, max_length=20):
    if len(text) > max_length:
        return text[:max_length] + " ..."
    return text

def display_section(header, entries):
    # Winning Entries Section
    st.subheader(header)

    # Display winning entries
    num_cols = 5  # Number of columns to display
    cols = st.columns(num_cols)

    for idx, entry in enumerate(entries):
        with cols[idx % num_cols]:
            st.image(f"https://dummyimage.com/600x400/000/fff&text={entry['company_name']}", use_column_width=True)
            st.write(f"#### [{truncate_text(entry['name'])}]({entry['url']})")
            st.write(f"**{entry['job_level']}**")
            st.markdown(f"`{entry['salary']}`")
            
            # # HTML and CSS for hover effect
            # html_content = f"""
            # <div class="hover-container">
            #     <img src="https://dummyimage.com/600x400/000/fff&text={entry['company_name']}" alt="{entry['company_name']}" class="hover-image">
            #     <h4>{truncate_text(entry['name'])}</h4>
            #     <p><strong>{entry['job_level']}</strong></p>
            #     <p>{entry['salary']}</p>
            #     <div class="hover-content">
            #         <p>{entry['job_description']}</p>
            #     </div>
            # </div>
            # """
            # css_content = """
            # <style>
            #     .hover-container {
            #         position: relative;
            #         display: inline-block;
            #         width: 100%;
            #     }
            #     .hover-image {
            #         width: 100%;
            #         height: auto;
            #         display: block;
            #     }
            #     .hover-content {
            #         display: none;
            #         position: absolute;
            #         top: 50%;
            #         left: 50%;
            #         width: 50%;
            #         height: 50%;
            #         background-color: red;
            #         color: white;
            #         text-align: center;
            #         padding: 10px;
            #         box-sizing: border-box;
            #         overflow-y: auto;
            #         z-index: 2;
            #     }
            #     .hover-container:hover .hover-content {
            #         display: block;
            #         overflow-y: scroll;
            #     }
            #     .hover-content p {
            #         max-height: 300px;  /* Adjust this value to fit your layout */
            #         overflow-y: auto;
            #         margin: 0;
            #     }
            # </style>
            # """
            # st.markdown(css_content, unsafe_allow_html=True)
            # st.markdown(html_content, unsafe_allow_html=True)
                
if client:
    entries = list(client.stream(query=""))
    if entries is not []:
        display_section("Top recommendations", entries)
else:
    st.warning("Please upload your resume to display job recommendations.")

# Winning Entries Section
st.subheader("Query Results")


# Example entries data
entries = [
    {
        "title": "Wiki-Search",
        "author": "marcusschiesser",
        "image_url": "https://dummyimage.com/600x400/000/fff&text=Wiki-Search",
        "source_url": "#",
        "techs": ["Weaviate"]
    },
    {
        "title": "AI Reasearch Buddy",
        "author": "bp-high",
        "image_url": "https://dummyimage.com/600x400/000/fff&text=AI+Reasearch+Buddy",
        "source_url": "#",
        "techs": ["Clarifai", "LangChain", "LlamaIndex"]
    },
    {
        "title": "The LLMs Arena",
        "author": "enricd",
        "image_url": "https://dummyimage.com/600x400/000/fff&text=The+LLMs+Arena",
        "source_url": "#",
        "techs": ["LangChain"]
    },
    {
        "title": "Persona Simulator",
        "author": "msull",
        "image_url": "https://dummyimage.com/600x400/000/fff&text=Persona+Simulator",
        "source_url": "#",
        "techs": ["Clarifai"]
    },
    {
        "title": "MusicCritique",
        "author": "reximioluwah",
        "image_url": "https://dummyimage.com/600x400/000/fff&text=MusicCritique",
        "source_url": "#",
        "techs": ["AssemblyAI", "LangChain"]
    }
]

# Display winning entries
num_cols = 5  # Number of columns to display
cols = st.columns(num_cols)

for idx, entry in enumerate(entries):
    with cols[idx % num_cols]:
        st.image(entry["image_url"], use_column_width=True)
        st.markdown(f"#### [{entry['title']}]({entry['source_url']})")
        st.markdown(f"**{entry['author']}**")
        st.markdown(f"[View source]({entry['source_url']})")
        st.markdown(" ".join([f"`{tech}`" for tech in entry["techs"]]))
        

with st.expander("Show Filtered DataFrame (101 apps)"):
    st.dataframe(df)


# Footer
st.markdown("---")
st.markdown("Made with ❤️ for the LLM Hackathon.")