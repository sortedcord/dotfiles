# dotfiles

My personal configs for Arch Linux: niri, kitty, mako, yazi, zellij, Neovim, quickshell, Helium browser flags, `mimeapps.list`, and `user-dirs.dirs`.

## Related projects

- **niri fork:** https://github.com/sortedcord/niri (the niri build this config uses)
- **Helium fork (helide):** https://github.com/sortedcord/helide
- **wl-kbptr fork:** https://github.com/sortedcord/wl-kbptr (adds a `mouse` mode: pick a spot, then move the pointer with `h`/`j`/`k`/`l` and click with `f`/`d`/`s` until `Escape`). Bound to `Mod+G` in `niri/keybinds/mouse.kdl`. Build and install it with `meson setup build --buildtype=release -Dopencv=enabled && meson compile -C build && sudo meson install -C build`.
- **Neovim config:** https://github.com/sortedcord/nvimconfig (included as the `nvim/` submodule)
- **Quickshell config:** https://github.com/sortedcord/doalot (included as the `quickshell/` submodule)

## Other things I use

- **Howdy (Moto):** https://github.com/sortedcord/howdy-moto
- **Touchpad enhancements:** https://github.com/sortedcord/touchpad-enhancements
- **keyd:** key remapping config in `keyd/`. The installer links `default.conf` and `rkn80.conf` into `/etc/keyd/` (uses `sudo`). Reload with `sudo keyd reload`.

- **Power tuning:** files in `power/` are linked into the system config directories by `install.sh` (uses `sudo`): `99-battery.conf` to `/etc/sysctl.d/`, `snd-hda-intel-power.conf` to `/etc/modprobe.d/`, and `90-pci-runtime-pm.rules` to `/etc/udev/rules.d/`. They take effect on reboot, or immediately with `sudo sysctl --system && sudo udevadm control --reload && sudo udevadm trigger --subsystem-match=pci --action=add`.

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

It also installs the GTK theme in `gtk-theme-tokyo-night/`. The theme is linked to `~/.local/share/themes/TokyoNightKitty`, and its `activate.py` sets it as the GTK theme. Your previous GTK settings and CSS are backed up to `~/.config/gtk-theme-backup-<timestamp>`. Re-running the script skips this step if the theme is already active. It is skipped entirely when `TARGET` is set.

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
git submodule update --init --recursive --remote --merge
```

`nvim/` tracks `master` and `quickshell/` tracks `main` (set in `.gitmodules`), so `--remote` moves each one to its branch tip instead of the commit recorded earlier. Changes to those submodules are committed and pushed in their own repos first. Then commit the updated submodule pointer here so it records the new commit.

## Credits

- **Flag emojis for Windows:** https://github.com/Chasmical/flag-emojis-for-windows
