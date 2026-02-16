import requests
import json

# Configuration
SUPABASE_URL = "https://hmjecisthuzxmczbcksi.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhtamVjaXN0aHV6eG1jemJja3NpIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDkzNzk0MiwiZXhwIjoyMDg2NTEzOTQyfQ.PmJFQNpz2ZYK_5vzvjTnrqKb1Nu790Cp3virfx2IhDg"

def test_connection():
    print(f"Testing connection to {SUPABASE_URL}...")
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    
    # Try to list tables via PostgREST (standard endpoint is /rest/v1/)
    # We'll just try to get the OpenAPI spec or a known table if we knew one.
    # But checking the root of rest/v1/ usually gives a hint or 200 OK.
    
    try:
        # Check health/version or just root
        response = requests.get(f"{SUPABASE_URL}/rest/v1/", headers=headers)
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("Connection Successful! (Root accessed)")
            print("Response hint:", response.text[:200])
        else:
            print("Connection might have issues, or just empty.")
            print("Response:", response.text[:200])

        # Try to query the 'attendance_log' table we created earlier
        print("\nQuerying 'attendance_log'...")
        response = requests.get(f"{SUPABASE_URL}/rest/v1/attendance_log?select=*", headers=headers)
        if response.status_code == 200:
             print("Success! Can read attendance_log.")
             print("Data:", response.json())
        else:
            print(f"Failed to read table. Status: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_connection()
