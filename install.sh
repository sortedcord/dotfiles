#!/usr/bin/env bash
# Symlink the dotfiles into the config directory (default: ~/.config).
# Any existing file/folder/symlink at a target path is renamed to <name>.old first.
# Set TARGET to override the destination, e.g. TARGET=/tmp/test ./install.sh
# The GTK theme is only installed when TARGET is not overridden.
# Also installs the GTK theme (gtk-theme-tokyo-night) via its activate.py.
set -euo pipefail

DOTFILES="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_GTK=1
if [ -n "${TARGET:-}" ]; then INSTALL_GTK=0; fi
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
