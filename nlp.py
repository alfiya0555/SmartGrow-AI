import json
import re

with open("plants_data.json") as f:
    PLANT_DATA = json.load(f)

SYMPTOMS = {
    "yellow leaves": "Possible overwatering or nitrogen deficiency.",
    "brown spots": "Possible fungal infection or sunburn.",
    "drooping": "Likely underwatering or root stress.",
    "white powder": "Powdery mildew – reduce humidity.",
    "black spots": "Fungal disease – improve air circulation."
}

def detect_symptom(text):
    text = text.lower()
    for s in SYMPTOMS:
        if s in text:
            return s, SYMPTOMS[s]
    return None, None

def get_response(msg, plant, moisture, lux):
    msg = msg.lower()

    # --- Plant doctor ---
    symptom, advice = detect_symptom(msg)
    if symptom:
        return f"I detected **{symptom}**.\n\n{advice}\n\nLet me know the plant name for more specific advice."

    # --- Status command ---
    if "status" in msg:
        if plant == "none":
            return "No plant set. Use: set plant1 aloe vera"
        pdata = PLANT_DATA.get(plant, {})
        return (
            f"🌿 **{plant.capitalize()} Status**\n"
            f"Soil Moisture: {moisture}%\n"
            f"Light: {lux} lux\n"
            f"Watering range: {pdata['watering']['low']}–{pdata['watering']['high']}%\n"
            f"Light range: {pdata['light']['low']}–{pdata['light']['high']} lux"
        )

    # --- Care tips ---
    m = re.match(r"care (.*)", msg)
    if m:
        plant_name = m.group(1).strip()
        if plant_name in PLANT_DATA:
            return PLANT_DATA[plant_name]["care"]
        return "I don't have data for that plant."

    return "I'm here to help! You can ask:\n• set plant1 aloe vera\n• plant1 status\n• care rose\n• why are my leaves yellow?"
