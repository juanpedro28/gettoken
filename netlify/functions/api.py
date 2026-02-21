import requests
import json
import sys

# Configuration
# This is the base URL for the Xiaomi Global Community
BASE_URL = "https://new-ams.c.mi.com/global"

def main():
    print("--- Xiaomi API Tool (Manual Token) ---")
    print("1. Go to your Netlify website.")
    print("2. Login and copy the 'new_bbs_serviceToken'.")
    
    # Allow passing token as command line argument or input
    if len(sys.argv) > 1:
        token = sys.argv[1]
    else:
        token = input("\nPaste Token Here: ").strip()

    if not token:
        print("[!] Error: No token provided.")
        return

    # Setup the session
    session = requests.Session()
    
    # Set the cookie manually using the token you pasted
    session.cookies.set("new_bbs_serviceToken", token, domain=".mi.com")
    
    # Mimic a browser to avoid being blocked
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
        "Origin": "https://new-ams.c.mi.com",
        "Referer": "https://new-ams.c.mi.com/global",
        "Accept": "application/json, text/plain, */*"
    })

    print("\n[*] Verifying token and connecting to API...")

    try:
        # Example: Get Login Info to verify the token works
        # You can add your own API logic here
        response = session.get(f"{BASE_URL}/api/user/getLoginInfo")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                user_name = data.get("data", {}).get("user_name", "Unknown")
                user_id = data.get("data", {}).get("user_id", "Unknown")
                print(f"[+] Success! Logged in as: {user_name} (ID: {user_id})")
                print("[+] The token is valid. You can now add your custom logic to this script.")
            else:
                print(f"[-] Token invalid or expired. API Message: {data.get('msg')}")
        else:
            print(f"[-] HTTP Request Failed: {response.status_code}")

    except Exception as e:
        print(f"[!] Error: {e}")

if __name__ == "__main__":
    main()
