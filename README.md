# AsanaBackupTool
This script automates the process of backing up tasks, comments, and attachments from an Asana project. It fetches task details, stories, and attachments, and saves them in a CSV file and organized folders. Users can specify their Asana access token, project ID, and the output directory.

## Features

- Fetch tasks from an Asana project
- Retrieve task details, comments (stories), and attachments
- Download attachments and save them with unique filenames
- Save all task data to a CSV file

## Requirements

- Python 3.6+
- `requests` library

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/AsanaBackupTool.git
    cd AsanaBackupTool
    ```

2. Install the required libraries:
    ```bash
    pip install requests
    ```
## Arguments
- --token: (Required) Your Asana access token.
- --project-id: (Required) The ID of your Asana project.
- --output-dir: (Optional) The directory to save the downloaded data. Default is asana_project_data.

Please make sure your Asana access token has the necessary permissions to read the project data.
AsanaBackupTool is licensed under the MIT License. 

## Usage

Run the script with the required Asana access token, project ID, and optional output directory:

```bash
python Asana_backup_new_new.py --token your_access_token --project-id your_project_id --output-dir your_output_directory
