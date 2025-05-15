import os
import dropbox
from dropbox.exceptions import AuthError
import re
import requests
import json
import tempfile
import PyPDF2
import logging
from datetime import datetime
import sys
from requests_toolbelt.multipart.encoder import MultipartEncoder

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sync_to_twenty.log'),
        logging.StreamHandler()
    ]
)

def get_dropbox_token():
    token_file = 'token.txt'
    
    if os.path.exists(token_file):
        with open(token_file, 'r') as f:
            token = f.read().strip()
            if token:
                return token
    
    print("\nDropbox Access Token not found.")
    print("Please follow these steps:")
    print("1. Create a file named 'token.txt' in the current directory")
    print("2. Paste your Dropbox access token into this file")
    print("3. Save the file")
    print("4. Press Enter to continue...")
    
    input()
    
    if os.path.exists(token_file):
        with open(token_file, 'r') as f:
            token = f.read().strip()
            if token:
                return token
    
    print("Error: token.txt file not found or empty. Please try again.")
    return None

def get_twenty_token():
    token_file = 'twenty_token.txt'
    
    if os.path.exists(token_file):
        with open(token_file, 'r') as f:
            token = f.read().strip()
            if token:
                return token
    
    print("\nTwenty API Token not found.")
    print("Please follow these steps:")
    print("1. Create a file named 'twenty_token.txt' in the current directory")
    print("2. Paste your Twenty API token into this file")
    print("3. Save the file")
    print("4. Press Enter to continue...")
    
    input()
    
    if os.path.exists(token_file):
        with open(token_file, 'r') as f:
            token = f.read().strip()
            if token:
                return token
    
    print("Error: twenty_token.txt file not found or empty. Please try again.")
    return None

def init_dropbox():
    """Initialize Dropbox client with token."""
    try:
        token = get_dropbox_token()
        if not token:
            return None
            
        dbx = dropbox.Dropbox(token)
        dbx.users_get_current_account()  # Verify the connection
        logging.info("Successfully connected to Dropbox!")
        return dbx
    except Exception as e:
        logging.error(f"Error initializing Dropbox client: {e}")
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
                return root_folder
            except dropbox.exceptions.ApiError as e:
                if e.error.is_path() and e.error.get_path().is_not_found():
                    print(f"Error: Folder '{root_folder}' not found in Dropbox.")
                    print("Please check the folder name and try again.")
                else:
                    raise
        except Exception as e:
            print(f"Error accessing Dropbox folder: {e}")
            print("Please try again.")

def extract_customer_info(pdf_content):
    """Extract customer information from PDF content."""
    try:
        # Create a temporary file to store the PDF content
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_file.write(pdf_content)
            temp_file_path = temp_file.name

        # Read the PDF
        with open(temp_file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()

        # Extract information using regex patterns
        info = {}
        
        # Extract Customer ID
        customer_id_match = re.search(r'Customer ID: (CUST-\d{3})', text)
        if customer_id_match:
            info['customer_id'] = customer_id_match.group(1)
        
        # Extract Account Manager
        account_manager_match = re.search(r'Account Manager: (.*?)(?:\n|$)', text)
        if account_manager_match:
            info['account_manager'] = account_manager_match.group(1).strip()
        
        # Extract Age
        age_match = re.search(r'Age: (\d+)', text)
        if age_match:
            info['age'] = int(age_match.group(1))
        
        # Extract Retirement Date
        retirement_date_match = re.search(r'Retirement Date: (\d{4}-\d{2}-\d{2})', text)
        if retirement_date_match:
            info['retirement_date'] = retirement_date_match.group(1)
        
        # Extract Previous Industry
        industry_match = re.search(r'Previous Industry: (.*?)(?:\n|$)', text)
        if industry_match:
            info['industry'] = industry_match.group(1).strip()
        
        # Extract Contact Information
        email_match = re.search(r'Primary contact: (.*?)(?:\n|$)', text)
        if email_match:
            info['email'] = email_match.group(1).strip()
        
        phone_match = re.search(r'Phone: (.*?)(?:\n|$)', text)
        if phone_match:
            info['phone'] = phone_match.group(1).strip()
        
        city_match = re.search(r'City: (.*?)(?:\n|$)', text)
        if city_match:
            info['city'] = city_match.group(1).strip()
        
        # Extract Annual Revenue
        revenue_match = re.search(r'Annual Retirement Income: (\$[\d,]+)', text)
        if revenue_match:
            info['annual_revenue'] = revenue_match.group(1)
        
        # Clean up temporary file
        os.unlink(temp_file_path)
        
        return info
    except Exception as e:
        logging.error(f"Error extracting customer info from PDF: {e}")
        return None

def create_person_in_twenty(token, customer_info):
    """Create a person record in Twenty using GraphQL API."""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }
    
    # Prepare the mutation
    mutation = """
    mutation CreatePerson($data: PersonCreateInput!) {
      createPerson(data: $data) {
        id
        name {
          firstName
          lastName
        }
        emails {
          primaryEmail
        }
        phones {
          primaryPhoneNumber
        }
        city
      }
    }
    """
    
    # Prepare the variables
    variables = {
        "data": {
            "name": {
                "firstName": customer_info.get('first_name', ''),
                "lastName": customer_info.get('last_name', '')
            },
            "emails": {
                "primaryEmail": customer_info.get('email', '')
            },
            "phones": {
                "primaryPhoneNumber": customer_info.get('phone', '')
            },
            "city": customer_info.get('city', '')
        }
    }
    
    try:
        response = requests.post(
            'http://localhost:3003/graphql',
            headers=headers,
            json={
                'query': mutation,
                'variables': variables
            }
        )
        response.raise_for_status()
        result = response.json()
        
        if 'errors' in result:
            logging.error(f"GraphQL errors: {result['errors']}")
            return None
            
        return result['data']['createPerson']['id']
        
    except Exception as e:
        logging.error(f"Error creating person in Twenty: {e}")
        return None

