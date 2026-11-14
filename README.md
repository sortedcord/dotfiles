# dotfiles

My personal configs for Arch Linux: niri, kitty, mako, yazi, zellij, Neovim, quickshell, Helium browser flags, `mimeapps.list`, and `user-dirs.dirs`.

## Related projects

- **niri fork:** https://github.com/sortedcord/niri (the niri build this config uses)
- **Helium fork (helide):** https://github.com/sortedcord/helide
- **Neovim config:** https://github.com/sortedcord/nvimconfig (included as the `nvim/` submodule)
- **Quickshell config:** https://github.com/sortedcord/doalot (included as the `quickshell/` submodule)

## Clone

Clone with submodules so `nvim/` and `quickshell/` are populated:

```sh
git clone --recurse-submodules git@github.com:sortedcord/dotfiles.git ~/Projects/dotfiles
```

If you already cloned without submodules, fetch them with:

```sh
cd ~/Projects/dotfiles
git submodule update --init --recursive
```

## Install

```sh
cd ~/Projects/dotfiles
./install.sh
```

The script symlinks each item into `~/.config`:

- `kitty`, `mako`, `niri`, `yazi`, `zellij`, `nvim`, `quickshell`
- `helium-browser-flags.conf`, `mimeapps.list`, `user-dirs.dirs`

If a path already exists in `~/.config`, it is renamed to `<name>.old` before the symlink is created. If `<name>.old` is already taken, the script uses `<name>.old.<timestamp>` instead. Re-running the script is safe: items that are already linked are skipped.

To undo, remove the symlink and rename the `.old` back, for example:

```sh
rm ~/.config/kitty && mv ~/.config/kitty.old ~/.config/kitty
```

To test without touching your real config, point the script at another directory:

```sh
TARGET=/tmp/dotfiles-test ./install.sh
```

## Updating

```sh
cd ~/Projects/dotfiles
git pull --recurse-submodules
```

Changes to `nvim/` or `quickshell/` are committed in their own repos. After pushing those, commit the updated submodule pointer in this repo.
