#!/usr/bin/env bash
# Show an image in imv on the left half of the screen (Hyprland). Closes the earlier imv windows.
set -u
pkill -x imv 2>/dev/null
setsid imv "$1" >/dev/null 2>&1 &
for _ in $(seq 20); do
  sleep 0.2
  [ "$(hyprctl activewindow -j | python3 -c 'import json,sys; print(json.load(sys.stdin).get("class"))')" = imv ] && break
done
hyprctl dispatch 'hl.dsp.window.float({ action = "enable" })' >/dev/null
hyprctl dispatch 'hl.dsp.window.resize({ x = 1270, y = 1400 })' >/dev/null
hyprctl dispatch 'hl.dsp.window.move({ x = 4, y = 30 })' >/dev/null
