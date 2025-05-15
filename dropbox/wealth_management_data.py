import os
import dropbox
from dropbox.exceptions import AuthError
from datetime import datetime, timedelta
import random
import pandas as pd
from fpdf import FPDF
import tempfile
import uuid

def get_dropbox_token():
    token_file = 'token.txt'
    
    # Check if token file exists
    if os.path.exists(token_file):
        with open(token_file, 'r') as f:
            token = f.read().strip()
            if token:
                return token
    
    # If no token found, prompt user
    print("\nDropbox Access Token not found.")
    print("Please follow these steps:")
    print("1. Create a file named 'token.txt' in the current directory")
    print("2. Paste your Dropbox access token into this file")
    print("3. Save the file")
    print("4. Press Enter to continue...")
    
    input()  # Wait for user to press Enter
    
    # Check if token file was created
    if os.path.exists(token_file):
        with open(token_file, 'r') as f:
            token = f.read().strip()
            if token:
                return token
    
    print("Error: token.txt file not found or empty. Please try again.")
    return None

def get_root_folder(dbx):
    while True:
        root_folder = input("\nEnter the root folder name for customer data (default: 'Wealth Management'): ").strip()
        if not root_folder:
            root_folder = "Wealth Management"
            print(f"Using default folder: {root_folder}")
            
        # Remove leading slash if present
        root_folder = root_folder.lstrip('/')
        
        try:
            # Check if folder exists
            try:
                dbx.files_get_metadata(f"/{root_folder}")
                print(f"Using existing folder: {root_folder}")
            except dropbox.exceptions.ApiError as e:
                if e.error.is_path() and e.error.get_path().is_not_found():
                    # Create the folder if it doesn't exist
                    print(f"Creating new folder: {root_folder}")
                    dbx.files_create_folder(f"/{root_folder}")
                else:
                    raise
            
            return root_folder
        except Exception as e:
            print(f"Error accessing Dropbox folder: {e}")
            print("Please try again.")

# Sample data for generating customer information
CITIES = ["Miami, FL", "Orlando, FL", "Tampa, FL", "Jacksonville, FL", "Fort Lauderdale, FL", "St. Petersburg, FL", "Naples, FL", "Sarasota, FL"]
INDUSTRIES = ["Retired - Technology", "Retired - Finance", "Retired - Healthcare", "Retired - Manufacturing", "Retired - Education", "Retired - Government", "Retired - Military", "Retired - Business"]
JOB_TITLES = ["Retired", "Retired Executive", "Retired Professional", "Retired Educator", "Retired Military Officer", "Retired Business Owner", "Retired Healthcare Professional", "Retired Government Official"]
ACCOUNT_MANAGERS = ["John Smith", "Sarah Johnson", "Michael Brown", "Emily Davis", "David Wilson", "Lisa Anderson"]

# Additional data for more variety
FIRST_NAMES = [
    "James", "Emma", "William", "Olivia", "Benjamin", "Sophia", "Lucas", "Ava",
    "Henry", "Isabella", "Alexander", "Mia", "Sebastian", "Charlotte", "Jack", "Amelia",
    "Owen", "Harper", "Gabriel", "Evelyn", "Matthew", "Abigail", "Leo", "Elizabeth",
    "Nathan", "Sofia", "Isaac", "Avery", "Jayden", "Ella", "Anthony", "Scarlett",
    "Dylan", "Grace", "Andrew", "Victoria", "Joshua", "Riley", "Christopher", "Aria",
    "Theodore", "Lily", "Caleb", "Aubrey", "Ryan", "Zoey", "Asher", "Penelope",
    "Nathaniel", "Lillian", "Thomas", "Addison", "Leo", "Layla", "Isaiah", "Natalie",
    "Charles", "Camila", "Josiah", "Chloe", "Hudson", "Samantha", "Christian", "Stella",
    "Hunter", "Violet", "Connor", "Rebecca", "Eli", "Audrey", "Ezra", "Savannah",
    "Aaron", "Allison", "Landon", "Anna", "Adrian", "Ariana", "Jonathan", "Alice",
    "Nolan", "Hailey", "Jeremiah", "Gabriella", "Easton", "Sadie", "Elias", "Arianna",
    "Colton", "Paisley", "Cameron", "Skylar", "Carson", "Nora", "Robert", "Sarah",
    "Angel", "Claire", "Maverick", "Quinn", "Nicholas", "Lucy", "Dominic", "Elena"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas",
    "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White",
    "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young",
    "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
    "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
    "Carter", "Roberts", "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker",
    "Cruz", "Edwards", "Collins", "Reed", "Stewart", "Morris", "Morales", "Murphy",
    "Cook", "Rogers", "Morgan", "Peterson", "Cooper", "Reed", "Bailey", "Bell",
    "Gomez", "Kelly", "Howard", "Ward", "Cox", "Diaz", "Richardson", "Wood",
    "Watson", "Brooks", "Bennett", "Gray", "James", "Reyes", "Cruz", "Hughes",
    "Price", "Myers", "Long", "Foster", "Sanders", "Ross", "Morales", "Powell",
    "Sullivan", "Russell", "Ortiz", "Jenkins", "Gutierrez", "Perry", "Butler", "Barnes"
]

