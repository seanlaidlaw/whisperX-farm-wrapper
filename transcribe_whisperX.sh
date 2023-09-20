#!/usr/bin/env bash
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/lustre/scratch126/casm/team154pc/sl31/HomeExpansion/mambaforge/lib

whisperx "$1" --language en --model large-v2 --align_model WAV2VEC2_ASR_LARGE_LV60K_960H --vad_filter True --diarize --hf_token "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"
