import urllib.request
import urllib.error
import json
import ctypes
import os
import subprocess

# --- CONFIGURATION ---
N8N_WEBHOOK_URL = "http://localhost:5678/webhook/monitor" 
API_KEY = "tu_api_key_secreta"

def show_message(title, text):
    # MessageBoxW(hwnd, text, title, type)
    ctypes.windll.user32.MessageBoxW(0, text, title, 0x40 | 0)

def send_webhook(action):
    payload = {
        "action": action,
        "pc_name": os.getenv('COMPUTERNAME', 'Unknown')
    }
    
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
        urllib.request.urlopen(req)
    except Exception:
        pass # Ignore errors on exit

def main():
    # 1. Kill Monitor Process
    # Force kill /IM monitor_core.exe
    # Also kill python process if running as script (this is tricky in dev, be careful not to kill self if same name?)
    # For production with .exe, simple:
    
    try:
        # Try to kill the exe
        subprocess.run(["taskkill", "/F", "/IM", "monitor_core.exe"], capture_output=True)
        # Also try to kill the python script version if testing (be careful, might kill other python scripts)
        # subprocess.run(["taskkill", "/F", "/IM", "python.exe", "/FI", "WINDOWTITLE eq monitor_core.py"], capture_output=True) 
        # The above logic for python script killing is flaky, sticking to exe or manual in dev.
    except Exception as e:
        print(f"Error killing process: {e}")

    # 2. Send Webhook
    send_webhook("FIN_JORNADA")

    # 3. Show Popup
    show_message("Monitor de Productividad", "🛑 Sesión Terminada. Buen descanso")

if __name__ == "__main__":
    main()
