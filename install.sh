#!/usr/bin/env bash
# Symlink the dotfiles into the config directory (default: ~/.config).
# Any existing file/folder/symlink at a target path is renamed to <name>.old first.
# Set TARGET to override the destination, e.g. TARGET=/tmp/test ./install.sh
set -euo pipefail

DOTFILES="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="${TARGET:-$HOME/.config}"

ITEMS=(
  kitty
  mako
  niri
  yazi
  zellij
  nvim
  quickshell
  helium-browser-flags.conf
  mimeapps.list
  user-dirs.dirs
)

# Make sure the submodules (nvim, quickshell) are populated.
git -C "$DOTFILES" submodule update --init --recursive

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
