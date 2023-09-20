#!/usr/bin/env zsh

# fail script on first error
set -e

 gdrive_folder=$(<google_drive_folder.txt)
 hf_token=$(<hf_token.txt)

# download google drive folder for transcribing
gdown --fuzzy https://drive.google.com/drive/folders/"${gdrive_folder}" -O input_audio --folder

# find audio file in google drive folder
input_track="$(ls input_audio | grep '.m4a' | head -n 1)"

# get from audiofile the creation date
creation_time=$(ffprobe input_audio/"$input_track" 2>&1 | grep "creation_time" | sed 's/ *creation_time *: *//g' | tail -n 1)

# run transcription using whisper
bsub -q gpu-huge \
	-Is -n 1 -gpu "num=1" \
	-R'select[(mem>=12000)] order[gpu_maxfactor]' \
	-R'span[hosts=1]' -R'rusage[mem=12000]' -M12000 \
	whisperx --model large-v2 --align_model WAV2VEC2_ASR_LARGE_LV60K_960H \
	--diarize --language en \
	--hf_token "$hf_token" \
	 "input_audio/$input_track"

# generate from json transcript, a markdown format with speaker and text
python3 parse_json_to_markdown.py

python3 ./upload_notion.py "$creation_time"
rm input_audio/"$input_extensionless".{wav,m4a}
rm "$input_extensionless".{srt,tsv,txt,vtt,word.srt,json}
