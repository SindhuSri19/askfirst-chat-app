import streamlit as st
import requests

BASE_URL = "https://askfirst-backend.onrender.com"

st.set_page_config(
    page_title="AskFirst Chat"
)

st.title("AskFirst AI Chat")

if "thread_id" not in st.session_state:
    st.session_state.thread_id = None


if st.sidebar.button("New Thread"):

    res = requests.post(
        f"{BASE_URL}/threads"
    )

    st.session_state.thread_id = res.json()["id"]


threads = requests.get(
    f"{BASE_URL}/threads"
).json()

st.sidebar.write("Chats")

for thread in threads:

    if st.sidebar.button(
        thread["title"],
        key=thread["id"]
    ):
        st.session_state.thread_id = thread["id"]


if st.session_state.thread_id:

    messages = requests.get(
        f"{BASE_URL}/threads/{st.session_state.thread_id}"
    ).json()

    for msg in messages:

        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    prompt = st.chat_input("Type a message")

    if prompt:

        requests.post(
            f"{BASE_URL}/chat",
            json={
                "thread_id": st.session_state.thread_id,
                "message": prompt
            }
        )

        st.rerun()