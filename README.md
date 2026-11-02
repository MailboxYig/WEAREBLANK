# WEAREBLANK - CODM Auto-Updater Setup Guide

Welcome! This tool automates your Call of Duty: Mobile (CODM) updates on your Meta Quest headset so you never have to worry about manual file transfers or reconnecting to a PC again.

---

## What You Need Before You Start
* Your Meta Quest headset and a USB-C cable.
* **USB Debugging** enabled inside your Meta Quest headset developer settings.

---

## Step-by-Step Instructions

### Step 1: Download the Toolkit
1. Go to this repository's main page.
2. Click the green **`<> Code`** button near the top right.
3. Select **Download ZIP**.
4. Once downloaded, **extract/unzip** the folder completely onto your Windows PC desktop.

### Step 2: Connect Your Headset
1. Plug your Meta Quest into your PC using the USB-C cable.
2. Put on your headset and select **"Allow"** or **"Grant"** when prompted to **Allow USB Debugging**.

### Step 3: Run the Installer on Your PC
1. Open the extracted folder on your PC.
2. Double-click the file named **`install.bat`**.
   * *(Note: If ADB is missing from your PC, the script will automatically install it securely to your hard drive).*
3. Watch the terminal window as it sideloads Termux, Termux:Boot, and pushes the automation scripts to your headset.

### Step 4: Finalize Setup Inside Your Headset
1. Put on your Meta Quest headset. Termux should open automatically. 
2. Inside the Termux terminal, type this exact command and press **Enter**:
   ```sh
   sh /sdcard/Download/setup.sh