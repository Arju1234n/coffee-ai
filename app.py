import asyncio
import streamlit as st

from google.adk.runners import InMemoryRunner
from google.genai import types

from agent import root_agent


st.set_page_config(
    page_title="AI Barista",
    page_icon="☕",
    layout="centered"
)

st.title("☕ AI Barista")
st.write("Ask me what coffee you should order.")


if "runner" not in st.session_state:
    st.session_state.runner = InMemoryRunner(
        agent=root_agent,
        app_name="coffee_ai"
    )

if "user_id" not in st.session_state:
    st.session_state.user_id = "customer_1"

if "session_id" not in st.session_state:
    session = asyncio.run(
        st.session_state.runner.session_service.create_session(
            app_name="coffee_ai",
            user_id=st.session_state.user_id
        )
    )
    st.session_state.session_id = session.id

if "messages" not in st.session_state:
    st.session_state.messages = []


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


user_input = st.chat_input(
    "Example: I want a cold coffee under ₹250"
)


if user_input:
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    with st.chat_message("user"):
        st.markdown(user_input)

    async def get_response():
        content = types.Content(
            role="user",
            parts=[types.Part(text=user_input)]
        )

        response_text = ""

        async for event in st.session_state.runner.run_async(
            user_id=st.session_state.user_id,
            session_id=st.session_state.session_id,
            new_message=content
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        response_text += part.text

        return response_text

    response = asyncio.run(get_response())

    st.session_state.messages.append(
        {"role": "assistant", "content": response}
    )

    with st.chat_message("assistant"):
        st.markdown(response)

