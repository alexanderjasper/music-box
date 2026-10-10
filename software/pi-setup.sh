#!/usr/bin/env bash
# One-off OS tweaks for the box's Pi. Safe to run again.
#
# Usage (on the Pi):  sudo bash ~/software/pi-setup.sh
set -euo pipefail

# Keep the journal across reboots. Raspberry Pi OS keeps it in RAM only, so the
# reboot that fixes a misbehaving box also erases the log of what went wrong.
# Capped, so the SD card isn't worn by an ever-growing log.
mkdir -p /etc/systemd/journald.conf.d
cat > /etc/systemd/journald.conf.d/90-musicbox-persistent.conf <<'EOF'
[Journal]
Storage=persistent
SystemMaxUse=50M
EOF
systemctl restart systemd-journald
journalctl --flush

# Wi-Fi power saving off for good. The unit's `iw ... power_save off` only runs
# when the service starts; NetworkManager turns power saving back on whenever
# the Wi-Fi reconnects, and the idle Pi then drops the packets Sonos answers with.
# 2 = disable.
cat > /etc/NetworkManager/conf.d/90-musicbox-wifi-powersave.conf <<'EOF'
[connection]
wifi.powersave = 2
EOF
systemctl reload NetworkManager
nmcli -t -f NAME,TYPE connection show --active | awk -F: '$2 ~ /wireless/ {print $1}' |
  while read -r con; do nmcli connection modify "$con" 802-11-wireless.powersave 2; done

echo "done: persistent journal, Wi-Fi power saving disabled"
