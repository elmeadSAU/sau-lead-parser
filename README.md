# Email Lead Parser & AI Analytics Dashboard

A Python pipeline and interactive Streamlit web app for parsing .eml lead files generated from WordPress / Gravity Forms and analyzing graduate prospective student data using Google AI Studio (Gemini 2.5 Flash).

## Key Features

- Automated .eml Parsing: Extracts structured fields into parsed_leads.csv.
- Interactive Streamlit Dashboard: Displays real-time metrics, program distribution charts, and lead source breakdowns.
- AI Analysis with Google AI Studio: Integrated with google-genai (Gemini 2.5 Flash) to generate executive summaries and answer custom analytics queries.

## Setup & Local Execution

1. Clone & install dependencies:
   pip install -r requirements.txt

2. Run the Email Parser:
   python3 parse_emails.py

3. Launch the Streamlit Analytics Dashboard:
   export GEMINI_API_KEY="your_api_key_here"
   streamlit run app.py

## Tech Stack

- Data Processing: Python 3, Pandas, BeautifulSoup4
- Dashboard Interface: Streamlit, Plotly Express
- AI Engine: Google AI Studio SDK (google-genai), Gemini 2.5 Flash
