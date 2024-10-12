import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from agents import hotel_checkin_agent, GraphState

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
        try:
            # Initialize the state with the current message and step count
            initial_state = GraphState(messages=[HumanMessage(content=prompt)])
            response = hotel_checkin_agent.invoke(initial_state)
            for message in response["messages"]:
                if isinstance(message, AIMessage):
                    st.markdown(message.content)
                    st.session_state.messages.append({"role": "assistant", "content": message.content})
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.session_state.messages.append({"role": "assistant", "content": "I apologize, but an error occurred. Please try again or contact the front desk for assistance."})