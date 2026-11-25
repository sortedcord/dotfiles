# Wedgewood (GTK)

A user-local GTK 3 / GTK 4 theme generated from `~/.config/kitty/colors.conf`, with libadwaita palette overrides. Builds on the installed GTK dark theme's widget geometry and assets rather than replacing controls from scratch.

## Palette

- Window/content background: Kitty `background` (`#0e1017`)
- Headers, sidebars, buttons, cards: `color0` (`#24283B`)
- Borders and hovered controls: `color8` (`#444B6A`)
- Primary text: `color15` (`#D5D6DB`), for readability
- Secondary text: Kitty `foreground` (`#787C99`)
- Selection and accent: `color4` (`#8698df`), with dark selected text
- Visited links: `color5` (`#BB9AF7`)
- Error/destructive, success, warning: `color1`, `color2`, `color3`

## Activation

Already activated for this user using:

```sh
python3 ~/Projects/dotfiles/gtk-theme-wedgewood/activate.py
```

The installer links `~/.local/share/themes/Wedgewood` to this project, sets the GSettings GTK theme and dark preference, updates GTK 3/4 settings, and imports the generated palette in the user GTK CSS files. Existing settings and CSS are backed up before changes; unrelated settings.ini keys are retained. Existing user CSS is replaced (after backup) to prevent conflicting color overrides.

Keep this project directory in place. Restart applications to pick up all changes; logging out and back in may help apps that cache their settings. No system files, fonts, icon themes, Qt themes, Kitty configuration, or browser themes are changed.

## Regenerate after changing Kitty colors

```sh
python3 ~/Projects/dotfiles/gtk-theme-wedgewood/build.py
```

Restart GTK applications afterward. This is a snapshot, not a live synchronization service.

## Undo

The latest activation backup path is in `last-backup.txt`. Restore it with:

```sh
python3 ~/Projects/dotfiles/gtk-theme-wedgewood/activate.py --restore /path/to/backup
```

This restores the previous desktop settings and GTK settings/CSS, including removing files that did not exist before activation. The now-inactive installed theme and project are retained for reuse. Each activation creates a separate backup; restore older backups in reverse order if needed.

## Compatibility

GTK 3 uses the built-in Adwaita dark stylesheet; GTK 4 uses the built-in Default dark stylesheet. The generated palette supplies both legacy named colors and modern CSS variables used by libadwaita. Widget layouts and assets remain provided by your installed GTK libraries.

Libadwaita does not officially support arbitrary third-party themes. The user CSS override works for many native applications, but apps can override it, and sandboxed Flatpak/Snap apps may not see these host paths. Future GTK/libadwaita versions may require adjustments. Applications using Qt, Electron, or custom rendering are outside this GTK theme's scope.

## Validation

The generated full GTK 3 and GTK 4 stylesheets were loaded through their respective `Gtk.CssProvider` APIs with zero parser diagnostics. A libadwaita window with a header bar, entry, and button was constructed successfully after activation. No visual screenshot verification was performed.

Reference: https://gnome.pages.gitlab.gnome.org/libadwaita/doc/1-latest/css-variables.html
