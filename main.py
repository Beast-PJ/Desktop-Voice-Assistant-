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

def get_time():
    now = datetime.datetime.now()
    current_time = now.strftime("%I:%M %p")
    speak(f"The current time is {current_time}")

def open_website(url):
    webbrowser.open(url)

def take_screenshot():
    screenshot = pyautogui.screenshot()
    screenshot.save("screenshot.png")
    speak("Screenshot taken and saved as screenshot.png")

def main():
    speak("Hello! How can I assist you?")
    while True:
        command = take_command()
        if command:
            if "open" in command:
                application_name = command.split(" ", 1)[1]
                open_application(application_name)
            elif "battery" in command:
                get_battery_status()
            elif "time" in command:
                get_time()
            elif "website" in command:
                url = command.split(" ", 1)[1]
                open_website(url)
            elif "screenshot" in command:
                take_screenshot()
            elif "exit" in command:
                speak("Goodbye!")
                sys.exit()
            else:
                speak("Sorry, I didn't understand that command.")

if __name__ == "__main__":
    main()
