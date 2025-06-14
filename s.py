import subprocess
import time
import requests
import zipfile
import os
import re

NGROK_URL = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip"
NGROK_ZIP = "ngrok.zip"
NGROK_FOLDER = "ngrok"
NGROK_EXE = os.path.join(NGROK_FOLDER, "ngrok.exe")
PORT = "3389"
SAVE_FILE = "ngrok_tcp_url.txt"
MAX_RETRIES = 10
WAIT_BETWEEN_RETRIES = 5

# Regex: checks for region (e.g., 2.tcp.us-cal-1.ngrok.io)
VALID_TCP_URL = re.compile(r"tcp://\d+\.tcp\.[a-z\-]+\d*\.ngrok\.io:\d+")

# Download ngrok if not exists
if not os.path.exists(NGROK_EXE):
    print("[*] Downloading ngrok...")
    r = requests.get(NGROK_URL)
    with open(NGROK_ZIP, "wb") as f:
        f.write(r.content)

    print("[*] Extracting ngrok...")
    with zipfile.ZipFile(NGROK_ZIP, 'r') as zip_ref:
        zip_ref.extractall(NGROK_FOLDER)

# Fetch ngrok TCP URL from API
def get_tcp_url():
    try:
        r = requests.get("http://127.0.0.1:4040/api/tunnels")
        data = r.json()
        for tunnel in data.get("tunnels", []):
            if tunnel.get("proto") == "tcp":
                return tunnel.get("public_url")
    except Exception as e:
        print(f"[!] Error fetching URL: {e}")
    return None

# Try launching ngrok up to N times until regional TCP URL found
tcp_url = None
for attempt in range(1, MAX_RETRIES + 1):
    print(f"[*] Attempt {attempt} to start ngrok...")

    ngrok_proc = subprocess.Popen([NGROK_EXE, "tcp", PORT], stdout=subprocess.DEVNULL)
    time.sleep(WAIT_BETWEEN_RETRIES)

    tcp_url = get_tcp_url()

    if tcp_url and VALID_TCP_URL.match(tcp_url):
        print(f"[h] Found regional TCP URL: {tcp_url}")
        with open(SAVE_FILE, "w") as f:
            f.write(tcp_url)
        break
    else:
        print(f"[h] Invalid TCP URL: {tcp_url}")
        ngrok_proc.terminate()
        time.sleep(2)

if not tcp_url or not VALID_TCP_URL.match(tcp_url):
    print("[j] Failed to get a valid regional TCP URL after all attempts.")
    exit(1)

print("[*] Keeping tunnel alive for 5 hours...")
time.sleep(18000)
print("[✔️] Done.")
