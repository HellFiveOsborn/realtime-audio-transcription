# Real-Time Audio Transcription and Translation Script

This Python script captures audio in real-time either from the microphone or internal audio of your PC, transcribes it, and translates it simultaneously. It features a draggable interface that you can place anywhere on your screen to follow live subtitles. The script has been tested on Windows 11 with Python 3.12 and a GTX 1650 GPU, achieving good results for English to Portuguese subtitles. It can be easily adapted for other languages as it uses OpenAI's Whisper locally, and you can choose a translation engine like 'Helsinki-NLP/opus-mt-tc-big-en-pt', Google Translate, or any other.

## Features 🌟

- **Real-Time Audio Capture**: Captures audio from either the microphone or internal PC audio.
- **Simultaneous Transcription and Translation**: Transcribes and translates audio in real-time.
- **Draggable Interface**: A small, draggable interface to place subtitles anywhere on the screen.
- **Customizable**: Easily adaptable to other languages and translation engines.

## Requirements 📋

- Python 3.12
- PyAudio
- NumPy
- Whisper
- Torch
- Tkinter
- Transformers

## Installation 🛠️

1. **Clone the repository**:
   ```bash
   git clone https://github.com/HellFiveOsborn/realtime-audio-transcription.git
   cd realtime-audio-transcription
   ```

2. **Set up a virtual environment**:
   ```bash
   python -m venv venv
   source venv\Scripts\activate  # On Linux use `venv/bin/activate`
   ```
s
3. **Install the required packages**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage 🚀

1. **Run the script**:
   ```bash
   python app.py
   ```

2. **Options**:
   - `--devices`: Print available devices (true or false).
   - `--model`: Choose the Whisper model (`tiny`, `tiny.en`, `small`, `small.en`, `medium`, `medium.en`, `large`).
   - `--device_id`: Device ID from the list of available devices.

## Example Video 🎥

<a href="https://youtu.be/8kcFwBryL0M" target="_blank">
  <img src="https://img.youtube.com/vi/8kcFwBryL0M/maxresdefault.jpg" alt="Watch the video" width="640" height="360">
</a>

## Contributing 🤝

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License 📄

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements 🙏

- [OpenAI Whisper](https://github.com/openai/whisper)
- [Helsinki-NLP](https://huggingface.co/Helsinki-NLP)