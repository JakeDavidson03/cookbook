"""
A simple AI Action template showcasing some more advanced configuration features

Please check out the base guidance on AI Actions in our main repository readme:
https://github.com/sema4ai/actions/blob/master/README.md

"""

import numbers
import requests
import json
from sema4ai.actions import action, Secret

DELETE_URL = "https://api.dropboxapi.com/2/files/delete_v2"
DIRECTORY_CONTENTS_URL = "https://api.dropboxapi.com/2/files/list_folder"
DIRECTORY_CREATE_URL = "https://api.dropboxapi.com/2/files/create_folder_v2"
DOWNLOAD_URL = "https://content.dropboxapi.com/2/files/download"
UPLOAD_URL = "https://content.dropboxapi.com/2/files/upload"

def entry_to_file_item(
    entry: dict[str, str]
) -> dict[str, str]:
    return {
        "file_name": entry["name"],
        "full_path": entry["path_display"],
        "type": "directory" if entry[".tag"] == "folder" else "file",
        "size": entry["size"] if "size" in entry else 0
    }

###########
# ACTIONS #
###########

@action
def create_directory(
    dropbox_token: Secret,
    remote_path: str
) -> str:
    """
    Create a remote directory/path on a Dropbox account.

    Args:
        dropbox_token: The access token for an account.
        remote_path: The remote directory path to create.

    Returns:
        The created path.
    """

    response = requests.post(
        DIRECTORY_CREATE_URL,
        headers = {
            "Authorization": f"Bearer {dropbox_token.value}",
            "Content-Type": "application/json"
        },
        data = json.dumps({
            "path": remote_path,
            "autorename": False
        })
    )
    response.raise_for_status()

    return remote_path

@action
def list_files(
    dropbox_token: Secret,
    remote_path: str
) -> str:
    """
    List remote files and folders on a Dropbox account.

    Args:
        dropbox_token: The access token for an account.
        remote_path: The remote directory path to request against.

    Returns:
        A list of files and folders.
    """

    response = requests.post(
        DIRECTORY_CONTENTS_URL,
        headers = {
            "Authorization": f"Bearer {dropbox_token.value}",
            "Content-Type": "application/json"
        },
        data = json.dumps({
            "path": "" if remote_path == "/" else remote_path,
            "recursive": False,
            "limit": 2000,
            "include_media_info": False,
            "include_deleted": False,
            "include_has_explicit_shared_members": False,
            "include_mounted_folders": True
        })
    )
    response.raise_for_status()

    result = response.json()

    files = list(map(entry_to_file_item, result["entries"]))

    return json.dumps(files, separators=(',', ':'))
