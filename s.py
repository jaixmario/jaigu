import subprocess
import time
import requests
import zipfile
import os
import shutil

NGROK_URL = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip"
NGROK_ZIP = "ngrok.zip"
NGROK_FOLDER = "ngrok"
NGROK_EXE = os.path.join(NGROK_FOLDER, "ngrok.exe")
PORT = "3389"
SAVE_FILE = "ngrok_tcp_url.txt"
AUTH_TOKEN = os.environ.get("NGROK_AUTH_TOKEN")  # GitHub secret

# Download ngrok if not exists
if not os.path.exists(NGROK_EXE):
    print("[*] Downloading ngrok...")
    r = requests.get(NGROK_URL)
    with open(NGROK_ZIP, "wb") as f:
        f.write(r.content)

    print("[*] Extracting ngrok...")
    with zipfile.ZipFile(NGROK_ZIP, 'r') as zip_ref:
        zip_ref.extractall(NGROK_FOLDER)

# Authenticate ngrok
if AUTH_TOKEN:
    print("[*] Authenticating ngrok...")
    subprocess.run([NGROK_EXE, "authtoken", AUTH_TOKEN])
else:
    print("[!] NGROK_AUTH_TOKEN is not set!")
    exit(1)

# Start ngrok TCP tunnel
print("[*] Starting ngrok TCP tunnel...")
ngrok_proc = subprocess.Popen([NGROK_EXE, "tcp", PORT], stdout=subprocess.DEVNULL)

# Give ngrok some time to initialize
time.sleep(5)

# Get public TCP URL
def get_tcp_url():
    try:
        r = requests.get("http://127.0.0.1:4040/api/tunnels")
        data = r.json()
        for tunnel in data.get("tunnels", []):
            if tunnel.get("proto") == "tcp":
                return tunnel.get("public_url")
    except Exception as e:
        print(f"[!] Error: {e}")
    return None

tcp_url = get_tcp_url()
if tcp_url:
    print(f"[ok] ngrok TCP URL: {tcp_url}")
    with open(SAVE_FILE, "w") as f:
        f.write(tcp_url)
else:
    print("[no] Could not fetch ngrok TCP URL")

print("[*] Keeping tunnel alive for 5 hours...")
time.sleep(18000)

print("[✔️] Done.")
