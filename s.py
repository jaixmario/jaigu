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
WAIT_BETWEEN_RETRIES = 5  # seconds

# Only allow regional-style ngrok TCP URLs (exclude 0.tcp)
VALID_TCP_URL = re.compile(r"tcp://(?!0\.).+\.tcp\.[a-z\-]+\d*\.ngrok\.io:\d+")

# Step 1: Download ngrok if not exists
if not os.path.exists(NGROK_EXE):
    print("[*] Downloading ngrok...")
    r = requests.get(NGROK_URL)
    with open(NGROK_ZIP, "wb") as f:
        f.write(r.content)

    print("[*] Extracting ngrok...")
    with zipfile.ZipFile(NGROK_ZIP, 'r') as zip_ref:
        zip_ref.extractall(NGROK_FOLDER)

# Step 2: Kill any old ngrok processes
subprocess.run("taskkill /f /im ngrok.exe", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Step 3: Function to get the TCP URL from ngrok API
def get_tcp_url():
    try:
        r = requests.get("http://127.0.0.1:4040/api/tunnels")
        data = r.json()
        for tunnel in data.get("tunnels", []):
            if tunnel.get("proto") == "tcp":
                return tunnel.get("public_url")
    except Exception as e:
        print(f"[!] Error fetching ngrok URL: {e}")
    return None

# Step 4: Retry loop to get regional TCP URL
tcp_url = None
for attempt in range(1, MAX_RETRIES + 1):
    print(f"[*] Attempt {attempt} to start ngrok...")

    # Kill again just in case
    subprocess.run("taskkill /f /im ngrok.exe", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Start ngrok
    ngrok_proc = subprocess.Popen([NGROK_EXE, "tcp", PORT], stdout=subprocess.DEVNULL)
    time.sleep(WAIT_BETWEEN_RETRIES)

    tcp_url = get_tcp_url()

    if tcp_url and VALID_TCP_URL.match(tcp_url):
        print(f"[j] Found regional TCP URL: {tcp_url}")
        with open(SAVE_FILE, "w") as f:
            f.write(tcp_url)
        break
    else:
        print(f"[h] Invalid or no TCP URL: {tcp_url}")
        ngrok_proc.terminate()
        time.sleep(2)

if not tcp_url or not VALID_TCP_URL.match(tcp_url):
    print("[j] Failed to get valid regional ngrok TCP URL after retries.")
    exit(1)

print("[*] Keeping tunnel alive for 5 hours...")
time.sleep(18000)

print("[✔️] Done.")