def upload_file_to_twenty(twenty_token, file_name, file_content):
    """Upload a file to Twenty and return the file ID."""
    url = "http://localhost:3003/graphql"
    
    # Prepare the mutation (no personId argument)
    mutation = """
    mutation UploadFile($file: Upload!, $fileFolder: FileFolder) {
        uploadFile(file: $file, fileFolder: $fileFolder)
    }
    """
    
    operations = json.dumps({
        "query": mutation,
        "variables": {
            "file": None,
            "fileFolder": "PersonPicture"
        }
    })
    map_ = json.dumps({"0": ["variables.file"]})
    m = MultipartEncoder(
        fields={
            'operations': operations,
            'map': map_,
            '0': (file_name, file_content)
        }
    )
    
    headers = {
        "Authorization": f"Bearer {twenty_token}",
        "Content-Type": m.content_type
    }
    
    try:
        response = requests.post(url, data=m, headers=headers)
        response.raise_for_status()
        result = response.json()
        
        if 'errors' in result:
            error_msg = str(result['errors'])
            logging.error(f"Error uploading file to Twenty: {error_msg}")
            raise Exception(f"Failed to upload file: {error_msg}")
        
        file_id = result['data']['uploadFile']
        logging.info(f"File uploaded successfully. Return value: {file_id}")
        return file_id
    except Exception as e:
        logging.error(f"Error making API request to Twenty: {e}")
        raise Exception(f"Failed to upload file: {file_name} - {str(e)}")

