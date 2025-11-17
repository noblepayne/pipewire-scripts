#!/usr/bin/env bash
pw-dump | jq ".[] | select(.info.props[\"node.description\"] == \"$1\") | {id, type, node_description: .info.props[\"node.description\"]}.id"
