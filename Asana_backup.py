import requests
import os
import csv
from urllib.parse import unquote
import argparse


def parse_arguments():
    parser = argparse.ArgumentParser(description="Asana Backup Script")
    parser.add_argument('--token', type=str, required=True, help='(Required) Your Asana Access Token')
    parser.add_argument('--project-id', type=str, required=True, help='(Required) ID of the Asana project to back up')
    parser.add_argument('--output-dir', type=str, default='asana_project_data', help='(Optional) Directory where the output will be saved. Default is `asana_project_data`')
    parser.add_argument('--without-attachments', action='store_true', help='(Optional) Do not download attachments')
    return parser.parse_args()


args = parse_arguments()
ASANA_ACCESS_TOKEN = args.token
OUTPUT_DIR = args.output_dir
PROJECT_ID = args.project_id
WITHOUT_ATTACHMENTS = args.without_attachments

headers = {
    'Authorization': f'Bearer {ASANA_ACCESS_TOKEN}'
}


def fetch_tasks(project_id):
    url = (f'https://app.asana.com/api/1.0/projects/{project_id}/tasks?opt_fields=gid,name,assignee_status,completed,'
           'created_at,due_on,assignee,subtasks')
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    print("Fetched tasks.")
    return response.json()['data']


def fetch_task_details(task_id):
    url = (f'https://app.asana.com/api/1.0/tasks/{task_id}?opt_fields=gid,name,assignee,assignee_status,completed,'
           'created_at,due_on,notes,followers,projects,resource_subtype,start_on,tags,subtasks')
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    print(f"Fetched details for task {task_id}.")
    return response.json()['data']


def fetch_task_stories(task_id):
    url = f'https://app.asana.com/api/1.0/tasks/{task_id}/stories'
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    print(f"Fetched stories for task {task_id}.")
    return response.json()['data']


def fetch_task_attachments(task_id):
    url = f'https://app.asana.com/api/1.0/tasks/{task_id}/attachments?opt_fields=gid,name,download_url'
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    print(f"Fetched attachments for task {task_id}.")
    return response.json()['data']


def extract_filename(content_disposition):
    if 'filename*=' in content_disposition:
        filename = content_disposition.split("filename*=")[1]
        filename = filename.split("''")[1]
        filename = unquote(filename)
    elif 'filename=' in content_disposition:
        filename = content_disposition.split("filename=")[1].strip('"')
    else:
        filename = "unknown_filename"
    return filename


def truncate_filename(filename, max_length=255):
    if len(filename) > max_length:
        filename, extension = os.path.splitext(filename)
        filename = filename[:max_length - len(extension)] + extension
    return filename


def generate_unique_filename(filename, task_folder):
    base_name, extension = os.path.splitext(filename)
    counter = 1
    unique_filename = filename
    while os.path.exists(os.path.join(task_folder, unique_filename)):
        unique_filename = f"{base_name}_{counter}{extension}"
        counter += 1
    return unique_filename


def download_attachment(attachment, task_name):
    download_url = attachment.get('download_url')

    if not download_url:
        asset_id = attachment['gid']
        download_url = f"https://app.asana.com/app/asana/-/get_asset?asset_id={asset_id}"

    headers_without_auth = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/91.0.4472.124 Safari/537.36'
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
        pr
