
import os
import sys
import sqlite3
import subprocess
import time
import requests

# Load config safely
sys.path.append(os.getcwd())
try:
    from config.config import BOT_TOKEN, DATABASE_NAME
except ImportError:
    BOT_TOKEN = "8136137840:AAF7_Wf9KU2epPkGKdsijfdx6zIwNzPVfc8" # From config view
    DATABASE_NAME = "education_system.db"

def kill_python_processes():
    print("Killing all python.exe processes related to the bot...")
    try:
        # Get all python processes
        output = subprocess.check_output('wmic process where "name=\'python.exe\'" get ProcessId,CommandLine', shell=True).decode()
        for line in output.splitlines():
            if 'main.py' in line or 'sync_translations.py' in line or 'test_import.py' in line:
                pid = line.strip().split()[-1]
                print(f"Terminating PID {pid}...")
                subprocess.run(f'taskkill /F /PID {pid}', shell=True)
    except Exception as e:
        print(f"Error killing processes: {e}")

def clear_webhook():
    print("Clearing Telegram webhook and dropping pending updates...")
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook?drop_pending_updates=true"
    try:
        resp = requests.get(url, timeout=10)
        print(f"Response: {resp.json()}")
    except Exception as e:
        print(f"Error clearing webhook: {e}")

def cleanup_lock_files():
    print("Cleaning up potential lock files...")
    for f in ["bot.lock", "temp.lock"]:
        if os.path.exists(f):
            os.remove(f)
            print(f"Removed {f}")

def check_for_hidden_services():
    print("Checking for common process managers...")
    try:
        subprocess.run('pm2 list', shell=True)
        # If pm2 exists, suggest stopping it
        print("Note: If you use PM2, make sure to 'pm2 stop all' or 'pm2 delete all'")
    except:
        pass

if __name__ == "__main__":
    kill_python_processes()
    clear_webhook()
    cleanup_lock_files()
    check_for_hidden_services()
    print("\n--- HARD RESET COMPLETE ---")
    print("Try starting the bot now: python main.py")
