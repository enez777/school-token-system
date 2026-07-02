import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_FILE = os.path.join(SCRIPT_DIR, "school_data.json")

def load_data():
    if not os.path.exists(JSON_FILE):
        return {}
    with open(JSON_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(JSON_FILE, "w") as f:
        json.dump(data, f, indent=4)

def add_points_to_student(student_id, amount):
    """Adds points to a student database and saves it."""
    data = load_data()
    if student_id in data["students"]:
        data["students"][student_id]["points"] += amount
        save_data(data)
        return True, data["students"][student_id]["points"], data["students"][student_id]["name"]
    return False, 0, ""

def process_redemption(student_id, reward_name):
    """Processes redemption logic and saves the state."""
    data = load_data()
    if student_id not in data["students"] or reward_name not in data["rewards"]:
        return False, "Invalid Student ID or Reward Name."
        
    student = data["students"][student_id]
    cost = data["rewards"][reward_name]
    
    if student["points"] >= cost:
        student["points"] -= cost
        save_data(data)
        return True, f"Success! {student['name']} redeemed {reward_name}. Remaining: {student['points']} pts"
    else:
        return False, f"Insufficient points. Needs {cost - student['points']} more points."

def register_new_student(student_id, name):
    """Adds a completely new student to the JSON file with 0 points."""
    data = load_data()
    if student_id in data["students"]:
        return False, "This Student ID already exists."
    
    # Create the new student entry
    data["students"][student_id] = {"name": name, "points": 0}
    save_data(data)
    return True, f"Successfully registered {name}!"
