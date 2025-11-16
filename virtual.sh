#!/usr/bin/env bash
# virtual speaker
pactl load-module module-null-sink sink_name=VirtualBlaster01 channel_map=front-left,front-right
# virtual mic
#pactl load-module module-null-sink media.class=Audio/Source/Virtual sink_name=MicBlaster01 channel_map=front-left,front-right
pactl load-module module-null-sink media.class=Audio/Source/Virtual sink_name=MicBlaster01 channel_map=front-left
