import os
from pydub import AudioSegment
from config import OUTPUT_PATH, MONO_CHANNEL_OUTPUT

input_folder = OUTPUT_PATH  # Path of the .wav audio folder
output_folder = MONO_CHANNEL_OUTPUT  # Path for adjusted audio output (mono_channel)

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

files = os.listdir(input_folder)

for file in files:
    if file.endswith(".wav"):
        input_path = os.path.join(input_folder, file)
        
        audio = AudioSegment.from_wav(input_path)
        audio = audio.set_channels(1)
        audio = audio.set_frame_rate(16000)

        output_file = os.path.join(output_folder, file)

        audio.export(output_file, format="wav")