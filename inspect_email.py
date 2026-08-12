import email
from email import policy
import glob
import re
from urllib.parse import parse_qs, urlparse

eml_files = glob.glob("*.eml")

if not eml_files:
    print("No .eml files found!")
else:
    sample_file = eml_files[0]
    print(f"--- INSPECTING FILE: {sample_file} ---\n")
    
    with open(sample_file, "rb") as f:
        msg = email.message_from_binary_file(f, policy=policy.default)
    
    print("Subject:", msg["subject"])
    print("From:", msg["from"])
    print("Date:", msg["date"])
    print("-" * 40)

    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() in ["text/plain", "text/html"]:
                body += part.get_content()
    else:
        body = msg.get_content()

    print("\n--- ALL LINKS FOUND IN BODY ---")
    links = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', body)
    
    if not links:
        print("No URLs found in the body.")
    else:
        for url in set(links):
            print("\nURL:", url)
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            if params:
                print("  -> Query Parameters (UTMs):", params)
            else:
                print("  -> No query parameters attached to this link.")

