# NER-Scripts
Repository containing scripts utilized in the experiments conducted for the paper "Natural Language Processing Models for Named Entity Recognition in Digital TV Audio."


# Automation in capturing, extracting, transcribing, and labeling Transport Stream (TS) files
### About the scripts
Each script is responsible for performing a specific task, whether it's extracting audio from a TS file or performing transcription and labeling using SpaCy.

## TS Capture
### Generating files for each broadcaster
Access the tuner.cpp file, change line 93 to the channel frequency. Finally, compile the file generating the .out file, renaming it to the desired channel name. To compile the file, execute the following command:
```sh
g++ tune.cpp
```

### Performing TS capture
Once you have one or more compiled files for the channels, execute the following command to tune the dongle and capture TS from the channels:
```sh
python tunnel_and_writing.py
```
**Capture time and capture interval can be adjusted in the tunnel_and_writing.py file**

## Audio Extraction
### Setting up the environment
Before running the script, the user needs to run a docker server using the following command:
```sh
sudo docker run --rm -it --network=host bluenviron/mediamtx:latest 
```
Then create a virtual environment:
```sh
python -m venv env
```
After creation, access it with the following command:
*WINDOWS*
```sh
./env/Scripts/activate
```
*LINUX*
```sh
source env/bin/activate
```
Then, after accessing the created virtual environment, run the following command to install dependencies:
```sh
pip install -r requirements.txt
```
Finally, download the spaCy base:
```sh
python -m spacy download pt_core_news_lg
```
**If necessary, folder paths can be adjusted in the config.py file.**

## Execution
To run the scripts, just use the environment with the RTSP server running. Then:
Run the convert_ts_to_wav.py script to extract audio from TS files:
```sh
python convert_ts_to_wav.py
```
To standardize the audio output, run the following command:
```sh
python adjust_wav.py
```
Finally, run speech_to_text.py to perform audio transcription using the VOSK API:
```sh
python speech_to_text.py
```
