import requests
import json
import os
import csv
from urllib.parse import unquote
import argparse

# Function to parse command-line arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description="Asana Backup Script")
    parser.add_argument('--token', type=str, required=True, help='Asana Access Token')
    parser.add_argument('--output-dir', type=str, default='asana_project_data', help='Output Directory')
    parser.add_argument('--project-id', type=str, required=True, help='Asana Project ID')
    return parser.parse_args()

# Parse the arguments and set the constants
args = parse_arguments()
ASANA_ACCESS_TOKEN = args.token
OUTPUT_DIR = args.output_dir
PROJECT_ID = args.project_id

# Headers for Asana API
headers = {
    'Authorization': f'Bearer {ASANA_ACCESS_TOKEN}'
}

# Function to fetch tasks from a project
def fetch_tasks(project_id):
    url = f'https://app.asana.com/api/1.0/projects/{project_id}/tasks?opt_fields=gid,name,assignee_status,completed,created_at,due_on,assignee,subtasks'
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    print("Fetched tasks.")
    return response.json()['data']

# Function to fetch details of a specific task
def fetch_task_details(task_id):
    url = f'https://app.asana.com/api/1.0/tasks/{task_id}?opt_fields=gid,name,assignee,assignee_status,completed,created_at,due_on,notes,followers,projects,resource_subtype,start_on,tags,subtasks'
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    print(f"Fetched details for task {task_id}.")
    return response.json()['data']

# Function to fetch stories (comments) of a task
def fetch_task_stories(task_id):
    url = f'https://app.asana.com/api/1.0/tasks/{task_id}/stories'
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    print(f"Fetched stories for task {task_id}.")
    return response.json()['data']

# Function to fetch attachments of a task
def fetch_task_attachments(task_id):
    url = f'https://app.asana.com/api/1.0/tasks/{task_id}/attachments?opt_fields=gid,name,download_url'
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    print(f"Fetched attachments for task {task_id}.")
    return response.json()['data']

# Function to extract filename from Content-Disposition header
def extract_filename(content_disposition):
    if 'filename*=' in content_disposition:
        filename = content_disposition.split("filename*=")[1]
        filename = filename.split("''")[1]  # Remove charset part
        filename = unquote(filename)  # Decode percent-encoded characters
    elif 'filename=' in content_disposition:
        filename = content_disposition.split("filename=")[1].strip('"')
    else:
        filename = "unknown_filename"
    return filename

# Function to truncate filename if it's too long
def truncate_filename(filename, max_length=255):
    if len(filename) > max_length:
        filename, extension = os.path.splitext(filename)
        filename = filename[:max_length - len(extension)] + extension
    return filename

# Function to generate a unique filename if a file already exists
def generate_unique_filename(filename, task_folder):
    base_name, extension = os.path.splitext(filename)
    counter = 1
    unique_filename = filename
    while os.path.exists(os.path.join(task_folder, unique_filename)):
        unique_filename = f"{base_name}_{counter}{extension}"
        counter += 1
    return unique_filename

# Function to download an attachment
def download_attachment(attachment, task_name):
    download_url = attachment.get('download_url')
    
    if not download_url:
        asset_id = attachment['gid']
        download_url = f"https://app.asana.com/app/asana/-/get_asset?asset_id={asset_id}"
    
    headers_without_auth = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(download_url, headers=headers_without_auth, stream=True)
        response.raise_for_status()
        
        task_folder = os.path.join(OUTPUT_DIR, 'attachments', task_name)
        os.makedirs(task_folder, exist_ok=True)
        
        if 'Content-Disposition' in response.headers:
            content_disposition = response.headers['Content-Disposition']
            filename = extract_filename(content_disposition)
        else:
            filename = attachment['name']

        filename = truncate_filename(filename)
        filename = generate_unique_filename(filename, task_folder)
        attachment_path = os.path.join(task_folder, filename)

        with open(attachment_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
        
        print(f"Downloaded attachment {filename} for task {task_name}.")

    except requests.exceptions.RequestException as e:
        print(f"Failed to download attachment {attachment['name']} for task {task_name}. URL: {download_url}. Error: {e}")
        with open("debug_response.html", 'wb') as debug_file:
            debug_file.write(response.content)
        print("Saved debug response to 'debug_response.html'")
        
# Function to save tasks data to a CSV file
def save_data_to_csv(tasks_data):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    csv_file = os.path.join(OUTPUT_DIR, 'project_data.csv')
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Task ID', 'Task Name', 'Assignee', 'Status', 'Created At', 'Due On', 'Comments', 'Attachments', 'Subtasks'])

        for task in tasks_data:
            task_details = task['details']
            comments = '\n'.join([comment['text'] for comment in task['comments']])
            attachments = '\n'.join([attachment['name'] for attachment in task['attachments']])
            subtasks = '\n'.join([subtask['name'] for subtask in task_details.get('subtasks', []) if 'name' in subtask])

            assignee_name = task_details['assignee']['name'] if task_details['assignee'] else 'Unassigned'
            writer.writerow([
                task_details['gid'],
                task_details['name'],
                assignee_name,
                task_details['completed'],
                task_details['created_at'],
                task_details['due_on'],
                comments,
                attachments,
                subtasks
            ])
    print("Saved data to CSV.")

# Main function to orchestrate fetching and saving tasks data
def main():
    tasks = fetch_tasks(PROJECT_ID)
    all_data = []

    for task in tasks:
        task_id = task['gid']
        task_details = fetch_task_details(task_id)
        task_stories = fetch_task_stories(task_id)
        task_attachments = fetch_task_attachments(task_id)

        # Download each attachment
        for attachment in task_attachments:
            download_attachment(attachment, task_details['name'])

        task_data = {
            'details': task_details,
            'comments': task_stories,
            'attachments': task_attachments
        }
        
        all_data.append(task_data)

    # Save tasks data to CSV
    save_data_to_csv(all_data)
    print(f"Data has been saved to the '{OUTPUT_DIR}' directory.")

if __name__ == "__main__":
    main()
