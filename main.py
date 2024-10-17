import os
import sys
import subprocess
import webbrowser
import pyttsx3
import psutil
import pyautogui
import speech_recognition as sr
import datetime
import time
import requests
from fuzzywuzzy import fuzz
import platform
import smtplib

# Initialize speech engine
engine = pyttsx3.init()

# Flexible command list with synonyms
command_list = {
    'open_application': ['open', 'start', 'launch'],
    'battery_status': ['battery', 'power', 'charge level'],
    'time': ['time', 'current time', 'what time is it'],
    'weather': ['weather', 'temperature', 'forecast'],
    'set_reminder': ['reminder', 'alert', 'notify'],
    'screenshot': ['screenshot', 'capture screen'],
    'volume_up': ['increase volume', 'turn up the sound', 'louder'],
    'volume_down': ['decrease volume', 'turn down the sound', 'quieter'],
    'mute': ['mute', 'silence'],
    'unmute': ['unmute', 'unsilence'],
    'play_music': ['play music', 'start music', 'play a song'],
    'send_email': ['send email', 'write email', 'mail'],
    'search_google': ['search', 'google'],
    'exit': ['exit', 'quit', 'close']
}

def speak(text):
    engine.say(text)
    engine.runAndWait()

def take_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        print("Recognizing...")
        command = recognizer.recognize_google(audio).lower()
        print(f"You said: {command}")
        return command
    except Exception as e:
        print("Sorry, I didn't catch that.", e)
        return None

def match_command(input_command):
    for key, synonyms in command_list.items():
        for synonym in synonyms:
            if fuzz.ratio(input_command, synonym) > 70:
                return key
    return None

# New Features
def get_weather():
    api_key = "your_openweather_api_key"
    location = "your_location"
    weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}"
    try:
        response = requests.get(weather_url)
        data = response.json()
        if data["cod"] != "404":
            main = data["main"]
            temperature = main["temp"] - 273.15  # Convert to Celsius
            weather_description = data["weather"][0]["description"]
            speak(f"The temperature is {temperature:.2f} degrees Celsius with {weather_description}")
        else:
            speak("Could not retrieve weather information.")
    except:
        speak("Failed to get weather data.")

def set_reminder(reminder_text):
    with open('reminders.txt', 'a') as file:
        file.write(f"{reminder_text} - {datetime.datetime.now()}\n")
    speak("Reminder saved successfully.")

def control_volume(action):
    if action == 'volume_up':
        os.system("nircmd.exe changesysvolume 2000")
        speak("Volume increased.")
    elif action == 'volume_down':
        os.system("nircmd.exe changesysvolume -2000")
        speak("Volume decreased.")
    elif action == 'mute':
        os.system("nircmd.exe mutesysvolume 1")
        speak("System muted.")
    elif action == 'unmute':
        os.system("nircmd.exe mutesysvolume 0")
        speak("System unmuted.")

def play_music():
    music_dir = "C:\\YourMusicDirectory"  # Specify your music directory
    songs = os.listdir(music_dir)
    os.startfile(os.path.join(music_dir, songs[0]))
    speak("Playing music.")

def send_email(subject, body, recipient):
    your_email = "your_email@gmail.com"
    your_password = "your_password"

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(your_email, your_password)
        message = f"Subject: {subject}\n\n{body}"
        server.sendmail(your_email, recipient, message)
        server.quit()
        speak("Email sent successfully.")
    except Exception as e:
        speak("Failed to send email.")
        print(e)

# Main Command Handler
def command_handler(command):
    command_key = match_command(command)
    if command_key:
        if command_key == 'open_application':
            application_name = command.split(" ", 1)[1]
            os.startfile(application_name)
        elif command_key == 'battery_status':
            battery = psutil.sensors_battery()
            if battery:
                plugged_status = "Plugged in" if battery.power_plugged else "Not plugged in"
                speak(f"Battery is {battery.percent}% and {plugged_status}")
            else:
                speak("Could not get battery information.")
        elif command_key == 'time':
            now = datetime.datetime.now()
            speak(f"The current time is {now.strftime('%I:%M %p')}")
        elif command_key == 'weather':
            get_weather()
        elif command_key == 'set_reminder':
            reminder_text = command.split(" ", 1)[1]
            set_reminder(reminder_text)
        elif command_key in ['volume_up', 'volume_down', 'mute', 'unmute']:
            control_volume(command_key)
        elif command_key == 'screenshot':
            screenshot = pyautogui.screenshot()
            screenshot.save("screenshot.png")
            speak("Screenshot taken.")
        elif command_key == 'play_music':
            play_music()
        elif command_key == 'send_email':
            # For demo purposes, hardcoded values, can enhance to capture input
            send_email("Test Subject", "Test Body", "recipient@example.com")
        elif command_key == 'search_google':
            search_query = command.split(" ", 1)[1]
            webbrowser.open(f"https://www.google.com/search?q={search_query}")
        elif command_key == 'exit':
            speak("Goodbye!")
            sys.exit()

# Main voice command loop
def take_command_real_time():
    speak("Hello! How can I assist you today?")
    while True:
        command = take_command()
        if command:
            command_handler(command)

# Start the voice command loop
take_command_real_time()
