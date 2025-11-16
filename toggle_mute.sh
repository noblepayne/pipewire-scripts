#!/bin/bash

# Toggle mute for a PipeWire node
# Usage: ./toggle_mute.sh [node_id]
# If no node_id provided, uses the default sink

NODE_ID="${1:-76}"

# Get current mute state
MUTE_STATE=$(pw-dump "$NODE_ID" 2>/dev/null | grep -o '"mute": [^,}]*' | grep -o '[^:]*$' | xargs)

if [ -z "$MUTE_STATE" ]; then
	echo "Error: Node $NODE_ID not found or doesn't support mute control"
	exit 1
fi

# Toggle mute
if [ "$MUTE_STATE" = "true" ]; then
	NEW_STATE="false"
	echo "Unmuting node $NODE_ID"
else
	NEW_STATE="true"
	echo "Muting node $NODE_ID"
fi

# Apply new state
pw-cli set-param "$NODE_ID" Props '{ mute: '$NEW_STATE' }' 2>/dev/null

if [ $? -eq 0 ]; then
	echo "Success!"
else
	echo "Error: Failed to set mute state"
	exit 1
fi
