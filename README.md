# PipeWire Scripts

A collection of personal scripts for managing PipeWire audio, packaged with Nix for reproducible, dependency-managed execution.

## Scripts

- `find_by_media_name.sh`: Finds a PipeWire node ID by its `media.name` property.
- `find_by_node_desc.sh`: Finds a PipeWire node ID by its `node.description`.
- `find_by_node_desc_capture_group.sh`: Finds a PipeWire node ID by `node.description` and `port.group`.
- `monitor.sh`: Monitors audio levels from a URL using `ffmpeg`.
- `sum_flacs.py`: Calculates the total duration of audio files in the current directory.
- `toggle_mute.sh`: Toggles mute for a specific PipeWire node.
- `virtual.sh`: Creates virtual audio sinks and sources using `pactl`.

## Usage

These scripts are designed for a Linux environment with PipeWire.

### With Nix (Recommended)

Run scripts with Nix-managed dependencies:

```bash
nix run .#toggle_mute
nix run .#find_by_media_name -- "My Device"
nix run .#sum_flacs
```

Install a script to your profile:

```bash
nix profile install .#toggle_mute
```

### Without Nix

Make scripts executable and run them directly:

```bash
chmod +x scripts/*.sh scripts/*.py
./scripts/toggle_mute.sh
./scripts/find_by_media_name.sh "My Device"
./scripts/sum_flacs.py
```

You'll need to install dependencies manually.

## Dependencies

### Nix
All dependencies are managed via `flake.nix`. See the flake for the complete dependency mapping.

### Manual Installation
- `pw-dump` and `pw-cli` (from PipeWire)
- `jq`
- `ffmpeg` and `ffprobe`
- `pactl` (from PulseAudio)
- `python3` (for `sum_flacs.py`)

## License

This project is licensed under the MIT License.
