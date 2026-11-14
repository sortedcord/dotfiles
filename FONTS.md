# Fonts

Which fonts this setup uses, where they're referenced, and how emoji fallback works.

## Font families

| Font | Used by | Notes |
| --- | --- | --- |
| FiraCode Nerd Font Mono | Kitty (`kitty/kitty.conf`) | Terminal font, 14pt. Includes Nerd Font icons. |
| FiraCode Nerd Font | Quickshell (`quickshell/core/Theme.qml`, `fontFamily`) | Shell UI font. Proportional variant, not the Mono one. |
| Noto Sans | Mako (`mako/config`) | Notification font, 11pt. |
| monospace | Zellij web client (`zellij/config.kdl`, `web_client`) | Generic alias, not a specific font. Only used when the web client is enabled. |

Install FiraCode Nerd Font from the Arch repos or the Nerd Fonts project. Noto Sans comes from `noto-fonts`.

## Kitty details

`kitty/kitty.conf` sets:

- `font_family FiraCode Nerd Font Mono`
- `bold_font`, `italic_font`, `bold_italic_font` set to `auto`, so Kitty picks matching variants from the same family.
- `font_features FiraCodeNFM-Reg +liga +calt`, which turns on Fira Code ligatures and contextual alternates.

## Emoji fallback

Nerd Fonts don't include color emoji, so emoji fall back through fontconfig. The chain is:

1. **Segoe UI Emoji** (`seguiemj.ttf`) is the primary emoji font. It's installed per-user at `~/.local/share/fonts/seguiemj.ttf`. The installed build is the Segoe UI Emoji with Twemoji Flags file (`Segoe.UI.Emoji.with.Twemoji.Flags.ttf`), which adds flag glyphs and covers Unicode 15 emoji such as the pink, grey, and light blue hearts (U+1FA75–1FA77). It's a proprietary Microsoft font, so it is **not** in this repo and must not be redistributed.
2. **Noto Color Emoji** is the fallback for any characters Segoe UI Emoji lacks. Install it with `sudo pacman -S noto-fonts-emoji`.

Check the resolution with:

```sh
fc-match "Fira Code Nerd Font:charset=1f495"   # expect Segoe UI Emoji
fc-match "Fira Code Nerd Font:charset=1fa77"   # expect Segoe UI Emoji
```

Note that `fc-match emoji` (the generic alias) returns Noto Color Emoji, because the generic alias ranks it first. Apps that use Fira Code's fallback get Segoe first.

Restart Kitty and the browser after installing or changing emoji fonts.

## Setup on a new machine

1. Install FiraCode Nerd Font, Noto Sans (`noto-fonts`), and Noto Color Emoji (`noto-fonts-emoji`).
2. Copy the Segoe UI Emoji with Twemoji Flags file to `~/.local/share/fonts/seguiemj.ttf` (optional).
3. Run `fc-cache -f` and restart Kitty and the browser.
