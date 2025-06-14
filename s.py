import subprocess
import time
import requests
import json

NGROK_PATH = r".\ngrok\ngrok.exe" 
PORT = "3389"
SAVE_FILE = "ngrok_tcp_url.txt"

ngrok_proc = subprocess.Popen([NGROK_PATH, "tcp", PORT], stdout=subprocess.DEVNULL)
print("[*] ngrok started... waiting for tunnel to initialize...")
time.sleep(5) 
def get_tcp_url():
    try:
        response = requests.get("http://127.0.0.1:4040/api/tunnels")
        data = response.json()
        for tunnel in data.get("tunnels", []):
            if tunnel["proto"] == "tcp":
                return tunnel["public_url"]
    except Exception as e:
        print(f"[!] Error fetching tunnel: {e}")
        return None

tcp_url = get_tcp_url()

if tcp_url:
    print(f"[✅] ngrok TCP URL: {tcp_url}")
    with open(SAVE_FILE, "w") as f:
        f.write(tcp_url)
else:
    print("[❌] Could not retrieve ngrok TCP URL")

print("[*] Sleeping for 5 hours to keep tunnel alive...")
time.sleep(18000) 

print("[✔️] Done.")
