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
import pvporcupine  # For wake word detection

# Initialize pyttsx3 for text-to-speech
def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# Fuzzy matching function to find similar commands
def match_command(command):
    command_synonyms = {
        "open notepad": ["launch notepad", "start notepad", "run notepad", "open note", "create note"],
        "battery status": ["show battery", "check battery", "battery level", "battery information"],
        "what time is it": ["current time", "time now", "what's the time", "tell me the time"],
        "open website": ["launch site", "open url", "visit website", "go to website"],
        "take screenshot": ["capture screen", "take a snapshot", "screenshot now"],
        "volume up": ["increase volume", "raise volume", "turn up volume", "louder"],
        "volume down": ["decrease volume", "turn down volume", "reduce volume", "quieter"],
        "mute": ["mute sound", "silence", "turn off volume"],
        "lock computer": ["lock pc", "lock the computer", "lock the system"],
        "shutdown": ["turn off computer", "shut down pc", "power off"],
        "restart": ["reboot computer", "restart pc", "reboot system"],
        "log out": ["log off", "sign out", "logout from account"],
        "minimize windows": ["hide windows", "minimize all", "collapse windows"],
        "maximize windows": ["maximize window", "enlarge window"],
        "close window": ["close this window", "exit window", "close the application"],
        "play music": ["start music", "play songs", "open music player"],
        "pause music": ["stop music", "pause song"],
        "show cpu usage": ["cpu performance", "cpu stats", "check cpu usage"],
        "show memory": ["memory status", "check memory", "available memory"],
        "create folder": ["make new folder", "create directory", "new folder"],
        "delete file": ["remove file", "erase file", "delete document"],
        "make a note": ["write a note", "create a note", "new note", "make note"],
    }

    highest_similarity = 0
    best_match = None

    for key_command, synonyms in command_synonyms.items():
        # Check for a direct match or similar command
        for synonym in synonyms:
            similarity = fuzz.ratio(command, synonym)
            if similarity > highest_similarity and similarity > 70:  # 70% threshold
                highest_similarity = similarity
                best_match = key_command

    return best_match

# Function to listen for the wake word using Porcupine
def listen_for_wake_word():
    porcupine = None
    try:
        access_key = "YOUR_ACCESS_KEY_HERE"  # Replace this with your actual Picovoice access key
        porcupine = pvporcupine.create(access_key=access_key, keywords="jarvis")  # Add wake words here
        pa = pyaudio.PyAudio()
        stream = pa.open(format=pyaudio.paInt16, channels=1, rate=porcupine.sample_rate, input=True, frames_per_buffer=porcupine.frame_length)
        stream.start_stream()

        print("Listening for wake word...")

        while True:
            pcm = stream.read(porcupine.frame_length, exception_on_overflow=False)
            pcm = bytearray(pcm)
            keyword_index = porcupine.process(pcm)
            if keyword_index >= 0:
                print("Wake word detected!")
                speak("I'm listening")
                take_command_real_time()

    except KeyboardInterrupt:
        print("Terminated by user")
    finally:
        if porcupine:
            porcupine.delete()

    porcupine = None
    try:
        porcupine = pvporcupine.create(keywords=["Arise", "computer"])  # Customize your wake words here
        pa = pyaudio.PyAudio()
        stream = pa.open(format=pyaudio.paInt16, channels=1, rate=porcupine.sample_rate, input=True, frames_per_buffer=porcupine.frame_length)
        stream.start_stream()

        print("Listening for wake word...")

        while True:
            pcm = stream.read(porcupine.frame_length, exception_on_overflow=False)
            pcm = bytearray(pcm)
            keyword_index = porcupine.process(pcm)
            if keyword_index >= 0:
                print("Wake word detected!")
                speak("I'm listening")
                take_command_real_time()
                
    except KeyboardInterrupt:
        print("Terminated by user")
    finally:
        if porcupine:
            porcupine.delete()

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

    print("Listening for commands...")

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
                else:
                    speak("Sorry, I didn't understand that command.")

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

# Helper functions

# Function to open an application
def open_application(app_path):
    try:
        os.startfile(app_path)
        speak(f"Opening {app_path}")
    except Exception as e:
        speak(f"Unable to open {app_path}: {str(e)}")

# Function to get battery status
def get_battery_status():
    battery = psutil.sensors_battery()
    percent = battery.percent
    speak(f"Battery is at {percent} percent")

# Function to get current time
def get_time():
    time = datetime.datetime.now().strftime("%I:%M %p")
    speak(f"The time is {time}")

# Function to open a website
def open_website(url):
    if not url.startswith("http"):
        url = "http://" + url
    webbrowser.open(url)
    speak(f"Opening {url}")

# Function to take a screenshot
def take_screenshot():
    screenshot = pyautogui.screenshot()
    screenshot.save("screenshot.png")
    speak("Screenshot taken")

# Function to show CPU usage
def show_cpu_usage():
    cpu_percent = psutil.cpu_percent(interval=1)
    speak(f"CPU is at {cpu_percent} percent")

# Function to show memory info
def show_memory_info():
    memory = psutil.virtual_memory()
    speak(f"Available memory is {memory.available / 1024 / 1024:.2f} MB")

# Function to create a folder
def create_folder(folder_name):
    os.makedirs(folder_name, exist_ok=True)
    speak(f"Folder {folder_name} created")

# Function to delete a file
def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
        speak(f"{file_path} has been deleted")
    else:
        speak(f"{file_path} not found")

# Function to make a note
def make_note():
    note = "This is a sample note."
    with open("note.txt", "w") as f:
        f.write(note)
    speak("Note has been written")

# Main function
if __name__ == "__main__":
    listen_for_wake_word()
