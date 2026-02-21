# Xiaomi Token Extractor

This tool helps you extract the `new_bbs_serviceToken` from the Xiaomi Community website and use it with a Python script.

## How to use

1. **Get the Token**:
   - Visit the Web Interface.
   - Follow the instructions to copy the extraction command.
   - Paste it into the browser console on the Xiaomi Community page.

2. **Run the Script**:
   - Download `api.py` from the website (Step 4).
   - Install the requirement:
     ```bash
     pip install requests
     ```
   - Run the script and paste your token:
     ```bash
     python api.py
     ```

## Deployment (GitHub Pages)

1. Upload `index.html` and `api.py` to your GitHub repository.
2. Go to **Settings** > **Pages**.
3. Under **Build and deployment**, set **Source** to `Deploy from a branch`.
4. Select **Branch**: `main` and **Folder**: `/ (root)`.
5. Click **Save**.
****
