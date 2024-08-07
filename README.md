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

## Usage
Run the script with the required Asana access token, project ID, and optional output directory:

```python Asana_backup.py --help
usage: Asana_backup.py [-h] --token TOKEN [--output-dir OUTPUT_DIR] --project-id PROJECT_ID [--without-attachments]

Asana Backup Script

options:
  -h, --help            show this help message and exit
  --token TOKEN         (Required) Your Asana Access Token
  --output-dir OUTPUT_DIR
                        (Optional) Directory where the output will be saved. Default is `asana_project_data`
  --project-id PROJECT_ID
                        (Required) ID of the Asana project to back up
  --without-attachments
                        (Optional) Do not download attachments
```
                       
## Output
The script creates a directory (default **asana_project_data**) containing:
- A CSV file (**project_data.csv**) with task details.
- The **attachments** folder containing all files in their respective task folders, saved with unique file names.

_____________________________________________________________________________________
# Obtaining Asana Project ID and Access Token

To integrate with Asana's API, you'll need to obtain your Project ID and an Access Token. Follow the steps below to retrieve these details.

## Step 1: Log in to Asana Account

## Step 2: Find Your Project ID
1. **Navigate to the project for which you want the ID.**
2. **Look at the URL in your browser's address bar.** It should look something like this:
   ```https://app.asana.com/0/{workspace_id}/{project_id}```
3. **Copy your project_id**

## Step 3: Generate a Personal Access Token
1. **Go to the Asana Developer Console:**
   - Navigate to [Asana Developer Console](https://app.asana.com/0/developer-console).
2. **Create a new Personal Access Token:**
   - Click on "Create new token".
   - Give your token a name, for example "My Project Integration".
   - Click "Create Token".
3. **Copy your Personal Access Token:**
   - Once the token is generated, copy it immediately. **You won’t be able to see it again**. 
   - Store it in a secure place.
___________________________________________________________________________________

## Contributing
Feel free to open issues or submit pull requests for any improvements or bug fixes.

## License
This project is licensed under the MIT License.  

