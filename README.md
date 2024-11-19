# cPanel Checker

A multi-threaded tool to check for cPanel accounts. This script allows you to quickly verify cPanel credentials 

## Features
- Multi-threaded processing for faster execution.
- Automatic login to cPanel accounts.
- Detailed logs for successful and failed attempts.
- Pause and resume functionality using `CTRL+C`.
- Color-coded output for better readability.
- Update checking capability.

---

## Prerequisites
- Python 3.6 or higher
- `colorama` library for colorful output
- `requests` library for HTTP requests

Install the required dependencies using:
```bash
pip install requests colorama
```

---

## Usage

### Command-Line Arguments
| Argument           | Description                                   | Required/Default          |
|--------------------|-----------------------------------------------|---------------------------|
| `--file`           | Input file containing cPanel credentials (Format: `url|username|password`). | **Required**              |
| `-o`               | Output file to save successful logins.        | Default: `<file>_success.txt` |
| `--threads`        | Number of threads to use for processing.      | Default: `10`             |
| `--check-updates`  | Check for script updates and exit.            | Optional                  |

### Input File Format
The input file should contain cPanel login details in the following format:
```
http://example.com:2082|username|password
https://secure.example.com:2083|admin|password123
```

### Running the Script
To start the script, use:
```bash
python cpanel-checker.py --file cpanel.txt -o results.txt --threads 20
```

- Replace `cpanel.txt` with your input file containing credentials.
- Use the `-o` flag to specify an output file. Default is `<input_file>_success.txt`.
- Adjust the `--threads` parameter to control concurrency.

### Pausing and Resuming
Press `CTRL+C` during execution to pause the script. You will be prompted to:
- Enter `e` to exit.
- Enter `r` to resume.

---

## Notes
- This tool suppresses SSL warnings for secure URLs.
- Make sure your input file is properly formatted (`url|username|password`).

---
