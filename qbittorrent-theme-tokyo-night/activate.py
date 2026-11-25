#!/usr/bin/env python3
"""Build the translucent Qt6 style plugin, link the .qbtheme, and enable both for qBittorrent."""
from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent
BUNDLE = ROOT / 'tokyo-night-storm.qbtheme'
STYLE_SRC = ROOT / 'style' / 'tokyonightstyle.cpp'
STYLE_META = ROOT / 'style' / 'tokyonight.json'

HOME = Path.home()
PLUGIN_ROOT = HOME / '.local' / 'lib' / 'qt6' / 'plugins'
PLUGIN_SO = PLUGIN_ROOT / 'styles' / 'libtokyonightstyle.so'
ENV_CONF = HOME / '.config' / 'environment.d' / 'qt6-plugins.conf'

QBT_DIR = HOME / '.config' / 'qBittorrent'
THEMES_DIR = QBT_DIR / 'themes'
LINK = THEMES_DIR / 'tokyo-night-storm.qbtheme'
CONF = QBT_DIR / 'qBittorrent.conf'
SYS_DESKTOP = Path('/usr/share/applications/org.qbittorrent.qBittorrent.desktop')
USER_DESKTOP = HOME / '.local' / 'share' / 'applications' / 'org.qbittorrent.qBittorrent.desktop'


def build_style_plugin() -> None:
    PLUGIN_SO.parent.mkdir(parents=True, exist_ok=True)
    if PLUGIN_SO.exists():
        so_mtime = PLUGIN_SO.stat().st_mtime
        if so_mtime >= STYLE_SRC.stat().st_mtime and so_mtime >= STYLE_META.stat().st_mtime:
            return

    moc = '/usr/lib/qt6/moc'
    cflags_libs = subprocess.check_output(
        ['pkg-config', '--cflags', '--libs', 'Qt6Widgets'], text=True
    ).split()

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        moc_out = tmp_dir / 'tokyonightstyle.moc'
        subprocess.run([moc, str(STYLE_SRC), '-o', str(moc_out)], check=True)
        subprocess.run(
            [
                'g++', '-std=c++17', '-O2', '-fPIC', '-shared',
                f'-I{tmp_dir}', f'-I{STYLE_SRC.parent}',
                str(STYLE_SRC), '-o', str(PLUGIN_SO),
                *cflags_libs,
            ],
            check=True,
        )
    print(f'Built Qt6 style plugin: {PLUGIN_SO}')


def ensure_env_conf() -> None:
    ENV_CONF.parent.mkdir(parents=True, exist_ok=True)
    desired = f'QT_PLUGIN_PATH={PLUGIN_ROOT}\n'
    if not ENV_CONF.exists() or ENV_CONF.read_text(encoding='utf-8') != desired:
        ENV_CONF.write_text(desired, encoding='utf-8')
        print(f'Updated {ENV_CONF}')


def ensure_desktop_entry() -> None:
    if not SYS_DESKTOP.exists():
        return
    USER_DESKTOP.parent.mkdir(parents=True, exist_ok=True)
    text = SYS_DESKTOP.read_text(encoding='utf-8')
    updated = re.sub(
        r'^Exec=qbittorrent\b',
        f'Exec=env QT_PLUGIN_PATH={PLUGIN_ROOT} qbittorrent',
        text,
        flags=re.MULTILINE,
    )
    if not USER_DESKTOP.exists() or USER_DESKTOP.read_text(encoding='utf-8') != updated:
        USER_DESKTOP.write_text(updated, encoding='utf-8')
        print(f'Updated {USER_DESKTOP}')


def update_ini_sections(conf_path: Path, section_updates: dict[str, dict[str, str]]) -> None:
    if not conf_path.exists():
        conf_path.parent.mkdir(parents=True, exist_ok=True)
        lines = []
        for section, updates in section_updates.items():
            if lines:
                lines.append('')
            lines.append(f'[{section}]')
            for k, v in updates.items():
                lines.append(f'{k}={v}')
        conf_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
        return

    lines = conf_path.read_text(encoding='utf-8').splitlines()
    out = []
    current_section = None
    seen_sections = set()
    seen_keys: dict[str, set[str]] = {s: set() for s in section_updates}

    def flush_missing(section: str | None) -> None:
        if section and section in section_updates:
            insert_at = len(out)
            while insert_at > 0 and out[insert_at - 1] == '':
                insert_at -= 1
            missing = [
                f'{k}={v}'
                for k, v in section_updates[section].items()
                if k not in seen_keys[section]
            ]
            if missing:
                out[insert_at:insert_at] = missing
                seen_keys[section].update(section_updates[section].keys())

    for line in lines:
        section_match = re.match(r'^\s*\[([^\]]+)\]\s*$', line)
        if section_match:
            flush_missing(current_section)
            current_section = section_match.group(1)
            seen_sections.add(current_section)
            out.append(line)
            continue

        if current_section in section_updates and '=' in line:
            key = line.split('=', 1)[0].strip()
            if key in section_updates[current_section]:
                out.append(f'{key}={section_updates[current_section][key]}')
                seen_keys[current_section].add(key)
                continue

        out.append(line)

    flush_missing(current_section)

    for section, updates in section_updates.items():
        if section not in seen_sections:
            if out and out[-1] != '':
                out.append('')
            out.append(f'[{section}]')
            for k, v in updates.items():
                out.append(f'{k}={v}')

    conf_path.write_text('\n'.join(out) + '\n', encoding='utf-8')


def main() -> None:
    if not BUNDLE.exists():
        raise SystemExit(f'Missing theme bundle: {BUNDLE}')

    build_style_plugin()
    ensure_env_conf()
    ensure_desktop_entry()

    THEMES_DIR.mkdir(parents=True, exist_ok=True)
    if LINK.is_symlink():
        if LINK.resolve() != BUNDLE:
            LINK.unlink()
            LINK.symlink_to(BUNDLE)
    elif LINK.exists():
        raise SystemExit(f'Refusing to replace existing file: {LINK}')
    else:
        LINK.symlink_to(BUNDLE)

    update_ini_sections(
        CONF,
        {
            'Appearance': {
                'Style': 'tokyonight',
            },
            'Preferences': {
                'General\\UseCustomUITheme': 'true',
                'General\\CustomUIThemePath': str(LINK),
            },
        },
    )
    print(f'Activated qBittorrent theme: {LINK}')
    print(f'Updated {CONF} (restart qBittorrent to apply)')


if __name__ == '__main__':
    main()
