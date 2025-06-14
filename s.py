import subprocess
import time
import requests
import json
import os
import signal

DESIRED_SUFFIX = ".tcp.us-cal-1.ngrok.io"

def start_ngrok():
    return subprocess.Popen(["ngrok", "tcp", "3389"], stdout=subprocess.DEVNULL)

def stop_ngrok(proc):
    try:
        proc.send_signal(signal.SIGINT)
        proc.wait()
    except Exception:
        proc.kill()

def get_tcp_url():
    try:
        response = requests.get("http://localhost:4040/api/tunnels")
        tunnels = response.json().get("tunnels", [])
        for tunnel in tunnels:
            if tunnel["proto"] == "tcp":
                return tunnel["public_url"]
    except:
        pass
    return None

while True:
    print("[*] Starting ngrok...")
    ngrok_proc = start_ngrok()
    time.sleep(5)

    print("[*] Checking ngrok tunnel URL...")
    url = get_tcp_url()
    if url:
        print(f"[!] URL assigned: {url}")
        domain = url.replace("tcp://", "").split(":")[0]
        if domain.endswith(DESIRED_SUFFIX):
            print(f"[✅] Matched desired region: {url}")
            break
        else:
            print(f"[❌] Not a us-cal domain, retrying...")
    else:
        print("[❌] No tunnel found, retrying...")

    stop_ngrok(ngrok_proc)
    time.sleep(2)
