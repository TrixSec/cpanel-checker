import requests
import sys
import json
import time
import argparse
import threading
from concurrent.futures import ThreadPoolExecutor
from colorama import init, Fore, Style
from termcolor import colored 
import os

requests.urllib3.disable_warnings()
init(autoreset=True)

pause_event = threading.Event()
pause_event.set() 

def check_update():
    try:
        response = requests.get("https://raw.githubusercontent.com/TrixSec/cpanel-checker/main/VERSION")
        response.raise_for_status()
        latest_version = response.text.strip()

        if CPANEL_CHECKER_VERSION != latest_version:
            print(colored(f"[•] New version available: {latest_version}. Updating...", 'yellow'))
            os.system('git reset --hard HEAD')
            os.system('git pull')
            with open('VERSION', 'w') as version_file:
                version_file.write(latest_version)
            print(colored("[•] Update completed. Please rerun cpanel-checker.py.", 'green'))
            exit()

        print(colored(f"[•] You are using the latest version: {latest_version}.", 'green'))
    except requests.RequestException as e:
        print(colored(f"[×] Error fetching the latest version: {e}. Please check your internet connection.", 'red'))

CPANEL_CHECKER_VERSION = "1.0"

AUTHOR = "Trix Cyrus"

COPYRIGHT = "Copyright © 2024 Trixsec Org"

def print_banner():
    banner = r"""
░█▀▀░█▀█░█▀█░█▀█░█▀▀░█░░░░░█▀▀░█░█░█▀▀░█▀▀░█░█░█▀▀░█▀▄
░█░░░█▀▀░█▀█░█░█░█▀▀░█░░░░░█░░░█▀█░█▀▀░█░░░█▀▄░█▀▀░█▀▄
░▀▀▀░▀░░░▀░▀░▀░▀░▀▀▀░▀▀▀░░░▀▀▀░▀░▀░▀▀▀░▀▀▀░▀░▀░▀▀▀░▀░▀
    """
    print(colored(banner, 'cyan'))
    print(colored(f"cPanel Checker Version: {CPANEL_CHECKER_VERSION}", 'yellow'))
    print(colored(f"Made by {AUTHOR}", 'yellow'))
    print(colored(COPYRIGHT, 'yellow'))

def get_domain_count(url, username, password, output_file):
    """Fetches domain count for a given cPanel."""
    while not pause_event.is_set():
        time.sleep(0.1)  

    data_user_pass = {
        "user": username,
        "pass": password
    }
    s = requests.Session()
    try:
        resp = s.post(f"{url}/login/?login_only=1", data=data_user_pass, timeout=20, allow_redirects=True)
        login_resp = json.loads(resp.text)

        cpsess_token = login_resp["security_token"][7:]
        resp = s.post(
            f"{url}/cpsess{cpsess_token}/execute/DomainInfo/domains_data",
            data={"return_https_redirect_status": "1"}
        )
        domains_data = json.loads(resp.text)

        total_domain = 1 
        if domains_data["status"] == 1:
            total_domain += len(domains_data["data"].get("sub_domains", []))
            total_domain += len(domains_data["data"].get("addon_domains", []))

        print(Fore.GREEN + f"[SUCCESS LOGIN] --> {url}")
        with open(output_file, "a", encoding="utf-8") as success_log:
            success_log.write(f"{url}|{username}|{password}\n")

    except Exception:
        print(Fore.RED + f"[FAILED LOGIN] --> {url}")
    finally:
        s.close()
        time.sleep(0.05)

def handle_ctrl_c(signum, frame):
    """Handle CTRL+C and pause all threads."""
    global pause_event
    pause_event.clear()  
    print(Fore.YELLOW + "\nCTRL+C detected!")
    while True:
        choice = input(Fore.CYAN + Style.BRIGHT + "[e]xit or [r]esume? ").strip().lower()
        if choice == 'e':
            print(Fore.RED + "Exiting...")
            sys.exit(0)
        elif choice == 'r':
            print(Fore.GREEN + "Resuming...")
            pause_event.set() 
            break
        else:
            print(Fore.YELLOW + "Invalid choice. Please enter 'e' or 'r'.")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="cPanel Checker",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--file", required=True, help="Input file containing cPanel list.")
    parser.add_argument("-o", default=None, help="Output file to save results.")
    parser.add_argument("--threads", type=int, default=10, help="Number of threads to use.")
    parser.add_argument("--check-updates", action="store_true", help="Check for updates.")

    args = parser.parse_args()

    if args.check_updates:
        check_update()
        sys.exit(0)

    input_file = args.file
    output_file = args.o or f"{input_file}_success.txt"

    try:
        with open(input_file, 'r', encoding="utf-8") as f:
            urls = [line.strip().split('|') for line in f if '|' in line]
    except FileNotFoundError:
        print(Fore.RED + f"Error: File '{input_file}' not found.")
        sys.exit(1)

    print_banner()

    import signal
    signal.signal(signal.SIGINT, handle_ctrl_c)

    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        for url_info in urls:
            if len(url_info) == 3:
                url, username, password = url_info
                executor.submit(get_domain_count, url, username, password, output_file)
            else:
                print(Fore.YELLOW + f"Invalid format in input file: {url_info}")

if __name__ == "__main__":
    main()
