from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import platform

app = FastAPI()

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def scan_networks():
    system_platform = platform.system().lower()
    if "windows" in system_platform:
        command = ["netsh", "wlan", "show", "network", "mode=bssid"]
    elif "linux" in system_platform:
        command = ["nmcli", "-t", "-f", "SSID", "dev", "wifi"]
    else:
        return []

    try:
        output = subprocess.check_output(command, universal_newlines=True, stderr=subprocess.DEVNULL)
        return output.splitlines()
    except:
        return []

def parse_networks(lines):
    ssids = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if "windows" in platform.system().lower():
            if line.lower().startswith("ssid"):
                parts = line.split(":")
                if len(parts) > 1:
                    ssid = parts[-1].strip()
                    if ssid:
                        ssids.append(ssid)
        else:
            ssids.append(line)
    return ssids

def find_duplicates(ssids):
    ssid_count = {}
    duplicates = []
    for ssid in ssids:
        ssid_count[ssid] = ssid_count.get(ssid, 0) + 1
    for ssid, count in ssid_count.items():
        if count > 1:
            duplicates.append({"SSID": ssid, "Count": count})
    return duplicates

@app.get("/networks")
def get_networks():
    raw = scan_networks()
    ssids = parse_networks(raw)
    duplicates = find_duplicates(ssids)
    return {"networks": ssids, "duplicates": duplicates}
