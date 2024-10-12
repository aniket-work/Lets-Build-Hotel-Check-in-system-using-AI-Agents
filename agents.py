from typing import List, Dict, Any, Optional
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from tools import validate_pin, check_available_rooms, assign_room, create_access_key, charge_credit_card
from langchain_core.pydantic_v1 import BaseModel, Field
import os

load_dotenv()

GROQ_API_KEY = os.getenv('GROQ_API_KEY')

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

model = ChatGroq(model="mixtral-8x7b-32768", api_key=GROQ_API_KEY)


class GraphState(BaseModel):
    messages: List[BaseMessage] = Field(default_factory=list)
    current_step: str = Field(default="ask_pin")
    pin: str = Field(default="")
    room_number: str = Field(default="")
    access_key: Optional[str] = Field(default=None)
    charge_amount: float = Field(default=0.0)

    class Config:
        arbitrary_types_allowed = True


def should_continue(state: GraphState) -> str:
    if state.current_step == "complete":
        return END
    return 'agent'


def run_step(state: GraphState) -> Dict[str, Any]:
    messages = state.messages
    last_message = messages[-1].content if messages else ""

    if state.current_step == "ask_pin":
        if "pin" in last_message.lower():
            pin = last_message.split('"')[1] if '"' in last_message else last_message.split()[-1]
            is_valid = validate_pin(pin)
            if is_valid:
                new_message = AIMessage(
                    content=f"Thank you, your PIN {pin} has been validated. Let me check for available rooms.")
                state.pin = pin
                state.current_step = "check_rooms"
            else:
                new_message = AIMessage(content="I'm sorry, but the PIN you provided is not valid. Please try again.")
        else:
            new_message = AIMessage(content="Welcome to our hotel. Can you please provide your PIN for check-in?")

    elif state.current_step == "check_rooms":
        available_rooms = check_available_rooms()
        if available_rooms:
            room = available_rooms[0]
            state.room_number = room['number']
            state.access_key = create_access_key(room['number'])
            assign_room(state.pin, room['number'])
            new_message = AIMessage(
                content=f"Great news! I've assigned you to room {room['number']}. Your access key is {state.access_key}.")
            state.current_step = "charge_card"
        else:
            new_message = AIMessage(
                content="I apologize, but there are no available rooms at the moment. Please check back later.")
            state.current_step = "complete"

    elif state.current_step == "charge_card":
        charge_amount = 200.0  # Example amount
        charge_success = charge_credit_card(state.pin, charge_amount)
        if charge_success:
            state.charge_amount = charge_amount
            new_message = AIMessage(
                content=f"Your credit card has been successfully charged ${charge_amount:.2f} for your stay. Is there anything else I can help you with?")
            state.current_step = "complete"
        else:
            new_message = AIMessage(
                content="I apologize, but there was an issue charging your credit card. Please contact the front desk for assistance.")
            state.current_step = "complete"

    else:
        new_message = AIMessage(
            content="Is there anything else I can help you with? I hope you have a pleasant stay with us.")
        state.current_step = "complete"

    return {
        "messages": messages + [new_message],
        "current_step": state.current_step,
        "pin": state.pin,
        "room_number": state.room_number,
        "access_key": state.access_key if state.access_key is not None else "",
        "charge_amount": state.charge_amount
    }


workflow = StateGraph(state_schema=GraphState)

workflow.add_node('agent', run_step)

workflow.set_entry_point('agent')

workflow.add_conditional_edges(
    'agent',
    should_continue
)

hotel_checkin_agent = workflow.compile()