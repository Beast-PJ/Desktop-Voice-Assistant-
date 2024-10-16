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
from fuzzywuzzy import fuzz

# Initialize pyttsx3 for text-to-speech
def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# Real-time voice command processing with fuzzy matching
def take_command_real_time():
    model_path = "path/to/vosk-model"
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
        data = stream.read(4000, exception_on_overflow=False)
        if len(data) == 0:
            continue

        if recognizer.AcceptWaveform(data):
            result = recognizer.Result()
            result_json = json.loads(result)
            command = result_json.get('text', '').lower()
            if command:
                print(f"You said: {command}")
                best_command = match_command(command)
                if best_command:
                    print(f"Best match: {best_command}")
                    execute_command(best_command)

# Fuzzy matching to interpret mispronunciations
def match_command(command):
    commands = [
        "open notepad", "battery status", "what time is it", "open website",
        "take screenshot", "volume up", "volume down", "mute", "exit",
        "lock computer", "shutdown", "restart", "log out", "minimize windows", 
        "maximize windows", "close window", "play music", "pause music", 
        "show cpu usage", "show memory", "create folder", "delete file", "make a note"
    ]

    best_match = None
    highest_similarity = 0

    for predefined_command in commands:
        similarity = fuzz.ratio(command, predefined_command)
        if similarity > highest_similarity and similarity > 70:  # 70% match threshold
            highest_similarity = similarity
            best_match = predefined_command

    return best_match

# Command execution based on the best match
def execute_command(command):
    if "open notepad" in command:
        open_application("notepad.exe")
    elif "battery status" in command:
        get_battery_status()
    elif "what time is it" in command:
        get_time()
    elif "open website" in command:
        url = command.split("website", 1)[1].strip()
        open_website(url)
    elif "take screenshot" in command:
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
    elif "lock computer" in command:
        os.system("rundll32.exe user32.dll,LockWorkStation")
        speak("Locking the computer")
    elif "shutdown" in command:
        os.system("shutdown /s /t 1")
        speak("Shutting down the computer")
    elif "restart" in command:
        os.system("shutdown /r /t 1")
        speak("Restarting the computer")
    elif "log out" in command:
        os.system("shutdown /l")
        speak("Logging out")
    elif "minimize windows" in command:
        pyautogui.hotkey("win", "d")
        speak("Minimizing all windows")
    elif "maximize windows" in command:
        pyautogui.hotkey("win", "up")
        speak("Maximizing windows")
    elif "close window" in command:
        pyautogui.hotkey("alt", "f4")
        speak("Closing current window")
    elif "play music" in command:
        open_application("C:\\Path\\To\\MusicPlayer.exe")  # Modify with your music player path
    elif "pause music" in command:
        pyautogui.press("playpause")
        speak("Pausing music")
    elif "show cpu usage" in command:
        show_cpu_usage()
    elif "show memory" in command:
        show_memory_info()
    elif "create folder" in command:
        create_folder("NewFolder")
    elif "delete file" in command:
        delete_file("file_to_delete.txt")  # Modify file path accordingly
    elif "make a note" in command:
        make_note()
    elif "exit" in command:
        speak("Goodbye!")
        sys.exit()
    else:
        speak("Sorry, I didn't understand that command.")

# Open application by name
def open_application(application_name):
    try:
        os.startfile(application_name)
        speak(f"Opening {application_name}")
    except Exception as e:
        speak(f"Could not open {application_name}. Error: {e}")

# Get battery status using psutil
def get_battery_status():
    battery = psutil.sensors_battery()
    if battery:
        plugged = "Plugged in" if battery.power_plugged else "Not plugged in"
        speak(f"Battery is {battery.percent} percent and {plugged}")
    else:
        speak("Could not retrieve battery information.")

# Get current time
def get_time():
    now = datetime.datetime.now()
    current_time = now.strftime("%I:%M %p")
    speak(f"The current time is {current_time}")

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
    speak("Screenshot taken and saved.")

# Show CPU usage
def show_cpu_usage():
    cpu_usage = psutil.cpu_percent(interval=1)
    speak(f"CPU usage is {cpu_usage} percent")

# Show available memory
def show_memory_info():
    memory = psutil.virtual_memory()
    speak(f"Available memory is {memory.available // (1024 * 1024)} MB")

# Create a new folder
def create_folder(folder_name):
    try:
        os.mkdir(folder_name)
        speak(f"Created folder {folder_name}")
    except FileExistsError:
        speak("Folder already exists")

# Delete a file
def delete_file(file_name):
    try:
        os.remove(file_name)
        speak(f"Deleted file {file_name}")
    except FileNotFoundError:
        speak(f"File {file_name} not found")

# Create a quick note
def make_note():
    with open("note.txt", "w") as file:
        file.write("This is a quick note.")
    speak("Note has been created.")

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
