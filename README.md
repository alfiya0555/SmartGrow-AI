# 🌱 SmartGrow AI

**AI & IoT-Based Plant Monitoring and Care Assistant**

SmartGrow AI is an IoT-based plant monitoring system that helps users monitor plant conditions and receive plant-care information through a Telegram chatbot.

The system collects environmental data from sensors connected to an ESP32 and sends the data to a Flask-based backend. Users can interact with the Telegram bot to check the plant's current status, receive watering information, and view previous sensor readings.

---

## 🚀 Features

- 🌱 Real-time plant condition monitoring
- 💧 Soil moisture monitoring
- 🌡️ Temperature and humidity monitoring
- 💡 Light intensity monitoring
- 🤖 Telegram chatbot for plant-care interaction
- 📊 Sensor data storage using SQLite
- 📜 View previous sensor readings
- 💻 Sensor data simulation for testing without hardware

---

## 🛠️ Technologies Used

**Programming:** Python

**Backend:** Flask

**Database:** SQLite, SQLAlchemy

**Hardware:** ESP32, Capacitive Soil Moisture Sensor, BH1750 Light Sensor

**Communication:** Telegram Bot API

**Tools:** Arduino IDE, Postman, Git & GitHub

---

## 🏗️ System Architecture

```text
        🌱 Plant
           │
           ▼
     IoT Sensors
           │
           ▼
        ESP32
           │
           ▼
     Flask Backend
           │
      ┌────┴────┐
      ▼         ▼
   SQLite    Telegram
   Database     Bot
                  │
                  ▼
               👤 User
```

---

## 💬 Telegram Bot Commands

The chatbot supports commands such as:

| Command | Function |
|---|---|
| `hi` | Start interaction with the bot |
| `status` | Check the current plant condition |
| `water` | Get watering-related information |
| `history` | View previous sensor readings |

---

## 📂 Project Structure

```text
SmartGrow-AI/
│
├── app.py
├── simulate_sensor.py
├── smartgrow_memory.db
├── plants_data.json
├── requirements.txt
└── README.md
```

---

## ⚙️ How It Works

1. Sensors collect information about the plant's environment.
2. The ESP32 processes and sends the sensor data to the Flask backend.
3. The Flask server receives and processes the data.
4. Sensor readings are stored in the SQLite database.
5. The Telegram chatbot allows users to interact with the system.
6. Users can request plant status, watering information, and historical readings.

---
## 📸 Project Demo

### 🤖 Telegram Bot Interaction

The Telegram chatbot allows users to monitor their plants and request plant-care information through simple commands.

![Telegram Bot Interaction](telegram-bot-interaction.png)

### 💧 Soil Moisture Alert

The system can identify low soil-moisture conditions and provide an alert to the user through the Telegram chatbot.

![Soil Moisture Alert](soil-moisture-alert.png)

---
## 🧪 Testing Without Hardware

SmartGrow AI includes a sensor simulation script that can generate sample sensor readings.

This allows the backend and chatbot functionality to be tested without connecting the physical ESP32 and sensors.

---

## 🎯 Objective

The main objective of SmartGrow AI is to combine IoT monitoring and intelligent plant-care assistance into a simple system that helps users understand plant conditions and make informed watering and maintenance decisions.

---

## 🔮 Future Enhancements

- 📱 Mobile application
- 🧠 More advanced AI-based plant recommendations
- 🌦️ Weather-based plant-care suggestions
- 📈 Sensor data visualization
- 🔔 Automated watering alerts
- 🌿 Support for multiple plant species

---

## 👩‍💻 Project

**SmartGrow AI**

Developed as an academic AI & IoT project.

**Technologies:** Python • Flask • SQLite • ESP32 • Telegram Bot API • IoT

---

⭐ Thanks for visiting the project!
