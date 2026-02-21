import subprocess
import sys
import time
import webbrowser

required_packages = ["browser-cookie3", "selenium", "pyperclip", "tkinter"]
for package in required_packages:
    try:
        __import__(package.replace("-", "_"))
    except ImportError:
        print(f"[!] Installing missing package: {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

import browser_cookie3
import pyperclip
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
import tkinter as tk
from tkinter import ttk, messagebox
import threading

CHROME_LINK = "https://new-ams.c.mi.com/global"


def extract_firefox_token():
    """Extracts token from Firefox cookies."""
    try:
        # Close Firefox to ensure cookies are written to disk
        if sys.platform == "win32":
            subprocess.run(["taskkill", "/F", "/IM", "firefox.exe"], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            subprocess.run(["killall", "-9", "firefox"], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(2)  # Give it a moment
    except Exception as e:
        print(f"[!] Could not close Firefox automatically: {e}")

    try:
        cj = browser_cookie3.firefox(domain_name='mi.com')
        for cookie in cj:
            if "new_bbs_serviceToken" in cookie.name:
                return cookie.value
    except Exception as e:
        print(f"[!] Failed to load Firefox cookies: {e}")
        messagebox.showerror("Error", f"Failed to load Firefox cookies:\n{e}")
    return None

def extract_chrome_token():
    """Opens Chrome for login and automatically extracts the token."""
    token = None
    driver = None
    try:
        chrome_options = Options()
        chrome_options.add_argument("--app=" + CHROME_LINK)
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(CHROME_LINK)
        
        while True:
            try:
                if not driver.window_handles:
                    break
                
                cookies = driver.get_cookies()
                for cookie in cookies:
                    if cookie['name'] == 'new_bbs_serviceToken':
                        token = cookie['value']
                        break
            except Exception:
                break
            
            if token:
                break
            time.sleep(0.5)
            
    except WebDriverException as e:
        print(f"[!] WebDriver error: {e}")
        messagebox.showerror("WebDriver Error", "Could not start Chrome. Is chromedriver installed and in your PATH?\n\n" + str(e))
    except Exception as e:
        print(f"[!] Error executing script in Chrome: {e}")
        messagebox.showerror("Error", f"An error occurred in Chrome:\n{e}")
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass
    
    return token

class TokenExtractorGUI:
    def __init__(self, master):
        self.master = master
        master.title("Token Extractor")
        master.geometry("450x200")
        master.resizable(False, False)
        
        self.style = ttk.Style()
        self.style.theme_use('clam')

        self.main_frame = ttk.Frame(master, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(self.main_frame, text="Choose your browser to extract the token:").pack(pady=5, anchor='w')

        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(pady=10, fill=tk.X, expand=True)

        self.firefox_button = ttk.Button(self.button_frame, text="Get from Firefox", command=self.get_firefox_token)
        self.firefox_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        self.chrome_button = ttk.Button(self.button_frame, text="Login & Get Token", command=self.get_chrome_token)
        self.chrome_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        self.token_frame = ttk.Frame(self.main_frame)
        self.token_frame.pack(pady=5, fill=tk.X)
        
        ttk.Label(self.token_frame, text="Token:").pack(side=tk.LEFT)
        self.token_var = tk.StringVar()
        self.token_entry = ttk.Entry(self.token_frame, textvariable=self.token_var, state='readonly', width=40)
        self.token_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        self.copy_button = ttk.Button(self.token_frame, text="Copy", command=self.copy_token, state=tk.DISABLED)
        self.copy_button.pack(side=tk.LEFT)
        
        self.status_var = tk.StringVar()
        self.status_label = ttk.Label(self.main_frame, textvariable=self.status_var)
        self.status_label.pack(pady=5, anchor='w')

    def run_in_thread(self, target_func):
        self.firefox_button.config(state=tk.DISABLED)
        self.chrome_button.config(state=tk.DISABLED)
        self.status_var.set("Working...")
        
        thread = threading.Thread(target=self.run_and_update, args=(target_func,))
        thread.daemon = True
        thread.start()

    def run_and_update(self, target_func):
        token = target_func()
        
        self.master.after(0, self.update_gui_with_token, token)

    def update_gui_with_token(self, token):
        self.firefox_button.config(state=tk.NORMAL)
        self.chrome_button.config(state=tk.NORMAL)
        if token:
            self.token_var.set(token)
            self.copy_button.config(state=tk.NORMAL)
            self.status_var.set("Token found and ready to be copied!")
            self.copy_token() # auto-copy
            messagebox.showinfo("Success", "Token found and copied to clipboard!")
        else:
            self.token_var.set("")
            self.copy_button.config(state=tk.DISABLED)
            self.status_var.set("Token not found. Please make sure you are logged in.")
            messagebox.showwarning("Not Found", "Could not find the token. Please make sure you are logged in on mi.com.")

    def get_firefox_token(self):
        if not messagebox.askokcancel("Firefox Login", "Please make sure you are logged into https://c.mi.com/global on Firefox.\n\nThis script will need to close Firefox to read the cookies. Press OK to continue."):
            return
        self.run_in_thread(extract_firefox_token)

    def get_chrome_token(self):
        self.run_in_thread(extract_chrome_token)

    def copy_token(self):
        token = self.token_var.get()
        if token:
            pyperclip.copy(token)
            self.status_var.set("Token copied to clipboard!")

if __name__ == "__main__":
    print("GetTokens V3 - by byBestix on xdaforums, modified by Gemini")
    root = tk.Tk()
    app = TokenExtractorGUI(root)
    root.mainloop()
