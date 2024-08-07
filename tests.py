import pytest
from unittest.mock import patch, MagicMock
import requests

from Asana_backup import (
    parse_arguments,
    fetch_tasks,
    fetch_task_details,
    fetch_task_stories,
    fetch_task_attachments,
    preprocess_task_details,
    save_data_to_csv
)


def test_preprocess_task_details():
    task_details = {
        'gid': '1234',
        'name': 'Test Task',
        'assignee': None,
        'completed': True,
        'created_at': '2024-01-01',
        'due_on': '2024-01-31',
        'subtasks': []
    }
    processed_details = preprocess_task_details(task_details)
    assert processed_details['assignee']['name'] == 'Unassigned'
    assert processed_details['name'] == 'Test Task'
    assert processed_details['completed'] is True
    assert processed_details['created_at'] == '2024-01-01'
    assert processed_details['due_on'] == '2024-01-31'


@patch('requests.get')
def test_fetch_tasks(mock_get):
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {'data': [{'gid': '1234', 'name': 'Test Task'}]}
    mock_get.return_value = mock_response

    tasks = fetch_tasks('project_id')
    assert len(tasks) == 1
    assert tasks[0]['gid'] == '1234'


@patch('requests.get')
def test_fetch_task_details(mock_get):
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {'data': {'gid': '1234', 'name': 'Test Task'}}
    mock_get.return_value = mock_response

    task_details = fetch_task_details('task_id')
    assert task_details['gid'] == '1234'


@patch('requests.get')
def test_fetch_task_stories(mock_get):
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {'data': [{'text': 'Test comment'}]}
    mock_get.return_value = mock_response

    stories = fetch_task_stories('task_id')
    assert len(stories) == 1
    assert stories[0]['text'] == 'Test comment'


@patch('requests.get')
def test_fetch_task_attachments(mock_get):
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {'data': [{'name': 'Test Attachment'}]}
    mock_get.return_value = mock_response

    attachments = fetch_task_attachments('task_id')
    assert len(attachments) == 1
    assert attachments[0]['name'] == 'Test Attachment'


if __name__ == "__main__":
    pytest.main()
