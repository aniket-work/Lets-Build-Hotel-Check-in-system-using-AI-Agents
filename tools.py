from fastapi import FastAPI, HTTPException
import json
import random
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI()

def load_json(file_name):
    logger.info(f"Loading JSON from file: {file_name}")
    try:
        with open(file_name, 'r') as f:
            data = json.load(f)
        logger.debug(f"Successfully loaded JSON from {file_name}")
        return data
    except FileNotFoundError:
        logger.error(f"File not found: {file_name}")
        raise
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in file: {file_name}")
        raise

def save_json(file_name, data):
    logger.info(f"Saving JSON to file: {file_name}")
    try:
        with open(file_name, 'w') as f:
            json.dump(data, f, indent=2)
        logger.debug(f"Successfully saved JSON to {file_name}")
    except IOError:
        logger.error(f"Error writing to file: {file_name}")
        raise

@app.post("/validate_pin")
def validate_pin(pin: str):
    logger.info(f"Validating PIN: {pin}")
    users = load_json('users.json')
    for user in users:
        if user['pin'] == pin:
            logger.info(f"PIN {pin} is valid for user {user['id']}")
            return {"valid": True, "user_id": user['id']}
    logger.warning(f"Invalid PIN: {pin}")
    return {"valid": False}

def check_available_rooms():
    logger.info("Checking for available rooms")
    rooms = load_json('rooms.json')
    available_rooms = [room for room in rooms if room['status'] == 'available']
    logger.info(f"Found {len(available_rooms)} available rooms")
    return available_rooms

@app.post("/assign_room")
def assign_room(user_id: int, room_number: str):
    logger.info(f"Assigning room {room_number} to user {user_id}")
    rooms = load_json('rooms.json')
    for room in rooms:
        if room['number'] == room_number and room['status'] == 'available':
            room['status'] = 'occupied'
            room['user_id'] = user_id
            save_json('rooms.json', rooms)
            logger.info(f"Room {room_number} successfully assigned to user {user_id}")
            return {"success": True, "room_number": room_number}
    logger.error(f"Failed to assign room {room_number} to user {user_id}")
    raise HTTPException(status_code=400, detail="Room not available")

def create_access_key(room_number: str) -> str:
    logger.info(f"Creating access key for room {room_number}")
    access_key = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=6))
    logger.info(f"Access key created for room {room_number}: {access_key}")
    return access_key

@app.post("/charge_credit_card")
def charge_credit_card(user_id: int, amount: float):
    logger.info(f"Charging credit card for user {user_id}, amount: ${amount:.2f}")
    # Simulate credit card charge
    success = random.choice([True, False])  # Simulating success/failure
    if success:
        logger.info(f"Credit card charge successful for user {user_id}")
    else:
        logger.warning(f"Credit card charge failed for user {user_id}")
    return {"success": success, "amount": amount}

logger.info("Tools module initialized")