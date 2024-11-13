import os
import threading
import subprocess
from concurrent.futures import ThreadPoolExecutor
import time
from config import INPUT_PATH, OUTPUT_PATH

def process_file(ts_file, index):
    input_path = INPUT_PATH  # Define input folder PATH
    output_path = OUTPUT_PATH  # Define output folder PATH
    
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    ts_file_path = os.path.join(input_path, ts_file)
    base_name = os.path.splitext(ts_file)[0]
    output_wav_file = os.path.join(output_path, f"{base_name}.wav")
    rtsp_stream_url = f"rtsp://localhost:8554/stream{index}"

    # Step 1: Starting RTSP Stream
    def start_rtsp_stream():
        rtsp_stream_cmd = f"ffmpeg -re -i \"{ts_file_path}\" -map 0:a:0 -acodec aac -ar 44100 -ac 2 -f rtsp {rtsp_stream_url}"
        subprocess.run(rtsp_stream_cmd, shell=True)

    # Step 2: Capturing Audio from RTSP Stream
    def capture_audio_from_rtsp():
        time.sleep(5)  # Wait 5 seconds to ensure stream is active
        capture_cmd = f"ffmpeg -i {rtsp_stream_url} -bufsize 1024k -maxrate 1024k -acodec pcm_s16le -ar 44100 -ac 2 \"{output_wav_file}\""
        subprocess.run(capture_cmd, shell=True)

    rtsp_thread = threading.Thread(target=start_rtsp_stream)
    capture_thread = threading.Thread(target=capture_audio_from_rtsp)

    rtsp_thread.start()
    time.sleep(1)  
    capture_thread.start()

    rtsp_thread.join()
    capture_thread.join()

def main():
    input_path = INPUT_PATH
    ts_files = [f for f in os.listdir(input_path) if f.endswith('.ts')]
    
    with ThreadPoolExecutor(max_workers=2) as executor:
        for index, ts_file in enumerate(ts_files):
            executor.submit(process_file, ts_file, index)

if __name__ == "__main__":
    main()
