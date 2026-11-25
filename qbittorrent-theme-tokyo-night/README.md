# Tokyo Night Storm — qBittorrent

A static `.qbtheme` bundle for qBittorrent v5+ based on `kitty/colors.conf`, with light-colored SVG icons and controls.

## Files

- `config.json`: Qt palette, transfer list state colors, log colors, RSS colors, and pieces/progress bar colors.
- `stylesheet.qss`: Qt6 stylesheet for widgets, menus, toolbars, tabs, inputs, scrollbars, and views.
- `icons/`: Light-colored SVG icons derived from qBittorrent's icon set (`icons/dark/qbittorrent-tray-mono.svg` for dark-panel tray).
- `controls/`: Light-colored SVG checkboxes, radio buttons, arrows, and tree branch indicators.
- `resources.qrc`: Qt resource manifest.
- `tokyo-night-storm.qbtheme`: Compiled binary Qt resource bundle.
- `activate.py`: Symlinks `tokyo-night-storm.qbtheme` into `~/.config/qBittorrent/themes/` and enables it in `~/.config/qBittorrent/qBittorrent.conf`.

## Install

Run `./install.sh` from the dotfiles root, or run directly:

```sh
python3 ~/Projects/dotfiles/qbittorrent-theme-tokyo-night/activate.py
```

Restart qBittorrent after activating (if qBittorrent is running when `qBittorrent.conf` is edited, quit it first or re-run `activate.py` after quitting so it does not overwrite the config on exit).

## Transparency (niri)

Qt6 `QMainWindow` does not enable `WA_TranslucentBackground` from QSS alone, so wallpaper transparency is handled by niri in `niri/window-rules.kdl` (`opacity 0.88`) and `niri/config.kdl` (`draw-border-with-background false`) for `app-id="^org\.qbittorrent\.qBittorrent$"`.

## Rebuild `.qbtheme`

If you edit `config.json`, `stylesheet.qss`, or any SVG:

```sh
/usr/lib/qt6/rcc --binary resources.qrc -o tokyo-night-storm.qbtheme
```

## Palette mapping

| Surface | Kitty color | Hex |
| --- | --- | --- |
| Window & list background | background | `#0e1017` |
| Alternating row background | — | `#161925` |
| Toolbar headers, buttons, menus, tooltips | color0 | `#24283B` |
| Borders & scrollbar handles | color8 | `#444B6A` |
| Muted text, paused/stalled states | foreground | `#787C99` |
| Primary text & UI icons | color15 | `#D5D6DB` |
| Accent, selection, uploading | color4 | `#8698df` |
| Downloading & connected | color2 | `#41A6B5` |
| Queued, moving, warnings | color3 | `#E0AF68` |
| Checking & stopped seeding | color5 | `#BB9AF7` |
| Errors & missing files | color1 | `#F7768E` |
