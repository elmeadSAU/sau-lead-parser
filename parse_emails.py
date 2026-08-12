import email
from email import policy
import glob
import os
import re
from urllib.parse import parse_qs, urlparse
from bs4 import BeautifulSoup
import pandas as pd

def parse_eml_file(file_path):
    with open(file_path, "rb") as f:
        msg = email.message_from_binary_file(f, policy=policy.default)

    # Basic Email Metadata
    subject = msg.get("subject", "")
    date_sent = msg.get("date", "")

    # Get HTML body content
    body_html = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/html":
                body_html = part.get_content()
                break
            elif part.get_content_type() == "text/plain" and not body_html:
                body_html = part.get_content()
    else:
        body_html = msg.get_content()

    soup = BeautifulSoup(body_html, "html.parser")

    # Storage dictionary for lead details
    data = {
        "File Name": os.path.basename(file_path),
        "Subject": subject,
        "Date Sent": date_sent,
        "Name": "",
        "Email": "",
        "Cell Phone": "",
        "Receive Texts": "",
        "Birthdate": "",
        "Prospective Student Type": "",
        "Program of Interest": "",
        "Lead Source": "",
        "Parent Page URL": "",
        "GF Entry ID": "",
        "GF Lead ID": "",
    }

    # Extract tables or field labels from Gravity Forms template
    # Pattern matching labels in the HTML body
    labels = {
        "Name": "Name",
        "Email": "Email",
        "Cell Phone": "Cell Phone",
        "Receive texts?": "Receive Texts",
        "Birthdate": "Birthdate",
        "Prospective Student Type": "Prospective Student Type",
        "Program of Interest": "Program of Interest",
        "Lead Source": "Lead Source",
        "Parent Page URL": "Parent Page URL",
    }

    text_blocks = [text.strip() for text in soup.stripped_strings if text.strip()]
    
    for i, block in enumerate(text_blocks):
        for label, dict_key in labels.items():
            if block.lower() == label.lower() and i + 1 < len(text_blocks):
                data[dict_key] = text_blocks[i + 1]

    # Extract Gravity Forms ID parameters from links
    links = [a.get("href") for a in soup.find_all("a", href=True)]
    for link in links:
        if "gf_entries" in link:
            parsed = urlparse(link)
            params = parse_qs(parsed.query)
            data["GF Entry ID"] = params.get("id", [""])[0]
            data["GF Lead ID"] = params.get("lid", [""])[0]
            break

    return data

def main():
    eml_files = glob.glob("*.eml")
    if not eml_files:
        print("No .eml files found to process.")
        return

    print(f"Processing {len(eml_files)} emails...")
    records = [parse_eml_file(f) for f in eml_files]

    df = pd.DataFrame(records)
    output_filename = "parsed_leads.csv"
    df.to_csv(output_filename, index=False)
    print(f"Done! Successfully exported {len(df)} records to '{output_filename}'.")

if __name__ == "__main__":
    main()
