#!/usr/bin/env python3
"""Link the Tokyo Night Storm .qbtheme into ~/.config/qBittorrent/themes and enable it."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
BUNDLE = ROOT / 'tokyo-night-storm.qbtheme'
QBT_DIR = Path.home() / '.config' / 'qBittorrent'
THEMES_DIR = QBT_DIR / 'themes'
LINK = THEMES_DIR / 'tokyo-night-storm.qbtheme'
CONF = QBT_DIR / 'qBittorrent.conf'


def update_conf(conf_path: Path, theme_path: Path) -> None:
    updates = {
        'General\\UseCustomUITheme': 'true',
        'General\\CustomUIThemePath': str(theme_path),
    }
    if not conf_path.exists():
        conf_path.parent.mkdir(parents=True, exist_ok=True)
        lines = ['[Preferences]'] + [f'{k}={v}' for k, v in updates.items()]
        conf_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
        return

    lines = conf_path.read_text(encoding='utf-8').splitlines()
    out = []
    in_prefs = False
    found_prefs = False
    seen = set()

    for line in lines:
        section_match = re.match(r'^\s*\[([^\]]+)\]\s*$', line)
        if section_match:
            if in_prefs:
                insert_at = len(out)
                while insert_at > 0 and out[insert_at - 1] == '':
                    insert_at -= 1
                new_lines = [f'{k}={v}' for k, v in updates.items() if k not in seen]
                out[insert_at:insert_at] = new_lines
                seen.update(updates.keys())
            in_prefs = section_match.group(1) == 'Preferences'
            if in_prefs:
                found_prefs = True
            out.append(line)
            continue

        if in_prefs and '=' in line:
            key = line.split('=', 1)[0].strip()
            if key in updates:
                out.append(f'{key}={updates[key]}')
                seen.add(key)
                continue

        out.append(line)

    if in_prefs:
        for k, v in updates.items():
            if k not in seen:
                out.append(f'{k}={v}')
    elif not found_prefs:
        if out and out[-1] != '':
            out.append('')
        out.append('[Preferences]')
        for k, v in updates.items():
            out.append(f'{k}={v}')

    conf_path.write_text('\n'.join(out) + '\n', encoding='utf-8')


def main() -> None:
    if not BUNDLE.exists():
        raise SystemExit(f'Missing theme bundle: {BUNDLE}')

    THEMES_DIR.mkdir(parents=True, exist_ok=True)
    if LINK.is_symlink():
        if LINK.resolve() != BUNDLE:
            LINK.unlink()
            LINK.symlink_to(BUNDLE)
    elif LINK.exists():
        raise SystemExit(f'Refusing to replace existing file: {LINK}')
    else:
        LINK.symlink_to(BUNDLE)

    update_conf(CONF, LINK)
    print(f'Activated qBittorrent theme: {LINK}')
    print(f'Updated {CONF} (restart qBittorrent to apply)')


if __name__ == '__main__':
    main()
