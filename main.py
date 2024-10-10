import streamlit as st
from langchain_core.messages import HumanMessage
from agents import hotel_checkin_agent

st.title("Hotel Check-in System")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("How can I assist you with your check-in?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = hotel_checkin_agent.invoke({"input": HumanMessage(content=prompt)})
        st.markdown(response.content)
    st.session_state.messages.append({"role": "assistant", "content": response.content})