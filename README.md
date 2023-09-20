
#  Whisper Transcription (with Notion & Google Drive)

This project provides an automation script to download audio files from Google Drive, transcribe them, and upload the transcriptions to Notion, before moving the audio file to a new google drive folder after completion.

## Features

- Downloads audio files from a specified Google Drive folder.
- Transcribes the audio using the [whisperX](https://github.com/m-bain/whisperX) pipeline which runs on OpenAI's Whisper model.
- Uploads the transcription to a Notion database.
- Ability to move processed audio files to a different Google Drive folder.

## Requirements

- Python 3.8 or higher.
- Google Drive API access.
- Notion API access.
- GPU compute resources
- LSF job scheduler

Dependencies can be installed into mamba or conda environment with the following

```{bash}
mamba env update -n whisperx --file whisperx.yaml
```

## Setup

1. **Google Drive API Setup**:
   - Visit the [Google Cloud Console](https://console.cloud.google.com/).
   - Create a new project and navigate to it.
   - In the dashboard, search for "Google Drive API" and enable it.
   - Go to the `Credentials` tab and click on "Create Credentials" > "OAuth 2.0 Client IDs".
   - Configure the OAuth consent screen and choose the "Desktop App" application type.
   - Download the `client_secrets.json` file and extract the client_id and client_secret

2. **Notion API Setup**:
   - Go to [Notion.so](https://www.notion.so/) and create an integration to get your NOTION_TOKEN
   - extract the id from the notion page for the database to get the DATABASE_ID
   - Share your database with your newly created integration.

3. **Configuration**:
   - Edit the `settings.yaml` to add your client_id and client_secret keys for the Google Cloud API
   - Edit the `gdrive_whisper_settings.json` with appropriate values for Google Drive folder IDs, Notion tokens, and other necessary configurations.


## Usage

Execute the main script, it will check for new files in the Google Drive folder
you specify and automatically run the transcriptions on any new files in there
before moving them to the output folder you specify in the `gdrive_whisper_settings.json`

   ```
   python google_drive_api.py
   ```