def upload_document_to_twenty(file_path, file_name):
    """Upload a document to Twenty."""
    try:
        # Use "Attachment" folder for all files
        file_folder = "Attachment"
        
        mutation = """
        mutation UploadFile($file: Upload!, $fileFolder: FileFolder) {
            uploadFile(file: $file, fileFolder: $fileFolder)
        }
        """
        
        # Prepare the request with multipart encoding
        operations = {
            "query": mutation,
            "variables": {
                "file": None,
                "fileFolder": file_folder
            }
        }
        
        map_data = {
            "0": ["variables.file"]
        }
        
        files = {
            "operations": (None, json.dumps(operations)),
            "map": (None, json.dumps(map_data)),
            "0": (file_name, open(file_path, "rb"))
        }
        
        # Make the request
        response = requests.post(
            TWENTY_API_URL,
            headers={"Authorization": f"Bearer {TWENTY_TOKEN}"},
            files=files
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to upload document: {response.text}")
        
        result = response.json()
        if "errors" in result:
            raise Exception(f"GraphQL error: {result['errors']}")
        
        file_id = result["data"]["uploadFile"]
        logging.info(f"Document uploaded successfully: {file_id}")
        
        # Extract base URL without token
        base_url = file_id.split('?')[0]
        return base_url
        
    except Exception as e:
        logging.error(f"Error uploading document: {str(e)}")
        raise

def create_attachment_in_twenty(twenty_token, file_id, person_id, document_type="attachment", name=None):
    """Associate an uploaded file with a person in Twenty using createAttachment mutation and AttachmentCreateInput."""
    url = "http://localhost:3003/graphql"
    mutation = '''
    mutation CreateAttachment($data: AttachmentCreateInput!) {
      createAttachment(data: $data) {
        id
        name
        type
        personId
        person {
          id
          name { firstName lastName }
        }
        fullPath
      }
    }
    '''
    # Extract the original filename from the file_id if name is not provided
    if not name:
        # The file_id is in the format "attachment/UUID.extension?token=..."
        # We want to extract just the UUID.extension part
        name = file_id.split('/')[-1].split('?')[0]
    
    # Extract the base URL without tokens
    base_url = file_id.split('?')[0]
    
    data_input = {
        "name": name,
        "fullPath": base_url,  # Use the base URL without tokens
        "type": document_type,
        "personId": person_id
    }
    variables = {"data": data_input}
    headers = {
        "Authorization": f"Bearer {twenty_token}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(url, headers=headers, json={"query": mutation, "variables": variables})
        response.raise_for_status()
        result = response.json()
        if 'errors' in result:
            error_msg = str(result['errors'])
            logging.error(f"Error creating attachment in Twenty: {error_msg}")
            raise Exception(f"Failed to create attachment: {error_msg}")
        attachment = result['data']['createAttachment']
        logging.info(f"Attachment created successfully: {attachment}")
        return attachment
    except Exception as e:
        logging.error(f"Error making API request to Twenty: {e}")
        raise Exception(f"Failed to create attachment for file: {file_id} and person: {person_id} - {str(e)}")

def process_customer_folder(dbx, folder_path, twenty_token):
    """Process a customer folder and create records in Twenty."""
    try:
        # List all files in the folder
        result = dbx.files_list_folder(folder_path)
        
        # First, find and process the info PDF to create the person record
        person_id = None
        for entry in result.entries:
            if entry.name.endswith('_info.pdf'):
                _, response = dbx.files_download(f"{folder_path}/{entry.name}")
                customer_info = extract_customer_info(response.content)
                if not customer_info:
                    raise Exception(f"Could not extract customer info from PDF in folder: {folder_path}")
                # Try to parse first and last name from the file or folder name if not present
                if 'first_name' not in customer_info or not customer_info['first_name']:
                    name_parts = entry.name.replace('_info.pdf', '').replace('_', ' ').split()
                    if len(name_parts) >= 2:
                        customer_info['first_name'] = name_parts[0]
                        customer_info['last_name'] = ' '.join(name_parts[1:])
                    else:
                        customer_info['first_name'] = name_parts[0]
                        customer_info['last_name'] = ''
                person_id = create_person_in_twenty(twenty_token, customer_info)
                break
        
        if not person_id:
            raise Exception(f"No info PDF found in folder {folder_path}")
        
        # Now process all files and create attachments
        for entry in result.entries:
            try:
                # Download the file
                _, response = dbx.files_download(f"{folder_path}/{entry.name}")
                
                # Save the file temporarily
                temp_file_path = f"/tmp/{entry.name}"
                with open(temp_file_path, "wb") as f:
                    f.write(response.content)
                
                try:
                    # Upload the file to Twenty
                    file_id = upload_document_to_twenty(temp_file_path, entry.name)
                    
                    # Create the attachment
                    create_attachment_in_twenty(
                        twenty_token,
                        file_id,
                        person_id,
                        document_type="passport",
                        name=entry.name
                    )
                finally:
                    # Clean up the temporary file
                    if os.path.exists(temp_file_path):
                        os.remove(temp_file_path)
                        
            except Exception as e:
                logging.error(f"Error processing file {entry.name}: {str(e)}")
                continue
                
    except Exception as e:
        logging.error(f"Error processing folder {folder_path}: {str(e)}")
        raise

def main():
    """Main function to sync Dropbox files to Twenty."""
    try:
        # Initialize Dropbox client
        dbx = init_dropbox()
        if not dbx:
            raise Exception("Failed to initialize Dropbox client")
            
        # Get Twenty token
        twenty_token = get_twenty_token()
        if not twenty_token:
            raise Exception("Failed to get Twenty token")
            
        # Get root folder name
        root_folder = input("Enter the root folder name for customer data (default: 'Wealth Management'): ").strip()
        if not root_folder:
            root_folder = "Wealth Management"
            print(f"Using default folder: {root_folder}")
            
        # Check if folder exists
        try:
            dbx.files_get_metadata(f"/{root_folder}")
            print(f"Using existing folder: {root_folder}")
        except dropbox.exceptions.ApiError:
            raise Exception(f"Folder '{root_folder}' not found in Dropbox")
            
        # List all customer folders
        result = dbx.files_list_folder(f"/{root_folder}")
        
        # Process each customer folder
        for entry in result.entries:
            if isinstance(entry, dropbox.files.FolderMetadata):
                process_customer_folder(dbx, entry.path_display, twenty_token)
                
    except Exception as e:
        logging.error(f"Script failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 