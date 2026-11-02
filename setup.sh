#!/data/data/com.termux/files/usr/bin/sh
echo "[*] WEAREBLANK: Initializing environment and installing Python..."
pkg update -y && pkg install python -y

echo "[*] Requesting storage permissions..."
termux-setup-storage

echo "[*] Moving automation scripts to secure execution paths..."
cp /sdcard/Download/codm_checker.py ~/codm_checker.py
mkdir -p ~/.termux/boot/
cp /sdcard/Download/codm_boot.sh ~/.termux/boot/codm_boot.sh
chmod +x ~/.termux/boot/codm_boot.sh

echo "=================================================="
echo " [+] SETUP COMPLETE! All systems operational."
echo "=================================================="