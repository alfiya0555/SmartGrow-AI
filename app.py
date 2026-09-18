# app.py
import os
import time
import atexit
from datetime import datetime, timedelta
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
import requests

from models import db, SensorData, Alert

load_dotenv()

# ---------------- Settings (from .env or defaults) ----------------
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "").strip()
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID", "").strip()  # optional: override registered chat
SENSOR_API_KEY = os.getenv("SENSOR_API_KEY", "").strip()

MOISTURE_LOW_THRESHOLD = float(os.getenv("MOISTURE_THRESHOLD", "30"))    # low moisture threshold %
MOISTURE_HIGH_THRESHOLD = float(os.getenv("MOISTURE_HIGH_THRESHOLD", "80"))  # too-wet threshold %
LIGHT_LOW_THRESHOLD = float(os.getenv("LIGHT_LOW_THRESHOLD", "10"))      # lux low
LIGHT_HIGH_THRESHOLD = float(os.getenv("LIGHT_HIGH_THRESHOLD", "5000"))  # lux high
ALERT_COOLDOWN_MINUTES = int(os.getenv("ALERT_COOLDOWN_MINUTES", "30"))

# ---------------- Flask + DB ----------------
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///smartgrow_memory.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

print("USING DB FILE:", os.path.abspath("smartgrow_memory.db"))

with app.app_context():
    db.create_all()

latest_moisture = None
latest_lux = None

# ---------------- Chat ID helpers ----------------
if "__file__" in globals():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
else:
    BASE_DIR = os.getcwd()
CHAT_ID_FILE = os.path.join(BASE_DIR, "chat_id.txt")


def read_registered_chat_id():
    if os.path.exists(CHAT_ID_FILE):
        try:
            with open(CHAT_ID_FILE, "r") as f:
                v = f.read().strip()
                return v if v else None
        except Exception as e:
            print("Failed to read chat id file:", e)
    return None


def write_registered_chat_id(chat_id):
    try:
        with open(CHAT_ID_FILE, "w") as f:
            f.write(str(chat_id))
    except Exception as e:
        print("Failed to write chat id file:", e)


# ---------------- Telegram sender (HTTP requests) ----------------
def send_telegram_message(text):
    """Send a Telegram message synchronously via Bot API. Returns True on success."""
    if not TELEGRAM_TOKEN:
        print("❌ TELEGRAM_TOKEN not set")
        return False

    chat_id = ADMIN_CHAT_ID or read_registered_chat_id()
    if not chat_id:
        print("❌ No chat id available to send Telegram message")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        r = requests.post(url, json=payload, timeout=6)
        if r.status_code == 200:
            print("✔ Telegram message sent")
            return True
        else:
            print("❌ Telegram send failed:", r.status_code, r.text)
            return False
    except Exception as e:
        print("❌ Telegram request error:", e)
        return False


# ---------------- Alerts helpers ----------------
def last_alert_time(alert_type):
    try:
        a = Alert.query.filter_by(alert_type=alert_type).order_by(Alert.time.desc()).first()
        return a.time if a else None
    except Exception as e:
        print("DB error reading last alert:", e)
        return None


def record_alert(alert_type, value, sent_via="telegram"):
    try:
        a = Alert(alert_type=alert_type, value=value, sent_via=sent_via)
        db.session.add(a)
        db.session.commit()
    except Exception as e:
        print("Failed to record alert to DB:", e)
        try:
            db.session.rollback()
        except:
            pass


def trigger_alert_if_allowed(alert_type, value, message):
    last = last_alert_time(alert_type)
    now = datetime.now()
    if last and (now - last) < timedelta(minutes=ALERT_COOLDOWN_MINUTES):
        print(f"⏳ Cooldown for {alert_type} active - skipping alert.")
        return
    if send_telegram_message(message):
        record_alert(alert_type, value, sent_via="telegram")


# ---------------- Routes ----------------
@app.route("/")
def home():
    return "🌿 SmartGrow System Running (moisture + light only)"


