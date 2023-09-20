#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json

ls = os.listdir()
for file in ls:
    if file.endswith(".json"):
        print("Reading: " + file)
        with open(file, 'r') as f:
            transcript_json = json.load(f)
        transcript_json
        segments = transcript_json["segments"]
        segment_list = []
        for segment in segments:
            segment_dict = {"speaker": segment["speaker"], "text": segment["text"]}
            segment_list.append(segment_dict)

        ext_less = os.path.splitext(file)[0]
        output_file = open(ext_less + ".transcript.md", "a")
        for segment in segment_list:
            speaker = segment["speaker"]
            text = segment["text"]
            output_file.write(f"[{speaker.strip()}] {text.strip()}\n")
        output_file.close()
