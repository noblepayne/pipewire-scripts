#!/usr/bin/env sh
ffmpeg -i https://jblive.fm -filter:a ebur128 -f null -
