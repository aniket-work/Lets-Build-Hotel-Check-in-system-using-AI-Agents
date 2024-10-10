import os
from typing import List, Tuple, Any, Dict
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from tools import validate_pin, check_available_rooms, assign_room, create_access_key, charge_credit_card

system_prompt = """You are a hotel check-in assistant. Your task is to help guests check in by following these steps:
1. Ask for and validate their PIN
2. Check for available rooms
3. Assign a room and provide an access key
4. Confirm that their credit card has been charged

Use the available tools to perform these tasks. Be polite and professional in your interactions."""

human_prompt = "{input}"

chat_prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", human_prompt),
])



load_dotenv()

GROQ_API_KEY = os.getenv('GROQ_API_KEY')

model = ChatGroq(model="mixtral-8x7b-32768", api_key=GROQ_API_KEY)


def should_continue(state):
    messages = state['messages']
    last_message = messages[-1]
    if isinstance(last_message, AIMessage) and "check-in process is complete" in last_message.content.lower():
        return END
    return 'agent'


def run_step(state: Dict[str, Any]) -> Dict[str, Any]:
    messages = state['messages']

    execution = model.invoke(
        chat_prompt.format_prompt(
            input=messages[-1].content,
        ).to_messages()
    )

    messages.append(AIMessage(content=execution.content))

    return {
        'messages': messages
    }


workflow = StateGraph(nodes=[])

workflow.add_node('agent', run_step)

workflow.set_entry_point('agent')

workflow.add_conditional_edges(
    'agent',
    should_continue
)

workflow.add_terminal_node(END)

hotel_checkin_agent = workflow.compile()