#!/usr/bin/env bash
pw-dump | jq ".[] | select(.info.props[\"node.description\"] == \"$1\" and .info.props[\"port.group\"] == \"capture\") | {id, type, node_description: .info.props[\"node.description\"]}.id"
