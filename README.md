# System Deployment & usage Guide

## 1. Environment Setup

### Prerequisites
- Python 3.x installed.
- `pip install pyinstaller requests` (requests is optional if using urllib, but standard lib utilized as requested).

## 2. Compiling the Client (PyInstaller)
To generate the `.exe` files, run the following commands in your terminal (inside `src/client`):

### Monitor Core (Background Process - Hidden Console)
```powershell
pyinstaller --noconsole --onefile monitor_core.py
```

### Start Trigger (User Interface)
```powershell
# Optional: Add --noconsole to hide the black window background, assuming you only want the popup.
pyinstaller --noconsole --onefile iniciar_trabajo.py
```

### Stop Trigger (User Interface)
```powershell
pyinstaller --noconsole --onefile finalizar_trabajo.py
```

*The executables will be located in the `dist` folder.*

## 3. Database Setup (Supabase)
1.  Go to your Supabase Project -> SQL Editor.
2.  Copy and paste the content of `src/server/schema.sql`.
3.  Run the query to create tables.

## 4. n8n Configuration
1.  Create a new Workflow in n8n.
2.  Set up the **Webhook** node (POST, `/webhook/monitor`).
3.  Use the logic described in `src/server/n8n_workflow.md` or import the provided JSON snippet.
4.  Configure the **Postgres** node with your Supabase credentials (Host, User, Password, Database).

## 5. Usage
1.  Employee clicks `iniciar_trabajo.exe`.
    - Message "✅ Sesión Iniciada" appears.
    - `monitor_core.exe` starts running in background.
2.  Work happens... (Data sent every 15 mins).
3.  Employee clicks `finalizar_trabajo.exe`.
    - `monitor_core.exe` is killed.
    - Message "🛑 Sesión Terminada" appears.
