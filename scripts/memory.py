#!/usr/bin/env python3
"""
Process Memory Tree - visualizes memory usage by process in a tree format
"""
import os
import subprocess
import sys
from collections import defaultdict
from pathlib import Path


def get_process_tree():
    """Get process tree using pstree-like output."""
    try:
        result = subprocess.run(
            ['ps', '-eo', 'pid,ppid,cmd', '--no-headers'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip().split('\n')
    except (FileNotFoundError, subprocess.CalledProcessError):
        return []


def get_process_memory(pid):
    """Get memory usage for a specific process in MB."""
    try:
        with open(f'/proc/{pid}/status') as f:
            for line in f:
                if line.startswith('VmRSS:'):
                    return float(line.split()[1]) / 1024
    except (FileNotFoundError, ValueError):
        pass
    return 0


def shorten_path(cmd, max_len=42):
    """Shorten long nix paths and other long commands."""
    if len(cmd) <= max_len:
        return cmd
    
    # Handle nix store paths - extract the package name
    if '/nix/store/' in cmd:
        # Extract the hash-name part after /nix/store/
        parts = cmd.split('/nix/store/')
        if len(parts) > 1:
            nix_part = parts[1]
            # Format is: hash-name/rest/of/path/binary
            nix_parts = nix_part.split('/')
            if nix_parts:
                # Get hash-name
                hash_name = nix_parts[0]
                # Try to extract just the package name from hash-name
                if '-' in hash_name:
                    pkg_name = hash_name.split('-', 1)[1]  # Remove hash prefix
                    binary = nix_parts[-1]  # Get the binary name
                    short = f"{pkg_name}/{binary}"
                    if len(short) <= max_len:
                        return short
                    # If still too long, just return binary
                    return binary
    
    # Generic fallback: take last component
    if '/' in cmd:
        return cmd.split('/')[-1]
    
    # If still too long, truncate with ellipsis
    if len(cmd) > max_len:
        return cmd[:max_len-1] + '…'
    
    return cmd


def build_tree(ps_output):
    """Build parent-child process tree with memory."""
    tree = defaultdict(list)
    processes = {}
    
    for line in ps_output:
        parts = line.split(None, 2)
        if len(parts) < 3:
            continue
        
        try:
            pid = int(parts[0])
            ppid = int(parts[1])
            cmd = parts[2]
            mem_mb = get_process_memory(pid)
            
            if mem_mb > 0 or ppid == 1:  # Include if using memory or is top-level
                processes[pid] = {
                    'pid': pid,
                    'ppid': ppid,
                    'cmd': cmd.split()[0],
                    'mem_mb': mem_mb,
                }
                tree[ppid].append(pid)
        except (ValueError, IndexError):
            continue
    
    return tree, processes


def format_size(mb):
    """Format memory size nicely."""
    if mb < 1:
        return f"{mb*1024:.0f}K"
    elif mb < 1024:
        return f"{mb:.1f}M"
    else:
        return f"{mb/1024:.1f}G"


def calculate_subtree_memory(pid, tree, processes):
    """Calculate total memory used by process and all children."""
    total = processes.get(pid, {}).get('mem_mb', 0)
    for child_pid in tree.get(pid, []):
        total += calculate_subtree_memory(child_pid, tree, processes)
    return total


def print_tree(pid, tree, processes, prefix="", is_last=True, min_mem=0):
    """Recursively print process tree with memory usage."""
    if pid not in processes:
        return
    
    proc = processes[pid]
    if proc['mem_mb'] < min_mem:
        return
    
    # Build the tree line
    connector = "└── " if is_last else "├── "
    mem_str = format_size(proc['mem_mb'])
    short_cmd = shorten_path(proc['cmd'])
    
    # Build child list to check if there are more
    children = sorted(
        tree[pid],
        key=lambda p: processes.get(p, {}).get('mem_mb', 0),
        reverse=True
    )
    # Filter by min_mem
    children = [c for c in children if processes.get(c, {}).get('mem_mb', 0) >= min_mem]
    
    print(f"{prefix}{connector}{short_cmd:42s} {mem_str:>8s}  (pid {pid})")
    
    # Print children
    extension = "    " if is_last else "│   "
    for i, child_pid in enumerate(children):
        is_last_child = (i == len(children) - 1)
        print_tree(child_pid, tree, processes, prefix + extension, is_last_child, min_mem)


def main():
    min_mem_arg = 0.0
    show_summary = True
    show_tree = True
    
    # Parse arguments
    for arg in sys.argv[1:]:
        if arg in ['--no-summary', '-s']:
            show_summary = False
        elif arg in ['--no-tree', '-t']:
            show_tree = False
        elif arg in ['--help', '-h']:
            print(f"Usage: {sys.argv[0]} [options] [min_memory_mb]")
            print("Options:")
            print("  --no-summary, -s   Hide summary section")
            print("  --no-tree, -t      Hide process tree")
            print("  --help, -h         Show this help")
            sys.exit(0)
        else:
            try:
                min_mem_arg = float(arg)
            except ValueError:
                print(f"Invalid argument: {arg}")
                sys.exit(1)
    
    # Build process tree
    ps_output = get_process_tree()
    if not ps_output:
        print("Error: could not read process information")
        sys.exit(1)
    
    tree, processes = build_tree(ps_output)
    
    if show_summary:
        # Calculate total memory
        total_mem = sum(p['mem_mb'] for p in processes.values())
        
        # Find root processes and calculate their subtree totals
        roots = [p for p in processes if processes[p]['ppid'] == 1]
        root_totals = []
        for root_pid in roots:
            subtree_mem = calculate_subtree_memory(root_pid, tree, processes)
            root_totals.append((root_pid, subtree_mem))
        
        # Unwrap systemd: if systemd's subtree is huge, show its top children instead
        unwrapped = []
        for root_pid, subtree_mem in root_totals:
            proc = processes[root_pid]
            is_systemd = 'systemd' in proc['cmd'] and proc['ppid'] == 1
            
            if is_systemd and subtree_mem > total_mem * 0.5:
                # Systemd dominates - show its direct children instead
                children = tree.get(root_pid, [])
                for child_pid in children:
                    child_subtree = calculate_subtree_memory(child_pid, tree, processes)
                    if child_subtree > 0:
                        unwrapped.append((child_pid, child_subtree))
            else:
                unwrapped.append((root_pid, subtree_mem))
        
        root_totals = sorted(unwrapped, key=lambda x: x[1], reverse=True)
        
        # Print summary
        box_width = 56
        print("╔" + "═" * (box_width - 2) + "╗")
        mem_line = f"Total Memory: {format_size(total_mem)}"
        print(f"║ {mem_line:<{box_width-4}} ║")
        print("╠" + "═" * (box_width - 2) + "╣")
        print("║ Top Processes (with children):".ljust(box_width - 1) + "║")
        print("╠" + "═" * (box_width - 2) + "╣")
        
        for root_pid, subtree_mem in root_totals[:10]:
            proc = processes[root_pid]
            cmd = shorten_path(proc['cmd'], 30)
            mem_str = format_size(subtree_mem)
            pct = (subtree_mem / total_mem * 100) if total_mem > 0 else 0
            line = f"{cmd:30s} {mem_str:>8s} ({pct:5.1f}%)"
            print(f"║ {line:<{box_width-4}} ║")
        
        print("╚" + "═" * (box_width - 2) + "╝")
        print()
    
    if show_tree:
        # Print tree
        roots = sorted(
            [p for p in processes if processes[p]['ppid'] == 1],
            key=lambda p: calculate_subtree_memory(p, tree, processes),
            reverse=True
        )
        
        print(f"{'Process':42s} {'Memory':>8s}  PID")
        print("─" * 69)
        
        for i, root_pid in enumerate(roots):
            is_last = (i == len(roots) - 1)
            print_tree(root_pid, tree, processes, "", is_last, min_mem_arg)


if __name__ == '__main__':
    main()
