import ctypes
import json
import time
import urllib.request
import urllib.error
import socket
from datetime import datetime

# --- CONFIGURATION ---
# Replace with your actual n8n webhook URL
N8N_WEBHOOK_URL = "http://localhost:5678/webhook/monitor" 
API_KEY = "tu_api_key_secreta"  # Hardcoded or load from env/config
BATCH_INTERVAL = 15 * 60  # 15 minutes in seconds
BUFFER_CHECK_INTERVAL = 1.0 # Check active window every 1 second

# --- WIN32 API CONSTANTS & STRUCTURES ---
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

def get_active_window_title():
    hwnd = user32.GetForegroundWindow()
    if not hwnd:
        return None
    length = user32.GetWindowTextLengthW(hwnd)
    if length == 0:
        return "Unknown/Empty"
    buff = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buff, length + 1)
    return buff.value

def send_data(payload):
    req = urllib.request.Request(
        N8N_WEBHOOK_URL,
        data=json.dumps(payload).encode('utf-8'),
        headers={
            "Content-Type": "application/json",
            "x-api-key": API_KEY
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req) as response:
            print(f"Data sent. Status: {response.status}")
    except urllib.error.URLError as e:
        print(f"Failed to send data: {e}")

def main():
    pc_name = socket.gethostname()
    buffer = {} # Key: Window Title, Value: Duration (seconds)
    last_flush_time = time.time()
    
    print(f"Monitoring started on {pc_name}...")

    try:
        while True:
            current_title = get_active_window_title()
            
            if current_title:
                if current_title in buffer:
                    buffer[current_title] += BUFFER_CHECK_INTERVAL
                else:
                    buffer[current_title] = BUFFER_CHECK_INTERVAL

            # Check if it's time to flush
            if time.time() - last_flush_time >= BATCH_INTERVAL:
                if buffer:
                    # Prepare payload
                    activity_list = [
                        {"window_title": k, "duration_seconds": v} 
                        for k, v in buffer.items()
                    ]
                    
                    payload = {
                        "pc_name": pc_name,
                        "timestamp": datetime.now().isoformat(),
                        "activities": activity_list
                    }
                    
                    print("Flushing buffer to n8n...")
                    send_data(payload)
                    buffer.clear() # Reset buffer
                    last_flush_time = time.time()
                else:
                    # Reset timer even if empty to avoid immediate flush next loop
                    last_flush_time = time.time()

            time.sleep(BUFFER_CHECK_INTERVAL)
            
    except KeyboardInterrupt:
        print("Monitoring stopped.")

if __name__ == "__main__":
    main()
