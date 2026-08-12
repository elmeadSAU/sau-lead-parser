import os
import glob
import re
from bs4 import BeautifulSoup
from email import message_from_file
from urllib.parse import urlparse, parse_qs
import pandas as pd

def extract_channel(url, raw_source):
    if isinstance(url, str) and url.strip():
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        if 'utm_source' in params:
            return params['utm_source'][0].capitalize()
        if 'utm_medium' in params:
            return params['utm_medium'][0].capitalize()
        if 'gclid' in params:
            return "Google Ads"
        if 'fbclid' in params:
            return "Facebook Ads"
            
    if isinstance(raw_source, str) and raw_source.strip():
        return raw_source.strip()
        
    return "SAU Web Form"

def parse_eml_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        msg = message_from_file(f)
    
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/html":
                body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                break
            elif part.get_content_type() == "text/plain" and not body:
                body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
    else:
        body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')

    soup = BeautifulSoup(body, 'html.parser')
    text = soup.get_text()

    def get_field(label):
        pattern = rf"{label}:\s*(.*)"
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1).strip() if match else ""

    parent_url = get_field("Parent Page URL") or get_field("URL")
    raw_lead_source = get_field("Lead Source")

    data = {
        "File Name": os.path.basename(filepath),
        "Subject": msg.get("Subject", ""),
        "Date": msg.get("Date", ""),
        "Student Name": get_field("Name") or get_field("Student Name"),
        "Email Address": get_field("Email") or get_field("Email Address"),
        "Cell Phone": get_field("Phone") or get_field("Cell Phone"),
        "Program of Interest": get_field("Program of Interest") or get_field("Program") or "Unspecified Program",
        "Lead Source": extract_channel(parent_url, raw_lead_source),
        "Parent Page URL": parent_url,
        "Gravity Forms Entry ID": get_field("Entry ID") or get_field("id"),
        "Gravity Forms Lead ID": get_field("Lead ID") or get_field("lid"),
    }
    return data

def main():
    eml_files = glob.glob("*.eml")
    if not eml_files:
        print("No .eml files found in current directory.")
        return

    records = [parse_eml_file(f) for f in eml_files]
    df = pd.DataFrame(records)
    df.to_csv("parsed_leads.csv", index=False)
    print(f"Successfully processed {len(records)} .eml files into parsed_leads.csv")

if __name__ == "__main__":
    main()
