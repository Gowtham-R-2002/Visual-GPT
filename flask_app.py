
import audioop
import time
from flask import Flask, render_template, request, jsonify

import openai
import os
import pygame
import time
from pydub import AudioSegment
from translate import Translator
from deep_translator import GoogleTranslator
from gtts import gTTS
import sounddevice as sd


import io
import speech_recognition as sr

app = Flask(__name__)

# Set your AssemblyAI and OpenAI API keys
openai_api_key = "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"

# Configure OpenAI API key
openai.api_key = openai_api_key

tts_base_url = "https://texttospeech.googleapis.com/v1/text:synthesize"

@app.route('/', methods=['GET'])
def index():
    return render_template('main.html')

@app.route('/record', methods=['POST'])
def record():
    recognizer = sr.Recognizer()

    # Audio recording using sounddevice
    def audio_callback(indata, frames, time, status):
        audio_data.append(indata.copy())

    audio_data = []
    sample_rate = 44100  # Specify the sample rate
    with sd.InputStream(callback=audio_callback, channels=1, dtype='int16', samplerate=sample_rate):
        print("Listening...")
        silence_threshold = 500  # Adjust silence threshold as needed
        silence_duration = 2  # Adjust silence duration for automatic stopping
        last_audio_time = time.time()

        while True:
            sd.sleep(100)  # Adjust sleep interval as needed

            if len(audio_data) > 0:
                rms = audio_data[-1].max()
                if rms < silence_threshold:
                    if time.time() - last_audio_time > silence_duration:
                        break
                else:
                    last_audio_time = time.time()

    audio_frames = [chunk.tobytes() for chunk in audio_data]
    audio_data_bytes = b''.join(audio_frames)
    audio = sr.AudioData(audio_data_bytes, sample_rate, 2)

    try:
        text = recognizer.recognize_google(audio)
        return jsonify({'text': text})
    except sr.UnknownValueError:
        return jsonify({'error': 'Could not understand audio'})
    except sr.RequestError as e:
        return jsonify({'error': 'Error with the request to Google API: ' + str(e)})
    except sr.WaitTimeoutError:
        print("Timeout: No audio detected within the specified timeout.")


@app.route('/record_tamil', methods=['POST'])
def record_tamil():
    recognizer = sr.Recognizer()

    # Audio recording using sounddevice
    def audio_callback(indata, frames, time, status):
        audio_data.append(indata.copy())

    audio_data = []
    sample_rate = 44100  # Specify the sample rate
    with sd.InputStream(callback=audio_callback, channels=1, dtype='int16', samplerate=sample_rate):
        print("Listening...")
        silence_threshold = 500  # Adjust silence threshold as needed
        silence_duration = 2  # Adjust silence duration for automatic stopping
        last_audio_time = time.time()

        while True:
            sd.sleep(100)  # Adjust sleep interval as needed

            if len(audio_data) > 0:
                rms = audio_data[-1].max()
                if rms < silence_threshold:
                    if time.time() - last_audio_time > silence_duration:
                        break
                else:
                    last_audio_time = time.time()

    audio_frames = [chunk.tobytes() for chunk in audio_data]
    audio_data_bytes = b''.join(audio_frames)
    audio = sr.AudioData(audio_data_bytes, sample_rate, 2)

    try:
        text = recognizer.recognize_google(audio, language="ta-IN")
        translated = GoogleTranslator(source='auto', target='en').translate(text)
        return jsonify({'text': translated})
    except sr.UnknownValueError:
        return jsonify({'error': 'Could not understand audio'})
    except sr.RequestError as e:
        return jsonify({'error': 'Error with the request to Google API: ' + str(e)})
    except sr.WaitTimeoutError:
        print("Timeout: No audio detected within the specified timeout.")


@app.route('/get_gpt3_response', methods=['POST'])
def get_gpt3_response():
    data = request.get_json()
    prompt_text = data.get('prompt_text', '')

        # Call the GPT-3 API
    response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=prompt_text,
            max_tokens=150
        )

    gpt3_response = response['choices'][0]['text']
    return jsonify(gpt3_response=gpt3_response)


@app.route('/get_gpt3_response_tamil', methods=['POST'])
def get_gpt3_response_tamil():
    data = request.get_json()
    prompt_text = data.get('prompt_text', '')

        # Call the GPT-3 API
    response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=prompt_text,
            max_tokens=150
        )

    x = response['choices'][0]['text']

    to_translate = x
    gpt3_response = GoogleTranslator(source='en', target='ta').translate(to_translate)
    tts = gTTS(text=gpt3_response, lang='ta')
    audio_filename = f'output_{time.time()}.mp3'  # Generate a unique filename based on timestamp
    audio_path = os.path.join('static', audio_filename)
    tts.save(audio_path)

    return jsonify(gpt3_response=gpt3_response, audio_url=audio_path)





   




if __name__ == '__main__':
    app.run(debug=True)
