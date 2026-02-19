import os
import sys

# Add the project root to sys.path to allow importing from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from imap_tools import MailBox
from src.config import EMAIL_USER, EMAIL_PASS

print("Attempting login...")
try:
    with MailBox('imap.gmail.com').login(EMAIL_USER, EMAIL_PASS) as mailbox:
        print("Logged in.")
        print(f"Dir of mailbox: {dir(mailbox)}")
        if hasattr(mailbox, 'idle'):
            print("Trying idle.wait(timeout=5)...")
            # idle.wait() returns a list of responses
            responses = mailbox.idle.wait(timeout=5)
            print(f"Responses: {responses}")
        else:
            print("mailbox.idle does not exist")
except Exception as e:
    print(f"Login failed (expected if creds invalid): {e}")
