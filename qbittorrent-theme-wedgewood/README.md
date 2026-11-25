# Wedgewood — qBittorrent

A static `.qbtheme` bundle for qBittorrent v5+ based on `kitty/colors.conf`, with light-colored SVG icons/controls and background-only translucency (85% background opacity matching Kitty, with 100% opaque text and icons).

## Files

- `config.json`: Qt palette, transfer list state colors, log colors, RSS colors, and pieces/progress bar colors.
- `stylesheet.qss`: Qt6 stylesheet with transparent container backgrounds, translucent surfaces, and opaque text/borders.
- `icons/`: Light-colored SVG icons derived from qBittorrent's icon set (`icons/dark/qbittorrent-tray-mono.svg` for dark-panel tray).
- `controls/`: Light-colored SVG checkboxes, radio buttons, arrows, and tree branch indicators.
- `style/`: Minimal Qt6 `QProxyStyle` plugin (`wedgewood`) that enables `Qt::WA_TranslucentBackground` on top-level windows and paints the 85% `#0e1017` window background without fading text or icons.
- `resources.qrc`: Qt resource manifest.
- `wedgewood.qbtheme`: Compiled binary Qt resource bundle.
- `activate.py`: Builds `libwedgewoodstyle.so` into `~/.local/lib/qt6/plugins/styles/`, writes `~/.config/environment.d/qt6-plugins.conf` and `~/.local/share/applications/org.qbittorrent.qBittorrent.desktop`, symlinks `wedgewood.qbtheme` into `~/.config/qBittorrent/themes/`, and enables both in `~/.config/qBittorrent/qBittorrent.conf`.

## Install

Run `./install.sh` from the dotfiles root, or run directly:

```sh
python3 ~/Projects/dotfiles/qbittorrent-theme-wedgewood/activate.py
```

Restart qBittorrent after activating (if qBittorrent is running when `qBittorrent.conf` is edited, quit it first or re-run `activate.py` after quitting so it does not overwrite the config on exit).

## Transparency (niri + Qt6)

- `style/wedgewoodstyle.cpp` sets `Qt::WA_TranslucentBackground` on top-level windows and paints `rgba(14, 16, 23, 217)` behind `QMainWindow`/`QDialog` while keeping text, icons, and controls 100% opaque.
- `niri/config.kdl` exports `QT_PLUGIN_PATH` and sets `draw-border-with-background false` for `app-id="^org\.qbittorrent\.qBittorrent$"` so the focus ring fill does not show behind the translucent background.

## Rebuild `.qbtheme`

If you edit `config.json`, `stylesheet.qss`, or any SVG:

```sh
/usr/lib/qt6/rcc --binary resources.qrc -o wedgewood.qbtheme
```

## Palette mapping

| Surface | Kitty color | Hex |
| --- | --- | --- |
| Window background (85% alpha) | background | `#d90e1017` |
| Toolbar headers, buttons, menus, tooltips | color0 | `#24283B` |
| Borders & scrollbar handles | color8 | `#444B6A` |
| Muted text, paused/stalled states | foreground | `#787C99` |
| Primary text & UI icons | color15 | `#D5D6DB` |
| Accent, selection, uploading | color4 | `#8698df` |
| Downloading & connected | color2 | `#41A6B5` |
| Queued, moving, warnings | color3 | `#E0AF68` |
| Checking & stopped seeding | color5 | `#BB9AF7` |
| Errors & missing files | color1 | `#F7768E` |
