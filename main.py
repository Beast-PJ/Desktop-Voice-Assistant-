import os
import sys
import webbrowser
import pyttsx3
import psutil
import pyautogui
import speech_recognition as sr
import datetime
import time
import requests
import random
import json

def speak(text):
    engine = pyttsx3.init()
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
        print("You said:", command)
    except Exception as e:
        print("Sorry, I didn't catch that. Please say again.", e)
        command = None
    return command

def open_application(application_name):
    try:
        os.startfile(application_name)
    except Exception as e:
        speak(f"Unable to open {application_name}.")
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
    try:
        webbrowser.open(url)
        speak(f"Opening {url}")
    except Exception as e:
        speak(f"Unable to open {url}")
        print(e)

def take_screenshot():
    try:
        screenshot = pyautogui.screenshot()
        screenshot_filename = f"screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        screenshot.save(screenshot_filename)
        speak(f"Screenshot taken and saved as {screenshot_filename}")
    except Exception as e:
        speak("Unable to take screenshot.")
        print(e)

def get_weather(city):
    try:
        api_key = "your_openweathermap_api_key"  # You need to sign up at openweathermap.org and get an API key
        base_url = "http://api.openweathermap.org/data/2.5/weather?"
        complete_url = base_url + "q=" + city + "&appid=" + api_key
        response = requests.get(complete_url)
        data = response.json()
        if data["cod"] != "404":
            main = data["main"]
            weather_description = data["weather"][0]["description"]
            temperature = main["temp"] - 273.15  # Convert from Kelvin to Celsius
            speak(f"The temperature in {city} is {temperature:.2f} degrees Celsius with {weather_description}")
        else:
            speak(f"City {city} not found.")
    except Exception as e:
        speak("Unable to fetch weather information.")
        print(e)

def get_system_info():
    try:
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_info = psutil.virtual_memory()
        speak(f"CPU usage is at {cpu_usage} percent. Memory usage is at {memory_info.percent} percent.")
    except Exception as e:
        speak("Unable to fetch system information.")
        print(e)

def play_music(music_dir):
    try:
        songs = os.listdir(music_dir)
        song = random.choice(songs)
        os.startfile(os.path.join(music_dir, song))
        speak(f"Playing {song}")
    except Exception as e:
        speak("Unable to play music.")
        print(e)

def set_reminder(reminder_text, reminder_time):
    try:
        reminder_time = datetime.datetime.strptime(reminder_time, "%H:%M")
        current_time = datetime.datetime.now().time()
        delta = datetime.datetime.combine(datetime.date.today(), reminder_time) - datetime.datetime.combine(datetime.date.today(), current_time)
        time.sleep(delta.seconds)
        speak(f"Reminder: {reminder_text}")
    except Exception as e:
        speak("Unable to set reminder.")
        print(e)

def tell_joke():
    try:
        response = requests.get("https://official-joke-api.appspot.com/random_joke")
        joke = response.json()
        speak(joke["setup"])
        time.sleep(2)
        speak(joke["punchline"])
    except Exception as e:
        speak("Unable to fetch a joke.")
        print(e)

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
            elif "weather" in command:
                city = command.split(" ", 1)[1]
                get_weather(city)
            elif "system" in command:
                get_system_info()
            elif "music" in command:
                music_dir = "path_to_your_music_directory"  # Specify your music directory here
                play_music(music_dir)
            elif "reminder" in command:
                reminder_text, reminder_time = command.split(" ", 2)[1:]
                set_reminder(reminder_text, reminder_time)
            elif "joke" in command:
                tell_joke()
            elif "exit" in command:
                speak("Goodbye!")
                sys.exit()
            else:
                speak("Sorry, I didn't understand that command.")

if __name__ == "__main__":
    main()
