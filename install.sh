#!/usr/bin/env bash
# Symlink the dotfiles into the config directory (default: ~/.config).
# Any existing file/folder/symlink at a target path is renamed to <name>.old first.
# Set TARGET to override the destination, e.g. TARGET=/tmp/test ./install.sh
# The GTK theme and the system keyd config (/etc/keyd) are only installed when TARGET is not overridden.
# Also installs the GTK theme (gtk-theme-tokyo-night) via its activate.py.
set -euo pipefail

DOTFILES="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_GTK=1
INSTALL_SYSTEM=1
if [ -n "${TARGET:-}" ]; then INSTALL_GTK=0; INSTALL_SYSTEM=0; fi
TARGET="${TARGET:-$HOME/.config}"

ITEMS=(
  kitty
  mako
  niri
  yazi
  zellij
  nvim
  quickshell
  pipewire
  helium-browser-flags.conf
  mimeapps.list
  user-dirs.dirs
)

# Populate the submodules at the latest commit of the branch set in .gitmodules.
git -C "$DOTFILES" submodule update --init --recursive --remote

mkdir -p "$TARGET"
timestamp="$(date +%Y%m%d-%H%M%S)"

for item in "${ITEMS[@]}"; do
  src="$DOTFILES/$item"
  dst="$TARGET/$item"

  if [ ! -e "$src" ]; then
    echo "skip:    $src does not exist"
    continue
  fi

  # Already linked to the right place.
  if [ -L "$dst" ] && [ "$(readlink -f "$dst")" = "$(readlink -f "$src")" ]; then
    echo "ok:      $dst already linked"
    continue
  fi

  # Move anything existing out of the way, never overwriting an earlier .old.
  if [ -e "$dst" ] || [ -L "$dst" ]; then
    old="$dst.old"
    if [ -e "$old" ] || [ -L "$old" ]; then
      old="$dst.old.$timestamp"
    fi
    mv "$dst" "$old"
    echo "renamed: $dst -> $old"
  fi

  ln -s "$src" "$dst"
  echo "linked:  $dst -> $src"
done

# keyd: /etc/keyd is root-owned, so this step uses sudo.
# Existing files there are renamed to <name>.old first, like the user items above.
# Every file in KEYD_FILES is linked into /etc/keyd.
if [ "$INSTALL_SYSTEM" -eq 1 ]; then
  KEYD_FILES=(default.conf rkn80.conf)
  keyd_changed=0
  for keyd_name in "${KEYD_FILES[@]}"; do
    keyd_src="$DOTFILES/keyd/$keyd_name"
    keyd_dst="/etc/keyd/$keyd_name"

    if [ -L "$keyd_dst" ] && [ "$(readlink -f "$keyd_dst")" = "$(readlink -f "$keyd_src")" ]; then
      echo "ok:      $keyd_dst already linked"
      continue
    fi
    if [ -e "$keyd_dst" ] || [ -L "$keyd_dst" ]; then
      keyd_old="$keyd_dst.old"
      if sudo test -e "$keyd_old" || sudo test -L "$keyd_old"; then
        keyd_old="$keyd_dst.old.$timestamp"
      fi
      sudo mv "$keyd_dst" "$keyd_old"
      echo "renamed: $keyd_dst -> $keyd_old"
    fi
    sudo ln -s "$keyd_src" "$keyd_dst"
    echo "linked:  $keyd_dst -> $keyd_src"
    keyd_changed=1
  done
  if [ "$keyd_changed" -eq 1 ]; then
    echo "hint:    run 'sudo keyd reload' to apply the keyd config"
  fi
fi

# Power tuning: power/ files are linked into the system config dirs (uses sudo).
# Same rename-to-.old rule as keyd. Each entry is "<source name>:<destination dir>".
if [ "$INSTALL_SYSTEM" -eq 1 ]; then
  POWER_FILES=(
    99-battery.conf:/etc/sysctl.d
    snd-hda-intel-power.conf:/etc/modprobe.d
    90-pci-runtime-pm.rules:/etc/udev/rules.d
    91-motobook-psr.rules:/etc/udev/rules.d
    motobook-psr:/usr/local/bin
    motobook-psr.service:/etc/systemd/system
  )
  power_changed=0
  for power_entry in "${POWER_FILES[@]}"; do
    power_name="${power_entry%%:*}"
    power_dir="${power_entry#*:}"
    power_src="$DOTFILES/power/$power_name"
    power_dst="$power_dir/$power_name"

    if [ -L "$power_dst" ] && [ "$(readlink -f "$power_dst")" = "$(readlink -f "$power_src")" ]; then
      echo "ok:      $power_dst already linked"
      continue
    fi
    if [ -e "$power_dst" ] || [ -L "$power_dst" ]; then
      power_old="$power_dst.old"
      if sudo test -e "$power_old" || sudo test -L "$power_old"; then
        power_old="$power_dst.old.$timestamp"
      fi
      sudo mv "$power_dst" "$power_old"
      echo "renamed: $power_dst -> $power_old"
    fi
    sudo ln -s "$power_src" "$power_dst"
    echo "linked:  $power_dst -> $power_src"
    power_changed=1
  done
  if [ "$power_changed" -eq 1 ]; then
    echo "hint:    run 'sudo sysctl --system && sudo udevadm control --reload && sudo systemctl daemon-reload && sudo udevadm trigger --subsystem-match=pci --subsystem-match=power_supply --action=add' to apply power tuning now, or reboot"
  fi
fi

# GTK theme: links ~/.local/share/themes/TokyoNightKitty to the repo and
# applies it (sets GTK 3/4 settings and CSS, backs up the previous ones).
if [ "$INSTALL_GTK" -eq 1 ]; then
  gtk_dir="$DOTFILES/gtk-theme-tokyo-night"
  gtk_link="$HOME/.local/share/themes/TokyoNightKitty"

  if [ -L "$gtk_link" ] && [ "$(readlink -f "$gtk_link")" = "$(readlink -f "$gtk_dir")" ]; then
    echo "ok:      GTK theme already installed"
  else
    # A dangling link (e.g. the project was moved) must go before activate.py can recreate it.
    if [ -L "$gtk_link" ] && [ ! -e "$gtk_link" ]; then
      rm "$gtk_link"
      echo "removed: broken GTK theme link $gtk_link"
    fi
    python3 "$gtk_dir/activate.py"
  fi
fi
