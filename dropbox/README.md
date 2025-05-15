# Wealth Management Customer Data Generator

This script generates sample customer data for a wealth management company and uploads it to Dropbox. For each customer, it creates:
- A folder with the customer's name
- A PDF document with customer information
- An Excel file with sample investment portfolio data
- A PDF document with sample meeting notes

## Prerequisites

- Python 3.7 or higher
- A Dropbox account and API key

## Setup

1. Install the required packages:
```bash
pip install -r requirements.txt
```

2. Set your Dropbox API key as an environment variable:
```bash
export DROPBOX_API_KEY='your_api_key_here'
```

## Usage

Run the script:
```bash
python wealth_management_data.py
```

The script will:
1. Connect to Dropbox using your API key
2. Generate sample data for 5 customers
3. Create PDFs and Excel files for each customer
4. Upload everything to your Dropbox account

## Output Structure

For each customer, the following structure will be created in your Dropbox:

```
/Customer Name/
    ├── Customer Name_info.pdf
    ├── Customer Name_portfolio.xlsx
    └── Customer Name_notes.pdf
```

## Customization

You can modify the following in the script:
- Number of customers (default: 5)
- Sample data (cities, industries, job titles, etc.)
- File formats and content
- Folder structure 