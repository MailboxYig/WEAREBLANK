import os
import zipfile
import subprocess
import glob
import shutil

# ====================================================================
# CONFIGURATION: Direct XAPK download link
# ====================================================================
XAPK_URL = "https://d.apkpure.com/b/XAPK/com.activision.callofduty.shooter?versionCode=17048&nc=arm64-v8a&sv=24"

# Exact components required for deployment (ignores all other language/arch bloat)
TARGET_COMPONENTS = [
    "com.activision.callofduty.shooter",
    "config.arm64_v8a",
    "AssetPackMain",
    "AssetPackPatch1",
    "AssetPackAudioLQ",
    "AssetPackVideo",
    "AssetPackConfig"
]

def download_file(url, dest_path):
    print("[+] Connecting to download source via Windows curl...")
    cmd = [
        "curl.exe",
        "-L",                     # Follow redirects
        "-k",                     # Bypass SSL checks
        "-#",                     # Show clean progress bar
        "-A", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "-H", "Referer: https://apkpure.com/",
        url,
        "-o", dest_path
    ]
    
    result = subprocess.run(cmd)
    if result.returncode != 0:
        raise Exception(f"curl download failed with exit code {result.returncode}")
    print("\n[+] Download complete!")

def main():
    print("====================================================================")
    print("  WEAREBLANK - CODM XAPK Filtered Multi-Installer")
    print("====================================================================")
    
    # 1. Check for local XAPK, use top config URL, or prompt if blank
    xapk_files = glob.glob("*.xapk")
    if xapk_files:
        xapk_path = xapk_files[0]
        print(f"[+] Found existing local XAPK package: {xapk_path}")
    else:
        url = XAPK_URL
        if not url or url == "PASTE_YOUR_DIRECT_LINK_HERE":
            url = input("[?] Paste your direct XAPK download link: ").strip()
            
        if not url:
            print("[!] No URL provided. Exiting.")
            return
        
        xapk_path = "codm_downloaded.xapk"
        try:
            download_file(url, xapk_path)
        except Exception as e:
            print(f"\n[!] Download failed: {e}")
            input("Press Enter to exit...")
            return

    extract_dir = "temp_xapk_extracted"
    if os.path.exists(extract_dir):
        shutil.rmtree(extract_dir)
    os.makedirs(extract_dir, exist_ok=True)

    # 2. Unpack XAPK container
    print("[+] Unpacking XAPK container...")
    with zipfile.ZipFile(xapk_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)

    # 3. Filter and gather ONLY the required APK components
    print("[+] Filtering for required CODM components...")
    all_apks = glob.glob(os.path.join(extract_dir, "**", "*.apk"), recursive=True)
    
    apk_files = []
    for apk in all_apks:
        filename = os.path.basename(apk)
        # Check if the filename matches our target list
        if any(target in filename for target in TARGET_COMPONENTS):
            # If it's a config split, ensure it's specifically arm64_v8a and discard other arch/dpi splits
            if "config." in filename and "arm64_v8a" not in filename:
                continue
            apk_files.append(apk)

    if not apk_files:
        print("[!] Error: None of the required CODM components were found in the package.")
        shutil.rmtree(extract_dir, ignore_errors=True)
        return

    print(f"[+] Located {len(apk_files)} required components for installation:")
    for apk in apk_files:
        print(f"    - {os.path.basename(apk)}")

    # 4. Push via ADB multi-install
    print("\n[+] Waiting for Meta Quest connection via ADB...")
    subprocess.run(["adb", "wait-for-device"])
    print("[+] Device connected. Executing atomic multi-APK installation...")

    cmd = ["adb", "install-multiple"] + apk_files
    result = subprocess.run(cmd)

    if result.returncode == 0:
        print("\n[+] Base app, arm64 config, and all required asset packs installed successfully!")
    else:
        print("\n[!] Installation encountered an issue. Check ADB status.")

    # 5. Cleanup temp files
    print("[+] Cleaning up temporary workspace files...")
    shutil.rmtree(extract_dir, ignore_errors=True)
    
    print("====================================================================")
    print("  DEPLOYMENT COMPLETE!")
    print("====================================================================")
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()