INDUSTRY_PREFIXES = ["Retired -", "Former", "Ex-"]
INDUSTRY_TYPES = [
    "Technology", "Finance", "Healthcare", "Manufacturing", "Education", "Government", "Military", "Business",
    "Engineering", "Science", "Law", "Media", "Construction", "Transportation", "Energy", "Agriculture",
    "Retail", "Hospitality", "Entertainment", "Telecommunications", "Real Estate", "Insurance", "Consulting",
    "Marketing", "Research", "Architecture", "Pharmaceuticals", "Non-Profit", "Utilities", "Automotive"
]

JOB_PREFIXES = ["Retired", "Former", "Ex-"]
JOB_TYPES = [
    "Executive", "Professional", "Educator", "Military Officer", "Business Owner", "Healthcare Professional",
    "Government Official", "Engineer", "Scientist", "Attorney", "Manager", "Director", "Consultant",
    "Analyst", "Architect", "Researcher", "Administrator", "Coordinator", "Specialist", "Supervisor"
]

def generate_customer_data(num_customers=5):
    customers = []
    for _ in range(num_customers):
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        
        # Generate retirement date (between 1 and 15 years ago)
        retirement_date = datetime.now() - timedelta(days=random.randint(365, 365*15))
        
        # Generate age (between 65 and 85)
        age = random.randint(65, 85)
        
        # Generate retirement income (between 50,000 and 200,000)
        retirement_income = f"${random.randint(50000, 200000):,}"
        
        # Generate more varied industry and job title
        industry_prefix = random.choice(INDUSTRY_PREFIXES)
        industry_type = random.choice(INDUSTRY_TYPES)
        industry = f"{industry_prefix} {industry_type}"
        
        job_prefix = random.choice(JOB_PREFIXES)
        job_type = random.choice(JOB_TYPES)
        job_title = f"{job_prefix} {job_type}"
        
        customer = {
            "name": f"{first_name} {last_name}",
            "email": f"{first_name.lower()}.{last_name.lower()}@example.com",
            "phone": f"+1-{random.randint(200, 999)}-{random.randint(200, 999)}-{random.randint(1000, 9999)}",
            "city": random.choice(CITIES),
            "job_title": job_title,
            "industry": industry,
            "annual_revenue": retirement_income,
            "account_manager": random.choice(ACCOUNT_MANAGERS),
            "customer_id": f"CUST-{random.randint(100, 999):03d}",
            "created_at": (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat(),
            "last_contact": (datetime.now() - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d"),
            "retirement_date": retirement_date.strftime("%Y-%m-%d"),
            "age": age
        }
        customers.append(customer)
    return customers

def create_customer_pdf(customer):
    pdf = FPDF()
    pdf.add_page()
    
    # Add title
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, f'Customer Information for {customer["name"]}', ln=True, align='C')
    pdf.ln(10)
    
    # Add customer details
    pdf.set_font('Arial', '', 12)
    details = [
        f"Customer ID: {customer['customer_id']}",
        f"Account Manager: {customer['account_manager']}",
        f"Status: Retired",
        f"Age: {customer['age']}",
        f"Retirement Date: {customer['retirement_date']}",
        f"Previous Industry: {customer['industry']}",
        f"Created at: {customer['created_at']}",
        "",
        "Notes:",
        f"- Primary contact: {customer['email']}",
        f"- Phone: {customer['phone']}",
        f"- City: {customer['city']}",
        f"- Previous Role: {customer['job_title']}",
        f"- Annual Retirement Income: {customer['annual_revenue']}",
        f"- Last contact: {customer['last_contact']}"
    ]
    
    for detail in details:
        pdf.cell(0, 10, detail, ln=True)
    
    return pdf

def create_sample_excel(customer):
    # Create a sample retirement portfolio
    data = {
        'Asset Type': ['Retirement Accounts (401k/IRA)', 'Social Security', 'Pension', 'Investment Portfolio', 'Real Estate', 'Cash Reserves'],
        'Allocation (%)': [35, 25, 15, 15, 5, 5],
        'Value ($)': [
            f"${random.randint(300000, 1000000):,}",
            f"${random.randint(20000, 40000):,}",
            f"${random.randint(50000, 200000):,}",
            f"${random.randint(100000, 500000):,}",
            f"${random.randint(100000, 300000):,}",
            f"${random.randint(50000, 200000):,}"
        ]
    }
    df = pd.DataFrame(data)
    return df

def get_user_input(prompt, min_value, max_value, default_value):
    while True:
        try:
            value = input(f"{prompt} (default: {default_value}): ").strip()
            if not value:
                return default_value
            
            value = int(value)
            if min_value <= value <= max_value:
                return value
            print(f"Please enter a number between {min_value} and {max_value}")
        except ValueError:
            print("Please enter a valid number")

def get_customer_count():
    return get_user_input(
        "\nHow many sample customers would you like to generate?",
        min_value=1,
        max_value=100,
        default_value=5
    )

def get_files_per_customer():
    return get_user_input(
        "\nHow many additional data files would you like per customer?",
        min_value=0,
        max_value=10,
        default_value=2
    )

def create_additional_files(customer, num_files, temp_dir):
    files = []
    for i in range(num_files):
        # Randomly choose between PDF and Excel
        if random.choice([True, False]):
            # Create additional PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font('Arial', '', 12)
            
            # Randomly choose a document type
            doc_type = random.choice([
                "Investment Strategy Review",
                "Tax Planning Document",
                "Insurance Coverage Analysis",
                "Estate Planning Update",
                "Healthcare Cost Projection",
                "Social Security Benefits Analysis",
                "Retirement Income Forecast",
                "Long-term Care Planning"
            ])
            
            pdf.cell(0, 10, f"{doc_type} - {customer['name']}", ln=True)
            pdf.ln(10)
            
            # Add some sample content
            pdf.multi_cell(0, 10, f"Document Date: {customer['last_contact']}\n\n"
                            f"Key Points:\n"
                            f"- Sample point 1\n"
                            f"- Sample point 2\n"
                            f"- Sample point 3\n\n"
                            f"Recommendations:\n"
                            f"- Sample recommendation 1\n"
                            f"- Sample recommendation 2")
            
            file_path = os.path.join(temp_dir, f"{customer['name']}_{doc_type.lower().replace(' ', '_')}.pdf")
            pdf.output(file_path)
            files.append((file_path, f"{customer['name']}_{doc_type.lower().replace(' ', '_')}.pdf"))
        else:
            # Create additional Excel
            data = {
                'Category': ['Category A', 'Category B', 'Category C', 'Category D'],
                'Value': [
                    f"${random.randint(10000, 100000):,}",
                    f"${random.randint(10000, 100000):,}",
                    f"${random.randint(10000, 100000):,}",
                    f"${random.randint(10000, 100000):,}"
                ],
                'Notes': ['Note 1', 'Note 2', 'Note 3', 'Note 4']
            }
            df = pd.DataFrame(data)
            
            file_name = f"{customer['name']}_additional_data_{i+1}.xlsx"
            file_path = os.path.join(temp_dir, file_name)
            df.to_excel(file_path, index=False)
            files.append((file_path, file_name))
    
    return files

def upload_to_dropbox(dbx, customer, root_folder, num_additional_files):
    # Create a temporary directory for our files
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create and save PDF
        pdf = create_customer_pdf(customer)
        pdf_path = os.path.join(temp_dir, f"{customer['name']}_info.pdf")
        pdf.output(pdf_path)
        
        # Create and save Excel
        df = create_sample_excel(customer)
        excel_path = os.path.join(temp_dir, f"{customer['name']}_portfolio.xlsx")
        df.to_excel(excel_path, index=False)
        
        # Create a sample note
        note_path = os.path.join(temp_dir, f"{customer['name']}_notes.pdf")
        note_pdf = FPDF()
        note_pdf.add_page()
        note_pdf.set_font('Arial', '', 12)
        note_pdf.cell(0, 10, f"Meeting Notes - {customer['name']}", ln=True)
        note_pdf.ln(10)
        note_pdf.multi_cell(0, 10, f"Meeting Date: {customer['last_contact']}\n\n"
                         f"Discussion Points:\n"
                         f"- Retirement Income Planning\n"
                         f"- Social Security Optimization\n"
                         f"- Required Minimum Distribution (RMD) Planning\n"
                         f"- Estate Planning Review\n"
                         f"- Healthcare Cost Planning\n\n"
                         f"Next Steps:\n"
                         f"- Review retirement account distributions\n"
                         f"- Update estate planning documents\n"
                         f"- Schedule annual healthcare review\n"
                         f"- Review long-term care insurance options")
        note_pdf.output(note_path)
        
        # Create additional files
        additional_files = create_additional_files(customer, num_additional_files, temp_dir)
        
        # Upload files to Dropbox
        folder_path = f"/{root_folder}/{customer['name']}"
        
        # Create customer folder
        try:
            dbx.files_create_folder(folder_path)
        except dropbox.exceptions.ApiError as e:
            if not (e.error.is_path() and e.error.get_path().is_conflict()):
                raise
        
        # Upload core files
        with open(pdf_path, 'rb') as f:
            dbx.files_upload(f.read(), f"{folder_path}/{customer['name']}_info.pdf")
        
        with open(excel_path, 'rb') as f:
            dbx.files_upload(f.read(), f"{folder_path}/{customer['name']}_portfolio.xlsx")
        
        with open(note_path, 'rb') as f:
            dbx.files_upload(f.read(), f"{folder_path}/{customer['name']}_notes.pdf")
        
        # Upload additional files
        for file_path, file_name in additional_files:
            with open(file_path, 'rb') as f:
                dbx.files_upload(f.read(), f"{folder_path}/{file_name}")

def main():
    # Get Dropbox token
    api_key = get_dropbox_token()
    if not api_key:
        return
    
    try:
        # Initialize Dropbox client
        dbx = dropbox.Dropbox(api_key)
        
        # Verify the connection
        dbx.users_get_current_account()
        print("Successfully connected to Dropbox!")
        
        # Get root folder
        root_folder = get_root_folder(dbx)
        
        # Get number of customers and files per customer
        num_customers = get_customer_count()
        num_additional_files = get_files_per_customer()
        
        # Generate customer data
        customers = generate_customer_data(num_customers)
        
        # Upload data for each customer
        for customer in customers:
            print(f"Creating data for {customer['name']}...")
            upload_to_dropbox(dbx, customer, root_folder, num_additional_files)
            print(f"Successfully uploaded data for {customer['name']}")
        
        print(f"\nAll customer data has been successfully uploaded to Dropbox folder: {root_folder}")
        print(f"Generated {num_customers} customers with {num_additional_files} additional files each")
        
    except AuthError as e:
        print(f"Error authenticating with Dropbox: {e}")
        print("Please check your access token and try again.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main() 