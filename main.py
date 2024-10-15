import os
import sys
import json
import webbrowser
import pyttsx3
import psutil
import pyautogui
import datetime
import pyaudio
from vosk import Model, KaldiRecognizer

# Initialize pyttsx3 for text-to-speech
def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# Function to listen and process speech in real-time
def take_command_real_time():
    model_path = "path/to/vosk-model"  # Replace with your Vosk model path
    if not os.path.exists(model_path):
        print(f"Model not found at {model_path}")
        return

    model = Model(model_path)
    recognizer = KaldiRecognizer(model, 16000)

    # Use PyAudio for real-time audio streaming
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
    stream.start_stream()

    print("Listening...")

    while True:
        data = stream.read(4000, exception_on_overflow=False)  # Read small chunks for real-time response
        if len(data) == 0:
            continue

        if recognizer.AcceptWaveform(data):  # Process each audio chunk
            result = recognizer.Result()
            result_json = json.loads(result)
            command = result_json.get('text', '').lower()
            if command:
                print(f"You said: {command}")
                execute_command(command)

# Function to execute various commands
def execute_command(command):
    if "open" in command:
        app_name = command.split("open", 1)[1].strip()
        open_application(app_name)

    elif "battery" in command:
        get_battery_status()

    elif "time" in command:
        get_time()

    elif "website" in command:
        url = command.split("website", 1)[1].strip()
        open_website(url)

    elif "screenshot" in command:
        take_screenshot()

    elif "volume up" in command:
        pyautogui.press("volumeup")
        speak("Increasing volume")

    elif "volume down" in command:
        pyautogui.press("volumedown")
        speak("Decreasing volume")

    elif "mute" in command:
        pyautogui.press("volumemute")
        speak("Muting system")

    elif "exit" in command:
        speak("Goodbye!")
        sys.exit()

    else:
        speak("Sorry, I didn't understand that command.")

# Open application by name (example: "open notepad")
def open_application(application_name):
    try:
        os.startfile(application_name)
        speak(f"Opening {application_name}")
    except Exception as e:
        speak(f"Could not open {application_name}. Error: {e}")

# Get battery status using psutil
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

# Get the current time
def get_time():
    now = datetime.datetime.now()
    current_time = now.strftime("%I:%M %p")
    speak(f"The current time is {current_time}")
    print(f"Current time: {current_time}")

# Open a website with the given URL
def open_website(url):
    try:
        webbrowser.open(f"https://{url}")
        speak(f"Opening {url}")
    except Exception as e:
        speak(f"Could not open the website. Error: {e}")

# Take a screenshot and save it
def take_screenshot():
    screenshot = pyautogui.screenshot()
    screenshot.save("screenshot.png")
    speak("Screenshot taken and saved as screenshot.png")

# Main function to start the assistant
def main():
    speak("Hello! How can I assist you?")
    try:
        take_command_real_time()
    except KeyboardInterrupt:
        print("Program terminated.")
        sys.exit()

if __name__ == "__main__":
    main()