@app.route("/sensor", methods=["POST"])
def sensor():
    global latest_moisture, latest_lux

    # Optional API key check
    if SENSOR_API_KEY:
        key = request.headers.get("X-API-KEY") or request.args.get("api_key")
        if key != SENSOR_API_KEY:
            return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json() or {}
    moisture = data.get("moisture")
    lux = data.get("lux")

    if moisture is None:
        return jsonify({"error": "Missing 'moisture' in JSON"}), 400
    if lux is None:
        return jsonify({"error": "Missing 'lux' in JSON"}), 400

    try:
        moisture = float(moisture)
        lux = float(lux)
    except Exception:
        return jsonify({"error": "moisture and lux must be numbers"}), 400

    latest_moisture = moisture
    latest_lux = lux

    # Save to DB
    try:
        entry = SensorData(moisture=moisture, lux=lux)
        db.session.add(entry)
        db.session.commit()
    except Exception as e:
        print("DB save failed:", e)
        try:
            db.session.rollback()
        except:
            pass

    # Alerts: moisture low
    if moisture < MOISTURE_LOW_THRESHOLD:
        trigger_alert_if_allowed(
            "low_moisture",
            moisture,
            f"⚠️ Soil moisture LOW ({moisture:.1f}%). Please water your plant."
        )

    # Alerts: moisture too high
    if moisture > MOISTURE_HIGH_THRESHOLD:
        trigger_alert_if_allowed(
            "high_moisture",
            moisture,
            f"💧 Soil moisture TOO HIGH ({moisture:.1f}%). Reduce watering to avoid root rot."
        )

    # Alerts: light low
    if lux < LIGHT_LOW_THRESHOLD:
        trigger_alert_if_allowed(
            "low_light",
            lux,
            f"🌑 Light too LOW ({lux:.1f} lux). Move plant to a brighter spot."
        )

    # Alerts: light high
    if lux > LIGHT_HIGH_THRESHOLD:
        trigger_alert_if_allowed(
            "high_light",
            lux,
            f"☀️ Light too HIGH ({lux:.1f} lux). Move plant out of direct sun."
        )

    return jsonify({"status": "ok", "moisture": moisture, "lux": lux})


@app.route("/get_latest", methods=["GET"])
def get_latest():
    return jsonify({"moisture": latest_moisture, "lux": latest_lux})


@app.route("/alerts", methods=["GET"])
def get_alerts():
    try:
        rows = Alert.query.order_by(Alert.time.desc()).limit(50).all()
        out = [{"time": r.time.strftime("%Y-%m-%d %H:%M:%S"), "type": r.alert_type, "value": r.value, "sent_via": r.sent_via} for r in rows]
        return jsonify(out)
    except Exception as e:
        print("Failed to fetch alerts:", e)
        return jsonify([])


# ---------------- Scheduled safety check ----------------
def scheduled_check():
    with app.app_context():
        print("Scheduled check running. Latest:", latest_moisture, latest_lux)
        if latest_moisture is not None:
            if latest_moisture < MOISTURE_LOW_THRESHOLD:
                trigger_alert_if_allowed(
                    "low_moisture",
                    latest_moisture,
                    f"⚠️ Soil moisture LOW ({latest_moisture:.1f}%). Please water your plant."
                )
            if latest_moisture > MOISTURE_HIGH_THRESHOLD:
                trigger_alert_if_allowed(
                    "high_moisture",
                    latest_moisture,
                    f"💧 Soil moisture TOO HIGH ({latest_moisture:.1f}%). Reduce watering."
                )
        if latest_lux is not None:
            if latest_lux < LIGHT_LOW_THRESHOLD:
                trigger_alert_if_allowed(
                    "low_light",
                    latest_lux,
                    f"🌑 Light too LOW ({latest_lux:.1f} lux)."
                )
            if latest_lux > LIGHT_HIGH_THRESHOLD:
                trigger_alert_if_allowed(
                    "high_light",
                    latest_lux,
                    f"☀️ Light too HIGH ({latest_lux:.1f} lux)."
                )


scheduler = BackgroundScheduler()
scheduler.add_job(scheduled_check, "interval", minutes=60)
scheduler.start()
atexit.register(lambda: scheduler.shutdown(wait=False))

# ---------------- Run ----------------
if __name__ == "__main__":
    print("🌿 SmartGrow Flask Server Starting (no temp sensor)...")
    app.run(host="0.0.0.0", port=5000, debug=True)


