import os
import json
import subprocess
import re
import urllib.request
from datetime import datetime

STATE_FILE = os.path.expanduser("~/.codm_update_state.json")
PACKAGE_NAME = "com.activision.callofduty.shooter"
DOWNLOAD_DIR = "/sdcard/Download/"

def get_installed_version():
    """Queries the local Android package manager for CODM's version string."""
    try:
        output = subprocess.check_output(["dumpsys", "package", PACKAGE_NAME], text=True)
        for line in output.splitlines():
            if "versionName=" in line:
                return line.strip().split("=")[1].split()[0]
    except Exception as e:
        print(f"[!] Error querying package manager: {e}")
    return None

def fetch_latest_metadata():
    """Scrapes APKPure's public app page to check the latest available version."""
    apkpure_url = f"https://apkpure.com/call-of-duty-mobile-game/com.activision.callofduty.shooter/download"
    metadata = {"version": None, "download_url": apkpure_url}
    try:
        req = urllib.request.Request(
            apkpure_url, 
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode("utf-8")
            
            ver_match = re.search(r'itemprop="softwareVersion"[^>]*>([^<]+)<', html)
            if ver_match:
                metadata["version"] = ver_match.group(1).strip()
            else:
                alt_match = re.search(r'/call-of-duty-mobile-game/com\.activision\.callofduty\.shooter/download/([0-9.]+)', html)
                if alt_match:
                    metadata["version"] = alt_match.group(1).strip()
                    
    except Exception as e:
        print(f"[!] Error fetching metadata from APKPure: {e}")
        
    return metadata

def install_split_apks(apk_folder="/sdcard/Download/codm_update/"):
    """
    Installs a directory of split/asset APKs atomically using 
    Android's package installer session API from within Termux.
    """
    if not os.path.exists(apk_folder):
        return False
        
    apk_files = [f for f in os.listdir(apk_folder) if f.endswith(".apk")]
    if not apk_files:
        return False

    print(f"[*] Creating installation session for {len(apk_files)} split/asset packages...")
    try:
        session_create = subprocess.run(
            ["pm", "install-create", "-i", "com.termux", "--user", "0"],
            text=True, captureoutput=True, check=True
        )
        match = re.search(r'\[(\d+)\]', session_create.stdout)
        if not match:
            return False
        session_id = match.group(1)

        for apk in apk_files:
            apk_path = os.path.join(apk_folder, apk)
            file_size = os.path.getsize(apk_path)
            write_cmd = f"pm install-write -S {file_size} {session_id} {apk} {apk_path}"
            subprocess.run(write_cmd, shell=True, check=True)

        commit_res = subprocess.run(
            ["pm", "install-commit", session_id],
            text=True, captureoutput=True
        )
        return "Success" in commit_res.stdout
    except Exception as e:
        print(f"[!] Split installation exception: {e}")
        return False

def run_update_check(force=False):
    print("[*] WEAREBLANK: Checking CODM version parity...")
    today = datetime.now().strftime("%Y-%m-%d")
    
    state = {}
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            try:
                state = json.load(f)
            except json.JSONDecodeError:
                pass

    if not force and state.get("last_checked_date") == today:
        print("[*] Already checked today. Skipping.")
        return

    installed = get_installed_version()
    remote = fetch_latest_metadata()
    
    print(f"[*] Installed Version : {installed}")
    print(f"[*] Latest Available  : {remote.get('version', 'Unknown')}")

    state["last_checked_date"] = today
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

    if installed and remote.get("version") and installed != remote["version"]:
        print("[+] New CODM version detected! Checking for staged update bundle...")
        if not install_split_apks():
            os.system(f"am start -a android.intent.action.VIEW -d {remote['download_url']}")
    else:
        print("[+] CODM is fully up to date.")

if __name__ == "__main__":
    import sys
    force_check = "--force" in sys.argv
    run_update_check(force=force_check)