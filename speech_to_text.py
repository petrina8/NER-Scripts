import os
import csv
from vosk import Model, KaldiRecognizer
import wave
import json
from config import MONO_CHANNEL_OUTPUT, VOSK_MODEL_PATH
from collections import defaultdict
import spacy

class AudioTranscriber:
    def __init__(self, input_folder=MONO_CHANNEL_OUTPUT, output_csv='output.csv'):
        self.input_folder = input_folder
        self.output_csv = output_csv
        self.model = Model(VOSK_MODEL_PATH)
        self.nlp = spacy.load('pt_core_news_lg')


    def extract_ner_tags(self, text):
        doc = self.nlp(text)
        ner_dict = defaultdict(list)
        
        for token in doc:
            if token.ent_type_:
                # Mapeia as entidades do spaCy para as categorias desejadas
                ent_map = {
                    'ORG': 'ORG',
                    'GPE': 'LOC',
                    'LOC': 'LOC',
                    'PER': 'PER',
                    'PERSON': 'PER',
                    'MISC': 'MISC'
                }
                
                if token.ent_type_ in ent_map:
                    ent_tag = ent_map[token.ent_type_]
                    
                    # Define o prefixo (B- ou I-) baseado no IOB
                    prefix = 'B-' if token.ent_iob_ == 'B' else 'I-'
                    full_tag = f"{prefix}{ent_tag}"
                    
                    # Adiciona o token ao dicionário com a tag apropriada
                    ner_dict[full_tag].append(token.text)
        
        # Converter listas em strings
        result = {tag: ' '.join(tokens) for tag, tokens in ner_dict.items()}
        
        # Garantir que todas as tags existam no dicionário, mesmo que vazias
        all_tags = [f"{prefix}{tag}" for prefix in ['B-', 'I-'] 
                   for tag in ['PER', 'ORG', 'LOC', 'MISC']]
        
        # Preencher tags ausentes com strings vazias
        final_dict = {tag: result.get(tag, "") for tag in all_tags}
        
        return json.dumps(final_dict, ensure_ascii=False)


    def transcribe_folder(self):
        with open(self.output_csv, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['ts_file', 'text_transcription', 'ner_spacy_entities']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            files = os.listdir(self.input_folder)

            for file in files:
                if file.endswith(".wav"):
                    input_path = os.path.join(self.input_folder, file)
                    transcribed_text = self.transcribe_audio(input_path)
                    ner_spacy_entities = self.extract_ner_tags(transcribed_text)
                    
                    writer.writerow({
                        'ts_file': (file.split('.')[0] + '.ts'),
                        'text_transcription': transcribed_text,
                        'ner_spacy_entities': ner_spacy_entities
                    })

        return f"Transcrições e anotações CoNLL salvas em {self.output_csv}"

    def transcribe_audio(self, input_path):
        rec = KaldiRecognizer(self.model, 16000)
        wf = wave.open(input_path, "rb")
        transcribed_text_list = []

        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                transcribed_text_list.append(result['text'])

        final_result = json.loads(rec.FinalResult())
        transcribed_text_list.append(final_result['text'])

        complete_text = ' '.join(transcribed_text_list)
        return complete_text

if __name__ == "__main__":
    transcriber = AudioTranscriber()
    print(transcriber.transcribe_folder())
