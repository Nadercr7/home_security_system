# 🚨 Smart Home Guardian

**Smart Home Guardian** is a Python-based home security system simulator with a modern GUI that allows users to monitor and control virtual motion sensors throughout a simulated home environment.

---

## 🧠 Overview

Smart Home Guardian provides a virtual and interactive environment for testing home security concepts. It is built with **Python**, **CustomTkinter**, and **SQLite**, and simulates motion detection, real-time alerts, persistent event logging, and a visual floor plan of a home.

Whether you're a developer, student, or enthusiast, this project helps you learn and experiment with smart security systems — **without needing physical hardware**.

---

## 🔑 Features

- 🕵️ **Motion Detection Simulation** – Virtual sensors that detect and report motion.
- 🔐 **Security System Control** – Arm/disarm the system with status indicators.
- 📜 **Event Logging** – Automatically logs all events using an SQLite database.
- 🏠 **Visual Floor Plan** – Interactive layout showing sensor locations and statuses.
- 🚨 **Real-Time Alerts** – Visual feedback when security events are triggered.
- ⚙️ **Threat Response Logic** – Different behaviors depending on system state (armed/disarmed).

---

## 📦 Requirements

- Python 3.6+
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
- [Pillow (PIL)](https://python-pillow.org/)
- SQLite3 (comes pre-installed with Python)

---

## 🚀 Installation

1. **Clone the repository** or download the ZIP:

```bash
git clone https://github.com/Nadercr7/home_security_system.git
cd smart-home-guardian
````

2. **Install required dependencies**:

```bash
pip install customtkinter pillow
```

3. **Run the application**:

```bash
python home_security.py
```

---

## 🖥️ Usage

### 🎛️ Interface Overview

* **Left Panel**: System controls (arm/disarm), sensor triggers, and a live home layout.
* **Right Panel**: Real-time event log and alert notifications.

### 🧭 Controls

* **ARM/DISARM** – Toggle system state.
* **Trigger Sensor** – Simulate motion detection manually.
* **Refresh Events** – View the most recent security logs.

### 🔒 Security System States

* **DISARMED**: Events are logged only.
* **ARMED**: Events trigger alerts and are logged.

---

## 🧱 System Architecture

Smart Home Guardian uses object-oriented design with key software design patterns:

* 🧩 **Observer Pattern** – Sensors notify the SecurityAgent when events occur.
* 🧠 **Strategy Pattern** – Different responses depending on the system state.
* 🏗️ **Factory Pattern** – Easily add new sensor types.

### ⚙️ Core Components

| Component        | Description                                        |
| ---------------- | -------------------------------------------------- |
| `Sensor`         | Abstract class for all sensors                     |
| `MotionSensor`   | Simulated motion detection sensor                  |
| `SecurityAgent`  | Observes sensors and manages threat response logic |
| `AlertSystem`    | Displays alerts based on detected events           |
| `EventLogger`    | Logs all events to a persistent SQLite database    |
| `SecuritySystem` | Coordinates the entire system                      |
| `GUI`            | Interactive interface built with CustomTkinter     |

---

## 🗃️ Database Schema

SQLite is used to store event logs:

```sql
CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    event_type TEXT,
    description TEXT
);
```

---

## 🔧 Extending the System

### ➕ Add New Sensor Types

```python
class NewSensorType(Sensor):
    def __init__(self, name, location, params):
        super().__init__(name, location)
        # Additional initialization
    
    def start_monitoring(self):
        # Custom monitoring behavior
        pass
```

### 🧠 Add New Response Strategies

Modify the `SecurityAgent.update()` method to introduce new behaviors for different event types or system modes.

---

## 👤 Author

**Nader Mohamed**
Faculty of Artificial Intelligence, Kafr Elsheikh University
📧 [naderelakany@gmail.com](mailto:naderelakany@gmail.com)

---

## 🙏 Acknowledgments

* [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) – for modern UI widgets
* The Python community – for excellent open-source libraries and inspiration

---

## 📸 Screenshots
![Screenshot 2025-05-03 031553](https://github.com/user-attachments/assets/01b24ef7-508e-4a11-b29f-0b6f2c94ac25)


