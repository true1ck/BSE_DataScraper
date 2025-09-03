import os
import requests
import pandas as pd
from flask import Flask, render_template, jsonify
import json
from datetime import datetime

app = Flask(__name__)

# File to store previous company names
PREVIOUS_COMPANIES_FILE = 'previous_companies.json'

def load_previous_companies():
    """Load previous company data from a JSON file."""
    if os.path.exists(PREVIOUS_COMPANIES_FILE):
        with open(PREVIOUS_COMPANIES_FILE, 'r') as f:
            return set(json.load(f))
    return set()

def save_current_companies(companies):
    """Save current company data to a JSON file."""
    with open(PREVIOUS_COMPANIES_FILE, 'w') as f:
        json.dump(list(companies), f)

def fetch_company_updates():
    """Fetch company updates from BSE API with pagination."""
    today = datetime.now().strftime('%Y%m%d')
    
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9",
        "origin": "https://www.bseindia.com",
        "referer": "https://www.bseindia.com/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
    }

    all_data = []
    page = 1

    while True:
        params = {
            "pageno": str(page),
            "strCat": "Company Update",
            "strPrevDate": today,
            "strScrip": "",
            "strSearch": "P",
            "strToDate": today,
            "strType": "C",
            "subcategory": "Award of Order / Receipt of Order"
        }

        response = requests.get(
            "https://api.bseindia.com/BseIndiaAPI/api/AnnSubCategoryGetData/w",
            headers=headers,
            params=params
        )

        if response.status_code != 200:
            break

        json_data = response.json().get("Table", [])
        if not json_data:
            break

        all_data.extend(json_data)
        page += 1

    return all_data

@app.route('/')
def home():
    """Render the main page with the initial data."""
    data = fetch_company_updates()
    current_companies = {item['SLONGNAME'] for item in data if item.get('SLONGNAME')}
    save_current_companies(current_companies)

    if not data:
        return render_template('index.html', tables="<p>No updates found today.</p>")

    # Create a DataFrame and format the table
    df = pd.DataFrame(data)[['SLONGNAME', 'NEWSSUB', 'NEWS_DT', 'NSURL']]
    df.columns = ['Company Name', 'Announcement', 'Date', 'URL']

    # Format the date and URL for display
    df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d %H:%M:%S')
    df['URL'] = df['URL'].apply(lambda x: f'<a href="{x}" target="_blank">URL</a>')

    # Convert DataFrame to HTML
    table_html = df.to_html(classes='data', index=False, escape=False)

    return render_template('index.html', tables=table_html)

@app.route('/updates')
def updates():
    """Return updated company data as JSON."""
    data = fetch_company_updates()
    current_companies = {item['SLONGNAME'] for item in data if item.get('SLONGNAME')}
    previous_companies = load_previous_companies()

    new_companies = current_companies - previous_companies

    # Save current companies
    save_current_companies(current_companies)

    return jsonify({
        'new_companies': list(new_companies),
        'data': data
    })

if __name__ == '__main__':
    app.run(debug=True)
