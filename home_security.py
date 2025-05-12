import random
import time
import sqlite3
import datetime
import threading
from abc import ABC, abstractmethod
import customtkinter as ctk
from PIL import Image, ImageTk
import os

# Set appearance mode and default color theme
ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

# Database setup
def setup_database():
    conn = sqlite3.connect('security_system.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        event_type TEXT,
        description TEXT
    )
    ''')
    conn.commit()
    conn.close()
    print("Database initialized.")

# Event Logger
class EventLogger:
    def __init__(self):
        self.db_lock = threading.Lock()
    
    def log_event(self, event_type, description):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Use a lock to prevent concurrent database access
        with self.db_lock:
            # Create a new connection and cursor for each operation
            conn = sqlite3.connect('security_system.db')
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO events (timestamp, event_type, description) VALUES (?, ?, ?)",
                (timestamp, event_type, description)
            )
            conn.commit()
            conn.close()
        
        print(f"[LOG] {timestamp} - {event_type}: {description}")
        return timestamp
    
    def get_recent_events(self, limit=20):
        with self.db_lock:
            conn = sqlite3.connect('security_system.db')
            cursor = conn.cursor()
            cursor.execute(
                "SELECT timestamp, event_type, description FROM events ORDER BY timestamp DESC LIMIT ?",
                (limit,)
            )
            events = cursor.fetchall()
            conn.close()
        return events

# Abstract Sensor class
class Sensor(ABC):
    def __init__(self, name, location):
        self.name = name
        self.location = location
        self.observers = []
    
    def add_observer(self, observer):
        self.observers.append(observer)
    
    def notify_observers(self, event_data):
        for observer in self.observers:
            observer.update(event_data)
    
    @abstractmethod
    def start_monitoring(self):
        pass

# Motion Sensor implementation
class MotionSensor(Sensor):
    def __init__(self, name, location, detection_probability=0.3):
        super().__init__(name, location)
        self.detection_probability = detection_probability
        self.is_active = True
        self.monitoring_thread = None
    
    def detect_motion(self):
        if random.random() < self.detection_probability:
            event_data = {
                "sensor_type": "motion",
                "sensor_name": self.name,
                "location": self.location,
                "timestamp": datetime.datetime.now(),
                "detected": True
            }
            self.notify_observers(event_data)
            return True
        return False
    
    def start_monitoring(self):
        self.is_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
    
    def stop_monitoring(self):
        self.is_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=1.0)
    
    def _monitoring_loop(self):
        while self.is_active:
            self.detect_motion()
            # Sleep for a random time between 3-10 seconds
            time.sleep(random.uniform(3, 10))

    def simulate_motion_detection(self):
        """Manually trigger a motion detection event"""
        event_data = {
            "sensor_type": "motion",
            "sensor_name": self.name,
            "location": self.location,
            "timestamp": datetime.datetime.now(),
            "detected": True
        }
        self.notify_observers(event_data)
        return True

# Intelligent Agent - Observer for sensors
class SecurityAgent:
    def __init__(self, name, event_logger):
        self.name = name
        self.armed = False
        self.logger = event_logger
        self.alert_system = None
        self.callback = None
    
    def arm(self):
        self.armed = True
        timestamp = self.logger.log_event("SYSTEM", f"Security system ARMED by agent {self.name}")
        return timestamp
    
    def disarm(self):
        self.armed = False
        timestamp = self.logger.log_event("SYSTEM", f"Security system DISARMED by agent {self.name}")
        return timestamp
    
    def set_alert_system(self, alert_system):
        self.alert_system = alert_system
    
    def set_update_callback(self, callback):
        self.callback = callback
    
    def update(self, event_data):
        # Process sensor data and make decisions
        if event_data["sensor_type"] == "motion" and event_data["detected"]:
            location = event_data["location"]
            timestamp = self.logger.log_event(
                "MOTION", 
                f"Motion detected at {location} by {event_data['sensor_name']}"
            )
            
            if self.armed:
                # Trigger alert if system is armed
                if self.alert_system:
                    self.alert_system.trigger_alert(
                        f"Motion detected at {location} by {event_data['sensor_name']}"
                    )
                
                if self.callback:
                    # Use a function to avoid direct GUI updates from non-main thread
                    self.callback("alert", location, timestamp)
            else:
                if self.callback:
                    # Use a function to avoid direct GUI updates from non-main thread
                    self.callback("motion", location, timestamp)

# Alert System
class AlertSystem:
    def __init__(self, system_name, event_logger):
        self.system_name = system_name
        self.logger = event_logger
        self.callback = None
    
    def set_alert_callback(self, callback):
        self.callback = callback
    
    def trigger_alert(self, alert_message):
        # Log the alert
        timestamp = self.logger.log_event("ALERT", f"Alert triggered: {alert_message}")
        
        if self.callback:
            self.callback(alert_message, timestamp)

class SecuritySystem:
    def __init__(self, system_name="HomeSecurity"):
        self.system_name = system_name
        setup_database()
        self.event_logger = EventLogger()
        self.sensors = []
        self.agent = SecurityAgent("MainAgent", self.event_logger)
        self.alert_system = AlertSystem(system_name, self.event_logger)
        self.agent.set_alert_system(self.alert_system)
        self.system_state = "INACTIVE"
        
    def add_sensor(self, sensor):
        self.sensors.append(sensor)
        sensor.add_observer(self.agent)
        self.event_logger.log_event("SYSTEM", f"Added {sensor.name} sensor at {sensor.location}")
    
    def arm_system(self):
        timestamp = self.agent.arm()
        self.system_state = "ARMED"
        return timestamp
        
    def disarm_system(self):
        timestamp = self.agent.disarm()
        self.system_state = "DISARMED"
        return timestamp
    
    def set_agent_callback(self, callback):
        self.agent.set_update_callback(callback)
    
    def set_alert_callback(self, callback):
        self.alert_system.set_alert_callback(callback)
    
    def start(self):
        print(f"\n🔒 Starting {self.system_name} security system...")
        self.system_state = "ACTIVE"
        for sensor in self.sensors:
            sensor.start_monitoring()
            print(f"  - {sensor.name} at {sensor.location} is active")
    
    def stop(self):
        print(f"\n🛑 Stopping {self.system_name} security system...")
        self.system_state = "INACTIVE"
        for sensor in self.sensors:
            sensor.stop_monitoring()
        print("System shutdown complete.")
    
    def get_recent_events(self, limit=20):
        return self.event_logger.get_recent_events(limit)
    
    def simulate_motion(self, sensor_index=0):
        """Manually trigger motion on a specific sensor"""
        if 0 <= sensor_index < len(self.sensors):
            if isinstance(self.sensors[sensor_index], MotionSensor):
                self.sensors[sensor_index].simulate_motion_detection()
                return True
        return False

# GUI Application
class SecuritySystemApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("Smart Home Guardian Security System")
        self.geometry("1000x600")
        self.resizable(True, True)
        
        # Initialize security system
        self.security_system = SecuritySystem("Smart Home Guardian")
        self.security_system.add_sensor(MotionSensor("Front Door Sensor", "Front Door"))
        self.security_system.add_sensor(MotionSensor("Living Room Sensor", "Living Room"))
        self.security_system.add_sensor(MotionSensor("Back Door Sensor", "Back Door"))
        self.security_system.add_sensor(MotionSensor("Garage Sensor", "Garage"))
        
        # Set callbacks
        self.security_system.set_agent_callback(self.handle_sensor_update)
        self.security_system.set_alert_callback(self.handle_alert)
        
        # Create GUI elements
        self.create_widgets()
        
        # Start security system
        self.security_system.start()
        
        # Update events initially
        self.update_event_list()
        
    def create_widgets(self):
        # Create main frame with two columns
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Left frame - System controls and sensor status
        self.left_frame = ctk.CTkFrame(self)
        self.left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.configure_left_frame()
        
        # Right frame - Event log and notifications
        self.right_frame = ctk.CTkFrame(self)
        self.right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.configure_right_frame()
    
    def configure_left_frame(self):
        self.left_frame.grid_columnconfigure(0, weight=1)
        
        # System title
        title_label = ctk.CTkLabel(
            self.left_frame, 
            text="Smart Home Guardian", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        # System status
        status_frame = ctk.CTkFrame(self.left_frame)
        status_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        status_frame.grid_columnconfigure(1, weight=1)
        
        status_label = ctk.CTkLabel(status_frame, text="System Status:", font=ctk.CTkFont(size=16))
        status_label.grid(row=0, column=0, padx=10, pady=10)
        
        self.status_value = ctk.CTkLabel(
            status_frame, 
            text="DISARMED", 
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="orange"
        )
        self.status_value.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        # Arm/Disarm button
        self.arm_button = ctk.CTkButton(
            self.left_frame,
            text="ARM SYSTEM",
            font=ctk.CTkFont(size=16),
            fg_color="green",
            command=self.toggle_system_arm
        )
        self.arm_button.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        
        # Sensor status section
        sensor_frame = ctk.CTkFrame(self.left_frame)
        sensor_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        sensor_frame.grid_columnconfigure(0, weight=1)
        
        sensor_title = ctk.CTkLabel(
            sensor_frame, 
            text="Sensor Controls", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        sensor_title.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        # Sensor trigger buttons
        self.sensor_buttons = []
        sensors = [
            ("Front Door", 0), 
            ("Living Room", 1), 
            ("Back Door", 2),
            ("Garage", 3)
        ]
        
        for i, (location, idx) in enumerate(sensors):
            sensor_btn = ctk.CTkButton(
                sensor_frame,
                text=f"Trigger {location} Sensor",
                command=lambda idx=idx: self.trigger_sensor(idx)
            )
            sensor_btn.grid(row=i+1, column=0, padx=10, pady=5, sticky="ew")
            self.sensor_buttons.append(sensor_btn)
        
        # Floor plan visualization (simplified)
        floorplan_frame = ctk.CTkFrame(self.left_frame)
        floorplan_frame.grid(row=4, column=0, padx=20, pady=20, sticky="ew")
        
        floorplan_title = ctk.CTkLabel(
            floorplan_frame, 
            text="Home Layout", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        floorplan_title.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        # Simple floor plan drawing
        self.floorplan_canvas = ctk.CTkCanvas(floorplan_frame, width=400, height=200, bg="#f0f0f0")
        self.floorplan_canvas.grid(row=1, column=0, padx=10, pady=10)
        self.draw_floorplan()
    
    def configure_right_frame(self):
        self.right_frame.grid_columnconfigure(0, weight=1)
        self.right_frame.grid_rowconfigure(1, weight=1)
        
        # Event log header
        events_label = ctk.CTkLabel(
            self.right_frame, 
            text="Security Events", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        events_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        # Event log window (textbox)
        self.event_log = ctk.CTkTextbox(self.right_frame, width=400, height=400)
        self.event_log.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.event_log.configure(state="disabled")
        
        # Alert notification area
        self.alert_frame = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        self.alert_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        
        self.alert_label = ctk.CTkLabel(
            self.alert_frame,
            text="No active alerts",
            font=ctk.CTkFont(size=16),
        )
        self.alert_label.pack(pady=10)
        
        # Refresh button
        refresh_button = ctk.CTkButton(
            self.right_frame,
            text="Refresh Events",
            command=self.update_event_list
        )
        refresh_button.grid(row=3, column=0, padx=20, pady=20)
    
    def draw_floorplan(self):
        canvas = self.floorplan_canvas
        canvas.delete("all")
        
        # Draw house outline
        canvas.create_rectangle(50, 50, 350, 180, outline="black", width=2)
        
        # Draw rooms
        canvas.create_line(200, 50, 200, 180, fill="black", width=2)  # Middle divider
        canvas.create_line(50, 115, 200, 115, fill="black", width=2)  # Top room divider
        
        # Label rooms
        canvas.create_text(130, 85, text="Living Room")
        canvas.create_text(130, 145, text="Garage")
        canvas.create_text(275, 115, text="Bedroom")
        
        # Draw doors
        canvas.create_rectangle(180, 50, 220, 52, fill="brown", outline="")  # Front door
        canvas.create_rectangle(48, 130, 50, 150, fill="brown", outline="")  # Garage door
        canvas.create_rectangle(348, 130, 350, 150, fill="brown", outline="")  # Back door
        
        # Draw sensor locations with default state
        self.sensor_indicators = {
            "Front Door": canvas.create_oval(195, 40, 205, 50, fill="green"),
            "Living Room": canvas.create_oval(130, 70, 140, 80, fill="green"),
            "Back Door": canvas.create_oval(355, 140, 365, 150, fill="green"),
            "Garage": canvas.create_oval(90, 140, 100, 150, fill="green")
        }
    
    def update_sensor_indicator(self, location, state):
        """Update sensor indicators safely from any thread"""
        if hasattr(self, 'sensor_indicators') and location in self.sensor_indicators:
            color = "red" if state == "alert" else "yellow"
            # Use after method to ensure updates happen in the main thread
            self.after(0, lambda: self.floorplan_canvas.itemconfig(
                self.sensor_indicators[location], fill=color)
            )
            
            # Reset to green after 3 seconds
            self.after(3000, lambda: self.floorplan_canvas.itemconfig(
                self.sensor_indicators[location], fill="green")
            )
    
    def toggle_system_arm(self):
        if self.security_system.system_state == "ARMED":
            timestamp = self.security_system.disarm_system()
            self.status_value.configure(text="DISARMED", text_color="orange")
            self.arm_button.configure(text="ARM SYSTEM", fg_color="green")
        else:
            timestamp = self.security_system.arm_system()
            self.status_value.configure(text="ARMED", text_color="red")
            self.arm_button.configure(text="DISARM SYSTEM", fg_color="red")
        
        self.update_event_list()
    
    def trigger_sensor(self, sensor_index):
        self.security_system.simulate_motion(sensor_index)
    
    def handle_sensor_update(self, event_type, location, timestamp):
        """Safe handler for sensor updates that may come from other threads"""
        # Schedule GUI updates to run in the main thread
        self.after(0, lambda: self.update_sensor_indicator(location, event_type))
        self.after(0, self.update_event_list)
        
        if event_type == "alert":
            self.after(0, lambda: self.show_alert(f"INTRUDER DETECTED at {location}! - {timestamp}"))
    
    def handle_alert(self, message, timestamp):
        """Safe handler for alerts that may come from other threads"""
        # Schedule GUI updates to run in the main thread
        self.after(0, lambda: self.show_alert(f"SECURITY ALERT: {message} - {timestamp}"))
        self.after(0, self.update_event_list)
    
    def show_alert(self, message):
        self.alert_label.configure(
            text=message,
            text_color="red",
            fg_color="#ffdddd",
            corner_radius=10
        )
        self.alert_frame.configure(fg_color="#ffdddd")
        
        # Reset after 10 seconds
        self.after(10000, self.reset_alert_display)
    
    def reset_alert_display(self):
        self.alert_label.configure(
            text="No active alerts",
            text_color=("gray10", "gray90"),
            fg_color="transparent"
        )
        self.alert_frame.configure(fg_color="transparent")
    
    def update_event_list(self):
        # Get events from database
        events = self.security_system.get_recent_events()
        
        # Clear current text
        self.event_log.configure(state="normal")
        self.event_log.delete("1.0", "end")
        
        # Insert events
        for timestamp, event_type, description in events:
            if event_type == "ALERT":
                self.event_log.insert("end", f"{timestamp} - ", "timestamp")
                self.event_log.insert("end", f"{event_type}: ", "alert")
                self.event_log.insert("end", f"{description}\n", "alert_desc")
            elif event_type == "MOTION":
                self.event_log.insert("end", f"{timestamp} - ", "timestamp")
                self.event_log.insert("end", f"{event_type}: ", "motion")
                self.event_log.insert("end", f"{description}\n", "motion_desc")
            else:
                self.event_log.insert("end", f"{timestamp} - {event_type}: {description}\n", "normal")
        
        # Configure tags - FIXED: CustomTkinter doesn't allow font in tag_config
        self.event_log.tag_config("timestamp", foreground="#555555")
        self.event_log.tag_config("alert", foreground="red")  # Removed font parameter
        self.event_log.tag_config("alert_desc", foreground="red")
        self.event_log.tag_config("motion", foreground="blue")  # Removed font parameter
        self.event_log.tag_config("motion_desc", foreground="blue")
        
        self.event_log.configure(state="disabled")
    
    def on_closing(self):
        self.security_system.stop()
        self.destroy()

if __name__ == "__main__":
    app = SecuritySystemApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()