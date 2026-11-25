# Wedgewood — Chrome

An unpacked Chrome theme based on `/home/sortedcord/.config/kitty/colors.conf`.
No scripts, permissions, images, or external dependencies.

## Install

1. Open `chrome://extensions` in Chrome.
2. Enable **Developer mode** in the top-right corner.
3. Click **Load unpacked**.
4. Select `/home/sortedcord/Projects/dotfiles/chrome-theme-wedgewood`.
5. Open a new tab to see the theme.

If your Linux browser uses a system/GTK theme, choose the Classic/Chrome appearance in Settings → Appearance before loading this theme. Browser versions may label these options differently.

Keep this directory after installation. After editing `manifest.json`, reload the theme from the extensions page; if no reload control is available, load the directory again.

## Palette mapping

| Surface | Kitty color | Hex |
| --- | --- | --- |
| Window frame, address field, new-tab background | background | `#0e1017` |
| Active tab and toolbar | color0 | `#24283B` |
| Separators | color8 | `#444B6A` |
| Inactive tab text | foreground | `#787C99` |
| Active text and bookmarks | color15 | `#D5D6DB` |
| Toolbar icons and links | color4 | `#8698df` |
| Secondary links and incognito tab text | color5 | `#BB9AF7` |

Active text uses the palette's brighter color15 rather than Kitty's muted foreground for readability. All theme RGB values come directly from the Kitty palette. The theme is a snapshot: changes to the Kitty file are not synchronized automatically.

Chrome controls which surfaces can be themed. Menus, side panels, hover states, and some new-tab elements may use browser-derived colors. A custom new-tab background or a new-tab replacement extension can override the new-tab appearance. This theme does not recolor websites or change the browser's light/dark mode preference.

## Remove

Open Chrome Settings → Appearance and choose **Reset to default** for the theme.

## Reference

Chrome theme format: https://developer.chrome.com/docs/extensions/develop/ui/themes
