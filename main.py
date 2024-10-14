import os
import sys
import subprocess
import platform
import webbrowser
import pyttsx3
import psutil
import pyautogui
import speech_recognition as sr
import datetime
import time
import json
from vosk import Model, KaldiRecognizer
import ctypes
import shutil

# Initialize text-to-speech engine
def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# Use Vosk for offline speech recognition
def take_command():
    recognizer = sr.Recognizer()
    model_path = "path_to_your_vosk_model"  # Replace with the path to your Vosk model directory
    model = Model(model_path)  # Load the Vosk model
    
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    
    try:
        # Convert speech to text using Vosk offline model
        rec = KaldiRecognizer(model, 16000)
        rec.AcceptWaveform(audio.get_raw_data())
        result = rec.Result()
        result_json = json.loads(result)
        command = result_json.get("text", "").lower()
        
        print("You said:", command)
    except Exception as e:
        print("Sorry, I didn't catch that. Please say again.", e)
        command = None
    return command

# Open application by name
def open_application(application_name):
    try:
        if platform.system() == "Windows":
            os.startfile(application_name)
        elif platform.system() == "Darwin":  # macOS
            subprocess.Popen(["open", application_name])
        else:  # Linux
            subprocess.Popen(["xdg-open", application_name])
    except Exception as e:
        speak(f"Sorry, I couldn't open {application_name}")
        print(e)

# Control system volume
def control_volume(action):
    if platform.system() == "Windows":
        if "increase" in action:
            for _ in range(5):
                ctypes.windll.user32.keybd_event(0xAF, 0, 0, 0)  # Volume Up
        elif "decrease" in action:
            for _ in range(5):
                ctypes.windll.user32.keybd_event(0xAE, 0, 0, 0)  # Volume Down
        elif "mute" in action:
            ctypes.windll.user32.keybd_event(0xAD, 0, 0, 0)  # Mute

# Adjust system brightness (Windows only)
def control_brightness(level):
    try:
        if platform.system() == "Windows":
            level = max(0, min(100, level))  # Ensure brightness is between 0 and 100
            subprocess.run(f"powershell (Get-WmiObject -Namespace root/wmi -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{level})")
            speak(f"Brightness set to {level} percent")
        else:
            speak("Brightness control is not supported on this system.")
    except Exception as e:
        speak("Failed to adjust brightness.")
        print(e)

# Get CPU and RAM usage
def get_system_status():
    cpu_usage = psutil.cpu_percent(interval=1)
    ram_usage = psutil.virtual_memory().percent
    speak(f"CPU usage is at {cpu_usage} percent and RAM usage is at {ram_usage} percent.")

# Open specific file or folder
def open_file(file_path):
    try:
        os.startfile(file_path)
        speak(f"Opening {file_path}")
    except Exception as e:
        speak(f"Could not open {file_path}")
        print(e)

# Create a folder
def create_folder(folder_path):
    try:
        os.makedirs(folder_path, exist_ok=True)
        speak(f"Folder created at {folder_path}")
    except Exception as e:
        speak(f"Could not create folder at {folder_path}")
        print(e)

# Get battery status
def get_battery_status():
    battery = psutil.sensors_battery()
    if battery is not None:
        plugged = battery.power_plugged
        percent = str(battery.percent)
        if plugged:
            plugged_status = "Plugged In"
        else:
            plugged_status = "Not Plugged In"
        speak(f"Battery is {percent} percent charged and {plugged_status}")
    else:
        speak("Could not retrieve battery information.")

# Get current time
def get_time():
    now = datetime.datetime.now()
    current_time = now.strftime("%I:%M %p")
    speak(f"The current time is {current_time}")

# Open a website
def open_website(url):
    webbrowser.open(url)

# Take a screenshot
def take_screenshot():
    screenshot = pyautogui.screenshot()
    screenshot.save("screenshot.png")
    speak("Screenshot taken and saved as screenshot.png")

# Main logic
def main():
    speak("Hello! How can I assist you?")
    while True:
        command = take_command()
        if command:
            if "open" in command and "file" in command:
                file_path = command.split(" ", 2)[2]
                open_file(file_path)
            elif "create folder" in command:
                folder_path = command.split(" ", 2)[2]
                create_folder(folder_path)
            elif "open" in command:
                application_name = command.split(" ", 1)[1]
                open_application(application_name)
            elif "volume" in command:
                control_volume(command)
            elif "brightness" in command:
                level = int(command.split(" ", 1)[1])
                control_brightness(level)
            elif "battery" in command:
                get_battery_status()
            elif "time" in command:
                get_time()
            elif "website" in command:
                url = command.split(" ", 1)[1]
                open_website(url)
            elif "screenshot" in command:
                take_screenshot()
            elif "system status" in command:
                get_system_status()
            elif "exit" in command:
                speak("Goodbye!")
                sys.exit()
            else:
                speak("Sorry, I didn't understand that command.")

if __name__ == "__main__":
    main()
