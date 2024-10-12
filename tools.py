from fastapi import FastAPI, HTTPException
import json
import random

app = FastAPI()

def load_json(file_name):
    with open(file_name, 'r') as f:
        return json.load(f)

def save_json(file_name, data):
    with open(file_name, 'w') as f:
        json.dump(data, f, indent=2)

@app.post("/validate_pin")
def validate_pin(pin: str):
    users = load_json('users.json')
    for user in users:
        if user['pin'] == pin:
            return {"valid": True, "user_id": user['id']}
    return {"valid": False}

def check_available_rooms():
    rooms = load_json('rooms.json')
    available_rooms = [room for room in rooms if room['status'] == 'available']
    return available_rooms  # This will be an empty list if no rooms are available

@app.post("/assign_room")
def assign_room(user_id: int, room_number: str):
    rooms = load_json('rooms.json')
    for room in rooms:
        if room['number'] == room_number and room['status'] == 'available':
            room['status'] = 'occupied'
            room['user_id'] = user_id
            save_json('rooms.json', rooms)
            return {"success": True, "room_number": room_number}
    raise HTTPException(status_code=400, detail="Room not available")

def create_access_key(room_number: str) -> str:
    access_key = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=6))
    return access_key

@app.post("/charge_credit_card")
def charge_credit_card(user_id: int, amount: float):
    # Simulate credit card charge
    return {"success": True, "amount": amount}