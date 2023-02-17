#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# most of the code here is taken from the following Colab notebook:
# https://colab.research.google.com/drive/12W6bR-C6NIEjAML19JubtzHPIlVxdaUq?usp=sharing#scrollTo=q7qMLTISFE6M


# pyannote.audio seems to miss the first 0.5 seconds of the audio, and, therefore, we prepend a spcacer.
from pydub import AudioSegment

spacermilli = 2000
spacer = AudioSegment.silent(duration=spacermilli)


audio = AudioSegment.from_wav("to_transcribe_sample.wav") #lecun1.wav

audio = spacer.append(audio, crossfade=0)

audio.export('audio.wav', format='wav')

from pyannote.audio import Pipeline

pipeline = Pipeline.from_pretrained('pyannote/speaker-diarization', use_auth_token=True)


print("> diarising")
DEMO_FILE = {'uri': 'blabla', 'audio': 'audio.wav'}
dz = pipeline(DEMO_FILE)

with open("diarization.txt", "w") as text_file:
	text_file.write(str(dz))

print("> diarising complete l33")


def millisec(timeStr):
  spl = timeStr.split(":")
  s = (int)((int(spl[0]) * 60 * 60 + int(spl[1]) * 60 + float(spl[2]) )* 1000)
  return s

import re
dzs = open('diarization.txt').read().splitlines()

groups = []
g = []
lastend = 0


print("> grouping diarised")
for d in dzs:
	if g and (g[0].split()[-1] != d.split()[-1]):      #same speaker
		groups.append(g)
		g = []

	g.append(d)

	end = re.findall('[0-9]+:[0-9]+:[0-9]+\.[0-9]+', string=d)[1]
	end = millisec(end)
	if (lastend > end):       #segment engulfed by a previous segment
		groups.append(g)
		g = []
	else:
		lastend = end
if g:
	groups.append(g)
print(*groups, sep='\n')

print("> grouping diarised end l68")

print("> segmenting on groups")
audio = AudioSegment.from_wav("audio.wav")
gidx = -1
for g in groups:
	start = re.findall('[0-9]+:[0-9]+:[0-9]+\.[0-9]+', string=g[0])[0]
	end = re.findall('[0-9]+:[0-9]+:[0-9]+\.[0-9]+', string=g[-1])[1]
	start = millisec(start) #- spacermilli
	end = millisec(end)  #- spacermilli
	print(start, end)
	gidx += 1
	audio[start:end].export(str(gidx) + '.wav', format='wav')


print("> segmenting on groups... end")



print("> run whisper")
# whisper transcription
import os
for i in range(gidx+1):
	os.system("whisper " + str(i) + '.wav' + " --language en --model large")

print("> run whisper... end")


import webvtt

from datetime import timedelta

# speakers = {'SPEAKER_00':('Dyson', 'white', 'darkorange'), 'SPEAKER_01':('Interviewer', '#e1ffc7', 'darkgreen') }
# def_boxclr = 'white'
# def_spkrclr = 'orange'

html = []
gidx = -1
for g in groups:
	shift = re.findall('[0-9]+:[0-9]+:[0-9]+\.[0-9]+', string=g[0])[0]
	shift = millisec(shift) - spacermilli #the start time in the original video
	shift=max(shift, 0)

	gidx += 1
	captions = [[(int)(millisec(caption.start)), (int)(millisec(caption.end)),  caption.text] for caption in webvtt.read(str(gidx) + '.wav.vtt')]

	if captions:
		speaker = g[0].split()[-1]
		# boxclr = def_boxclr
		# spkrclr = def_spkrclr
		# if speaker in speakers:
		# speaker, boxclr, spkrclr = speakers[speaker]
		# html.append(f'<div class="e" style="background-color: {boxclr}">\n');
		# html.append(f'<span style="color: {spkrclr}">{speaker}</span><br>\n')

		for c in captions:
		# start = shift + c[0]

		# start = start / 1000.0   #time resolution ot youtube is Second.
		# startStr = '{0:02d}:{1:02d}:{2:02.2f}'.format((int)(start // 3600),
												# (int)(start % 3600 // 60),
												# start % 60)

			html.append("*" + speaker + ":* " +c[2])


s = "\n".join(html)

with open("capspeaker.html", "w") as text_file:
    text_file.write(s)
