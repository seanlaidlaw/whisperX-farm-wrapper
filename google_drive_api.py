#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import subprocess
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials

# Load settings from the settings.json file
with open("gdrive_whisper_settings.json", "r") as f:
    settings = json.load(f)

GDRIVE_API_DIR = settings["GDRIVE_API_DIR"]
GDRIVE_FOLDER_ID = settings["GDRIVE_FOLDER_ID"]
GDRIVE_OUTPUT_FOLDER_ID = settings["GDRIVE_OUTPUT_FOLDER_ID"]
DOWNLOAD_PATH = settings["DOWNLOAD_PATH"]
HF_TOKEN = settings["HF_TOKEN"]


def authenticate_gdrive():
    scope = ["https://www.googleapis.com/auth/drive"]
    gauth = GoogleAuth()
    gauth.auth_method = "service"
    gauth.credentials = ServiceAccountCredentials.from_json_keyfile_name(
        "credentials.json", scope
    )

    if gauth.credentials is None:
        # Authenticate if they're not there
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        # Refresh them if expired
        gauth.Refresh()
    else:
        # Initialize the saved creds
        gauth.Authorize()

    drive = GoogleDrive(gauth)
    file_list = drive.ListFile(
        {"q": "'{}' in parents".format(GDRIVE_API_DIR)}
    ).GetList()
    if len(file_list) < 1:
        raise Exception(
            "Google Drive didn't authorize correctly. Can't see files in drive"
        )
    else:
        return gauth


def fetch_input_audio_files(folder_id, gauth):
    drive = GoogleDrive(gauth)

    # List all files in the folder using the folder's ID
    file_list = drive.ListFile({"q": "'{}' in parents".format(folder_id)}).GetList()

    # Loop through each file and add to array for us to work with
    audio_files_to_transcribe = []
    for file1 in file_list:
        audio_files_to_transcribe.append(file1)

    return audio_files_to_transcribe


def download_file_from_google_drive(gd_file, download_path):
    download_path = download_path + "/" + gd_file["title"]
    gd_file.GetContentFile(download_path)
    if not os.path.exists(download_path):
        raise Exception("File not downloaded correctly")
    else:
        return download_path


def delete_file_from_google_drive(gd_file):
    gd_file.Delete()


# 3. Extract creation date from audio file
def get_creation_time(input_track):
    cmd = ["ffprobe", input_track]
    output = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode("utf-8")
    for line in output.splitlines():
        if "creation_time" in line:
            # usually the line will be like this, so we need to ignore before 0th : and keep everything after that
            #     creation_time   : 2023-06-10T16:29:15.000000Z
            split_line = line.split(":")
            everything_after_first = split_line[1 : len(split_line)]
            creation_time = ":".join(everything_after_first).strip()
            return creation_time


# 4. Transcribe using whisper with subprocess
def transcribe_audio(input_path):
    bsub_command = [
        "bsub",
        "-q",
        "gpu-normal",
        "-Is",
        "-n",
        "1",
        "-gpu",
        "num=1",
        "-R",
        "select[(mem>=12000)] order[gpu_maxfactor]",
        "-R",
        "span[hosts=1]",
        "-R",
        "rusage[mem=12000]",
        "-M12000",
        "whisperx",
        "--model",
        "large-v2",
        "--align_model",
        "WAV2VEC2_ASR_LARGE_LV60K_960H",
        "--diarize",
        "--language",
        "en",
        "--hf_token",
        HF_TOKEN,
        input_path,
    ]

    subprocess.run(bsub_command, check=True)


def get_transcribed_json(input_path):
    basename = os.path.basename(input_path)
    basename_extensionless = os.path.splitext(basename)[0]
    json_out = basename_extensionless + ".json"
    if not os.path.exists(json_out):
        raise Exception("JSON transcription not found")
    else:
        return json_out


# 5. Parse JSON to markdown
def parse_json_to_markdown(json_file):
    with open(json_file, "r") as f:
        transcript_json = json.load(f)
    segments = transcript_json["segments"]
    ext_less = os.path.splitext(json_file)[0]
    transcript_md = ext_less + ".transcript.md"
    with open(transcript_md, "a") as output_file:
        for segment in segments:
            if "speaker" in segment:
                speaker = segment["speaker"]
            else:
                speaker = "Unkown_Speaker"
            if "text" in segment:
                text = segment["text"]
                output_file.write(f"[{speaker.strip()}] {text.strip()}\n")
    return transcript_md


# 7. Cleanup generated files
def cleanup_temp_files(file_path):
    basename = os.path.basename(file_path)
    basename_extensionless = os.path.splitext(basename)[0]

    # delete all the output files from successful transcription
    for ext in ["json", "srt", "tsv", "txt", "vtt", "transcript.md"]:
        try:
            os.remove(basename_extensionless + "." + ext)
        except FileNotFoundError:
            pass

    # remove main audio file we transcribed
    try:
        os.remove(file_path)
    except FileNotFoundError:
        pass


def move_GDrive_file_to_completed(gd_file, destination_folder_id):
    # Fetch existing parent references of the file
    file_parents = gd_file["parents"]

    # Create a new reference to the destination folder
    new_parents = [{"kind": "drive#fileLink", "id": destination_folder_id}]

    # Update the file's parents property to associate it with the new folder
    gd_file["parents"] = new_parents
    gd_file.Upload()


if __name__ == "__main__":
    auth = authenticate_gdrive()
    audio_files = fetch_input_audio_files(GDRIVE_FOLDER_ID, auth)
    if len(audio_files) < 1:
        print("No files in Google drive folder")

    for file in audio_files:
        file_path = download_file_from_google_drive(file, DOWNLOAD_PATH)
        creation_time = get_creation_time(file_path)
        transcribe_audio(file_path)
        transcribed_json = get_transcribed_json(file_path)
        transcript_md = parse_json_to_markdown(transcribed_json)
        move_GDrive_file_to_completed(file, GDRIVE_OUTPUT_FOLDER_ID)
        cleanup_temp_files(file_path)
