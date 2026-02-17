import urllib.request
import urllib.error
import json
import ctypes
import os
import subprocess

# --- CONFIGURATION ---
from config import N8N_WEBHOOK_URL, API_KEY
STATUS_FILE = os.path.join(os.path.expanduser("~"), ".monitor_status")

def show_message(title, text):
    ctypes.windll.user32.MessageBoxW(0, text, title, 0x40 | 0)

def show_warning(title, text):
    ctypes.windll.user32.MessageBoxW(0, text, title, 0x30 | 0)  # 0x30 = MB_ICONWARNING

def get_status():
    """Read current work status from file."""
    try:
        if os.path.exists(STATUS_FILE):
            with open(STATUS_FILE, 'r') as f:
                return f.read().strip()
    except Exception:
        pass
    return "IDLE"

def set_status(status):
    """Write current work status to file."""
    try:
        with open(STATUS_FILE, 'w') as f:
            f.write(status)
    except Exception:
        pass

def send_webhook(action):
    payload = {
        "action": action,
        "pc_name": os.getenv('COMPUTERNAME', 'Unknown').upper()
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
        pass

def main():
    # 0. Check if already idle
    current_status = get_status()
    if current_status != "WORKING":
        show_warning("Monitor de Productividad", "⚠️ No hay una sesión activa.\nDebes iniciar una sesión primero.")
        return

    # 1. Kill Monitor Process
    try:
        subprocess.run(["taskkill", "/F", "/IM", "monitor_core.exe"], capture_output=True)
    except Exception as e:
        print(f"Error killing process: {e}")

    # 2. Send Webhook
    send_webhook("FIN_JORNADA")

    # 3. Update status
    set_status("IDLE")

    # 4. Show Popup
    show_message("Monitor de Productividad", "🛑 Sesión Terminada. Buen descanso")

if __name__ == "__main__":
    main()
