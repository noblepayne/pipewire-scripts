#!/usr/bin/env bash
pw-dump | jq ".[] | select(.info.props[\"media.name\"] == \"$1\") | {id, type, media_name: .info.props[\"media.name\"]}.id"
