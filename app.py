import pyaudio
import numpy as np
import whisper
import torch
import tkinter as tk
from tkinter import ttk
import threading
import sys
import signal
import wave
import sounddevice as sd
import argparse
from transformers import pipeline

# Argument parsing
parser = argparse.ArgumentParser(description="List of available options")
parser.add_argument("--devices", default='false', type=str, help="Print devices ID, true or false")
parser.add_argument("--model", type=str, choices=['tiny','tiny.en', 'small', 'small.en', 'medium', 'medium.en', 'large'], default='tiny.en', help='Whisper model to be used, choose from {tiny, tiny.en, small, small.en, medium, medium.en, large}')
parser.add_argument("--device_id", default=1, type=int, help="Device ID from the list of available devices, Microphone or Loopback device")
args = parser.parse_args()

# Audio settings
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 2
DEVICE_INDEX: int = args.device_id

def str2bool(string):
    str2val = {"true": True, "false": False}
    if string.lower() in str2val:
        return str2val[string.lower()]
    else:
        raise ValueError(f"Expected one of {set(str2val.keys())}, got {string}")

if not str2bool(args.devices):
    # Start of the Whisper model
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = whisper.load_model(args.model, device=device)

    # Initialization of the translation model
    print("Loading model of translation...")
    translator = pipeline("translation", model="Helsinki-NLP/opus-mt-tc-big-en-pt", device=0 if torch.cuda.is_available() else -1)

    # Configuration of the Tkinter window
    root = tk.Tk()
    root.overrideredirect(True)
    root.wm_attributes("-topmost", True)
    root.attributes("-alpha", 0.6) # Sets the transparency of the main window
    root.configure(bg='black')  # Sets the background of the main window to black

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width = int(screen_width * 0.50) # Adjust the width as needed (50% of the screen width)
    window_height = 100 # Adjust the height as needed

    x = (screen_width - window_width) // 2
    y = screen_height - 200

    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    # Create a main frame
    main_frame = tk.Frame(root, bg='black')
    main_frame.pack(fill="both", expand=True)

    # Create labels for the original and translated text, adjust the font size as needed and color.
    label_translated = tk.Label(main_frame, text="[...]", fg="yellow", bg="black", font=("Arial", 16), wraplength=window_width-20)
    label_translated.pack(fill="both", expand=True, padx=10, pady=3)
    label_original = tk.Label(main_frame, text="[...]", fg="gray", bg="black", font=("Arial", 16), wraplength=window_width-20, )
    label_original.pack(fill="both", expand=True, padx=10, pady=3)

    # Add a close button
    close_button = tk.Button(main_frame, text="×", command=root.quit, bg="red", fg="white")
    close_button.place(relx=1.0, rely=0.0, anchor='ne')

    running = True

def on_press(event):
    """
    Sets the x and y coordinates of the root window to the coordinates of the mouse event.

    Parameters:
        event (Event): The mouse event that triggered the function.

    Returns:
        None
    """
    root.x = event.x
    root.y = event.y

def on_drag(event):
    """
    Updates the position of the root window based on the mouse drag event.

    Parameters:
        event (Event): The mouse drag event that triggered the function.

    Returns:
        None
    """
    x = root.winfo_x() - root.x + event.x
    y = root.winfo_y() - root.y + event.y
    root.geometry(f"+{x}+{y}")

if not str2bool(args.devices):
    # Change the cursor to move style throughout the window.
    root.bind("<Enter>", lambda e: root.config(cursor="fleur"))
    root.bind("<Leave>", lambda e: root.config(cursor=""))
    close_button.bind("<Enter>", lambda e: close_button.config(cursor="hand2"))
    close_button.bind("<Leave>", lambda e: root.config(cursor="fleur"))
    root.bind("<ButtonPress-1>", on_press)
    root.bind("<B1-Motion>", on_drag)

def adjust_window_height():
    """
    Updates the window height based on the requested heights of the original and translated labels.
    """
    new_height = label_original.winfo_reqheight() + label_translated.winfo_reqheight() + 20  # 20 for padding and close button
    root.geometry(f"{window_width}x{new_height}+{root.winfo_x()}+{root.winfo_y()}")

def audio_capture_and_process():
    """
    Captures audio from the specified input device and processes it.

    This function opens a PyAudio stream to capture audio from the specified input device. It then records audio for a specified number of seconds and saves it as a WAV file. The recorded audio is then transcribed using a specified model. The transcription is displayed in the original label and, if available, translated to the specified language.

    Parameters:
        None

    Returns:
        None

    Raises:
        Exception: If there is an error in audio capture and processing.

    """
    global running
    p = pyaudio.PyAudio()

    try:
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        input_device_index=DEVICE_INDEX,
                        frames_per_buffer=CHUNK)

        print("Stream opened successfully")

        while running:
            print("Recording...")
            frames = []
            for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                data = stream.read(CHUNK, exception_on_overflow=False)
                frames.append(data)

            print("Finished recording")

            # Save as WAV file
            wf = wave.open("temp.wav", "wb")
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
            wf.close()

            print("Transcribing...")
            result = model.transcribe("temp.wav", task="transcribe", language="en", fp16=torch.cuda.is_available())
            transcription = result["text"].strip()

            if transcription:
                label_original.config(text=transcription)
                try:
                    translation = translator(transcription, max_length=512)[0]['translation_text']
                    label_translated.config(text=translation)
                except Exception as e:
                    print(f"Error in translation: {e}")
                    label_translated.config(text="...")
            else:
                label_original.config(text="[...]")
                label_translated.config(text="[...]")

            adjust_window_height()
            root.update()

    except Exception as e:
        print(f"Error in audio capture and processing: {e}")
    finally:
        if 'stream' in locals():
            stream.stop_stream()
            stream.close()
        p.terminate()

def start_threads():
    """
    Starts the audio capture and processing thread.

    This function creates a new thread that runs the `audio_capture_and_process` function. The thread is set as a daemon, which means it will be terminated when the main program exits. The thread starts running immediately after being created.

    Parameters:
        None

    Returns:
        None
    """
    audio_thread = threading.Thread(target=audio_capture_and_process)
    audio_thread.daemon = True
    audio_thread.start()

def on_closing():
    """
    Sets the global variable `running` to False, quits the root window, and exits the program.

    This function is called when the root window is closed. It sets the global variable `running` to False, indicating that the program should stop running. It then quits the root window and exits the program.

    Parameters:
        None

    Returns:
        None
    """
    global running
    running = False
    root.quit()
    sys.exit(0)

def signal_handler(sig, frame):
    on_closing()

if not str2bool(args.devices):
    root.protocol("WM_DELETE_WINDOW", on_closing)
    signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":
    if str2bool(args.devices) == True:
        print(sd.query_devices())
    else:
        print(f"Using {device}.")
        start_threads()
        try:
            root.mainloop()
        except KeyboardInterrupt:
            on_closing()