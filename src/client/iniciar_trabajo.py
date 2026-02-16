import subprocess
import urllib.request
import urllib.error
import json
import ctypes
import os
import sys

# --- CONFIGURATION ---
# Replace with your actual n8n webhook URL
N8N_WEBHOOK_URL = "http://localhost:5678/webhook/monitor" 
API_KEY = "tu_api_key_secreta"
MONITOR_EXECUTABLE = "monitor_core.exe" # Assumes it's in the same directory

def show_message(title, text):
    # MessageBoxW(hwnd, text, title, type)
    # type 0 = MB_OK
    ctypes.windll.user32.MessageBoxW(0, text, title, 0x40 | 0) # 0x40 = MB_ICONINFORMATION

def send_webhook(action):
    payload = {
        "action": action,
        "pc_name": os.getenv('COMPUTERNAME', 'Unknown'),
        "timestamp": "" # Let server handle timestamp or generate here
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
    # 1. Send Webhook
    print("Sending start signal...")
    if send_webhook("INICIO_JORNADA"):
        print("Signal sent.")
    else:
        print("Warning: Could not send start signal to server.")

    # 2. Launch Monitor Core
    # We look for the executable in the same directory as this script is running
    current_dir = os.path.dirname(os.path.abspath(__file__))
    monitor_path = os.path.join(current_dir, MONITOR_EXECUTABLE)
    
    # Check if exe exists, otherwise try .py for development
    if not os.path.exists(monitor_path):
        monitor_path_py = os.path.join(current_dir, "monitor_core.py")
        if os.path.exists(monitor_path_py):
            # Development mode: launch with pythonw (no console) or python
            monitor_path = ["python", monitor_path_py] 
        else:
            show_message("Error", f"No se encontró {MONITOR_EXECUTABLE} ni monitor_core.py")
            return
    else:
        monitor_path = [monitor_path]

    try:
        # Launch independently
        subprocess.Popen(monitor_path, cwd=current_dir, creationflags=subprocess.CREATE_NO_WINDOW)
    except Exception as e:
        show_message("Error", f"No se pudo iniciar el monitor: {e}")
        return

    # 3. Show Popup
    show_message("Monitor de Productividad", "✅ Sesión Iniciada. El registro está activo")

if __name__ == "__main__":
    main()
