
using [whisperX](https://github.com/m-bain/whisperX) to run transcriptions.

Pipeline is run by running ./sync_and_transcribe.zsh inside the whisperx mamba
environment

this will run a bsub job with the GPU to run whisperX on the input audio file,
using the google drive folder specified in the text file, and using the hugging
face api key that is put in hf_token.txt

the output result is uploaded to Notion database as a transcript
