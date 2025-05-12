# Smart Home Guardian

A Python-based home security system simulator with GUI interface that allows you to monitor and control virtual sensors throughout your home.

## Overview

Smart Home Guardian is a simulated home security system built with Python and CustomTkinter. It provides a virtual environment for testing home security concepts, featuring motion sensors, event logging, alerts, and a visual representation of your home's security status.

## Features

- **Motion Detection Simulation**: Virtual sensors that can detect and report motion
- **Security System Control**: Arm/disarm system with status indicators
- **Event Logging**: Persistent record of all security events using SQLite
- **Visual Floor Plan**: Interactive home layout showing sensor locations and states
- **Real-time Alerts**: Visual notifications when security events occur
- **Threat Response**: Different behavior when armed vs. disarmed

## Requirements

- Python 3.6+
- CustomTkinter
- Pillow (PIL)
- SQLite3 (included with Python)

## Installation

1. Clone the repository or download the source code
2. Install the required packages:

```bash
pip install customtkinter pillow
```

3. Run the application:

```bash
python home_security.py
```

## Usage

### Main Interface

The application interface is divided into two main sections:

- **Left Side**: System controls, sensor triggers, and home layout visualization
- **Right Side**: Security event log and alert notifications

### Controls

- **ARM/DISARM System**: Toggle the security system between armed and disarmed states
- **Sensor Triggers**: Manually simulate motion detection at different locations
- **Refresh Events**: Update the event log with the latest security events

### Security System States

- **DISARMED**: Motion is detected and logged but no alerts are triggered
- **ARMED**: Motion detection triggers security alerts and visual notifications

## System Architecture

The Smart Home Guardian is built using object-oriented design principles and follows several design patterns:

- **Observer Pattern**: Sensors notify the security agent of events
- **Strategy Pattern**: Different security responses based on system state
- **Factory Pattern**: Creation of various sensor types

### Key Components

1. **Sensors**: Abstract base class with concrete implementations like MotionSensor
2. **SecurityAgent**: Processes sensor data and makes security decisions
3. **AlertSystem**: Handles the triggering and display of security alerts
4. **EventLogger**: Records all system events to a SQLite database
5. **SecuritySystem**: Coordinates all components and manages system state
6. **GUI Application**: User interface built with CustomTkinter

## Database Structure

Events are stored in an SQLite database with the following schema:

```sql
CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    event_type TEXT,
    description TEXT
)
```

## Extending the System

### Adding New Sensor Types

Create a new class that inherits from the `Sensor` base class:

```python
class NewSensorType(Sensor):
    def __init__(self, name, location, additional_params):
        super().__init__(name, location)
        # Additional initialization
        
    def start_monitoring(self):
        # Implement monitoring behavior
        pass
        
    # Additional methods
```

### Adding New Security Responses

Modify the `SecurityAgent.update()` method to handle new event types or implement new response strategies.

## License

[MIT License](LICENSE)

## Author

[Your Name]

## Acknowledgments

- CustomTkinter for the modern UI components
- Python community for the excellent libraries and tools
