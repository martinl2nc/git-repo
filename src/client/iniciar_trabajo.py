import subprocess
import urllib.request
import urllib.error
import json
import ctypes
import os
import sys

# --- CONFIGURATION ---
from config import N8N_WEBHOOK_URL, API_KEY
MONITOR_EXECUTABLE = "monitor_core.exe"
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
        "pc_name": os.getenv('COMPUTERNAME', 'Unknown'),
        "timestamp": ""
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
        with urllib.request.urlopen(req) as response:
            return True
    except Exception as e:
        print(f"Error sending webhook: {e}")
        return False

def main():
    # 0. Check if already working
    current_status = get_status()
    if current_status == "WORKING":
        show_warning("Monitor de Productividad", "⚠️ Ya tienes una sesión activa.\nNo puedes iniciar otra sin finalizar la anterior.")
        return

    # 1. Send Webhook
    print("Sending start signal...")
    if send_webhook("INICIO_JORNADA"):
        print("Signal sent.")
        set_status("WORKING")
    else:
        print("Warning: Could not send start signal to server.")
        # Still allow local start even if webhook fails
        set_status("WORKING")

    # 2. Launch Monitor Core
    if getattr(sys, 'frozen', False):
        current_dir = os.path.dirname(sys.executable)
    else:
        current_dir = os.path.dirname(os.path.abspath(__file__))
    monitor_path = os.path.join(current_dir, MONITOR_EXECUTABLE)
    
    if not os.path.exists(monitor_path):
        monitor_path_py = os.path.join(current_dir, "monitor_core.py")
        if os.path.exists(monitor_path_py):
            monitor_path = ["python", monitor_path_py] 
        else:
            show_message("Error", f"No se encontró {MONITOR_EXECUTABLE} ni monitor_core.py")
            return
    else:
        monitor_path = [monitor_path]

    try:
        subprocess.Popen(monitor_path, cwd=current_dir, creationflags=subprocess.CREATE_NO_WINDOW)
    except Exception as e:
        show_message("Error", f"No se pudo iniciar el monitor: {e}")
        return

    # 3. Show Popup
    show_message("Monitor de Productividad", "✅ Sesión Iniciada. El registro está activo")

if __name__ == "__main__":
    main()
