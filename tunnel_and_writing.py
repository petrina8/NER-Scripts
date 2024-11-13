import os
import time
import subprocess
import datetime
import threading
from config import ROOT_FOLDER

folder = ROOT_FOLDER  # Add root folder path
WAITING_TIME = 900  # Wait interval between recording list starts - Ex: 900 = 15 minutes wait
WRITING_TIME = 90  # TS recording seconds - Ex: 90 = 1 minute and 30 seconds of recording

def list_out_files(folder):
    return [file for file in os.listdir(folder) if file.endswith('.out')]

def run_file_out(file, channel_name, duracao_captura):
    path_full = os.path.join(folder, file)
    os.chmod(path_full, 0o755)
    print(f"Executando {file} e iniciando captura de vídeo para o canal {channel_name}...")

    # Start capturing video in another thread, passing the channel name directly
    thread_record = threading.Thread(target=capture_video, args=(channel_name, duracao_captura,))
    thread_record.start()

    try:
        record_process = subprocess.Popen(path_full)
        time.sleep(WRITING_TIME)
        record_process.terminate()
        try:
            record_process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            print(f"O processo {file} não terminou no tempo esperado após o término. Será forçado a fechar.")
            record_process.kill()
        print(f"{file} executado por {WRITING_TIME / 60} minutos e depois terminado.")
    except Exception as e:
        print(f"Erro ao executar {file}: {e}")

    # Wait the end of the capture
    thread_record.join()

def capture_video(channel_name, duracao):
    timestamp = datetime.datetime.now().strftime('%d_%m_%Y_%H%M%S')
    file_name = f"{channel_name}_{timestamp}.ts"

    with open(file_name, 'wb') as out_file, open('/dev/dvb/adapter0/dvr0', 'rb') as dvr:
        print(f"Iniciando captura de vídeo para o canal {channel_name}...")
        start_time = time.time()
        try:
            while time.time() - start_time < duracao:
                data = dvr.read(1024)
                if not data:
                    break
                out_file.write(data)
            print(f"Captura de vídeo para o canal {channel_name} concluída.")
        except Exception as e:
            print(f"Erro durante a captura de vídeo: {e}")

def main():
    try:
        record_time = WRITING_TIME
        while True:
            files = list_out_files(folder)
            for file in files:
                channel_name = file[:-4] 
                run_file_out(file, channel_name, record_time)
            print(f"Aguardando {(WAITING_TIME/60)} minutos para a próxima captura...")
            time.sleep(WAITING_TIME)
    except KeyboardInterrupt:
        print("Execução interrompida pelo usuário.")

if __name__ == "__main__":
    main()