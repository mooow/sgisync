# sgisync #

This tool allows you to download magazines from sgi-italia.org (`sgidl.py`) and
sync them to a folder in your Google Drive (`SgiSync`, which uses my own google
drive interface, `gdrive.py`)

## Installing
You need a Google API `client_secrets.json` before you try using this program.
You should be able to obtain one from [here](https://console.developers.google.com/cloud-resource-manager).

## Configuration files ##
You can find example Configuration files in `skeleton`
* **sgidl_login.conf**: There you will put your username and password to access
sgi-italia.org
* sgisync.conf: There you will specify which magazines you want to sync, and in
which Google Drive folder you want to sync

The file `gdrive_credentials.json` will be created the first time the script is run, after browser authentication.

## Licensing ##
Please see `LICENSE`
