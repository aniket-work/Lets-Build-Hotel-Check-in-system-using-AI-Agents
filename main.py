import streamlit as st
import logging
from langchain_core.messages import HumanMessage, AIMessage
from agents import hotel_checkin_agent, GraphState

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logger.info("Starting Hotel Check-in System")

st.title("Hotel Check-in System")

if "messages" not in st.session_state:
    logger.info("Initializing session state")
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("How can I assist you with your check-in?"):
    logger.info(f"Received user input: {prompt}")
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            logger.info("Initializing GraphState and invoking hotel_checkin_agent")
            initial_state = GraphState(messages=[HumanMessage(content=prompt)])
            response = hotel_checkin_agent.invoke(initial_state)
            logger.debug(f"Agent response: {response}")
            for message in response["messages"]:
                if isinstance(message, AIMessage):
                    logger.info(f"Assistant response: {message.content}")
                    st.markdown(message.content)
                    st.session_state.messages.append({"role": "assistant", "content": message.content})
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}", exc_info=True)
            error_message = "I apologize, but an error occurred. Please try again or contact the front desk for assistance."
            st.error(error_message)
            st.session_state.messages.append({"role": "assistant", "content": error_message})

logger.info("Hotel Check-in System session ended")