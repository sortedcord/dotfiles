#!/usr/bin/env python3
"""Build a GTK theme from the local Kitty palette; does not activate it."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
SOURCE = Path.home() / '.config/kitty/colors.conf'
palette = {}
for line in SOURCE.read_text().splitlines():
    match = re.fullmatch(r'\s*(\w+)\s+(#[0-9a-fA-F]{6})\s*', line)
    if match:
        palette[match[1]] = match[2]

bg = palette['background']
surface = palette['color0']
fg = palette['color15']
muted = palette['foreground']
border = palette['color8']
accent = palette['color4']
purple = palette['color5']
error = palette['color1']
success = palette['color2']
warning = palette['color3']

colors = {
    'theme_bg_color': bg, 'theme_fg_color': fg,
    'theme_base_color': bg, 'theme_text_color': fg,
    'theme_selected_bg_color': accent, 'theme_selected_fg_color': bg,
    'theme_unfocused_bg_color': bg, 'theme_unfocused_fg_color': muted,
    'theme_unfocused_base_color': bg, 'theme_unfocused_text_color': muted,
    'theme_unfocused_selected_bg_color': border,
    'theme_unfocused_selected_fg_color': fg,
    'insensitive_bg_color': surface, 'insensitive_fg_color': muted,
    'insensitive_base_color': bg, 'borders': border,
    'unfocused_borders': surface,
    'warning_color': warning, 'error_color': error, 'success_color': success,
    'link_color': accent, 'link_visited_color': purple,
    'accent_bg_color': accent, 'accent_fg_color': bg, 'accent_color': accent,
    'destructive_bg_color': error, 'destructive_fg_color': bg,
    'destructive_color': error,
    'success_bg_color': success, 'success_fg_color': bg,
    'warning_bg_color': warning, 'warning_fg_color': bg,
    'error_bg_color': error, 'error_fg_color': bg,
    'window_bg_color': bg, 'window_fg_color': fg,
    'view_bg_color': bg, 'view_fg_color': fg,
    'headerbar_bg_color': surface, 'headerbar_fg_color': fg,
    'headerbar_border_color': border, 'headerbar_backdrop_color': bg,
    'headerbar_shade_color': 'rgba(0, 0, 0, 0.24)',
    'headerbar_darker_shade_color': 'rgba(0, 0, 0, 0.4)',
    'sidebar_bg_color': surface, 'sidebar_fg_color': fg,
    'sidebar_backdrop_color': surface,
    'sidebar_border_color': border, 'sidebar_shade_color': 'rgba(0, 0, 0, 0.24)',
    'secondary_sidebar_bg_color': bg, 'secondary_sidebar_fg_color': fg,
    'secondary_sidebar_backdrop_color': bg,
    'secondary_sidebar_border_color': border,
    'secondary_sidebar_shade_color': 'rgba(0, 0, 0, 0.24)',
    'card_bg_color': surface, 'card_fg_color': fg,
    'card_shade_color': 'rgba(0, 0, 0, 0.24)',
    'dialog_bg_color': surface, 'dialog_fg_color': fg,
    'popover_bg_color': surface, 'popover_fg_color': fg,
    'popover_shade_color': 'rgba(0, 0, 0, 0.24)',
    'thumbnail_bg_color': surface, 'thumbnail_fg_color': fg,
    'shade_color': 'rgba(0, 0, 0, 0.24)',
    'scrollbar_outline_color': bg,
}
header = '/* Generated from ~/.config/kitty/colors.conf by build.py. */\n'
named = '\n'.join(f'@define-color {name} {value};' for name, value in colors.items()) + '\n'

# Restrict overrides to UI surfaces; never set colors on every widget, which
# would also break application content, symbolic icons, and semantic states.
shared = f'''
.background {{ background-color: {bg}; color: {fg}; }}
headerbar, .titlebar, toolbar, .toolbar {{
  background-image: none; background-color: {surface}; color: {fg};
  border-color: {border};
}}
.view, textview text, treeview.view, iconview {{
  background-color: {bg}; color: {fg};
}}
entry, spinbutton:not(.vertical), searchentry {{
  background-image: none; background-color: {bg}; color: {fg};
  border-color: {border}; caret-color: {fg};
}}
entry:focus, entry:focus-within {{ border-color: {accent}; }}
button:not(.flat):not(.suggested-action):not(.destructive-action) {{
  background-image: none; background-color: {surface}; color: {fg};
  border-color: {border}; text-shadow: none;
}}
button:not(.flat):not(.suggested-action):not(.destructive-action):hover {{
  background-color: {border};
}}
button:checked, button:active, button.suggested-action {{
  background-image: none; background-color: {accent}; color: {bg};
}}
button.destructive-action {{
  background-image: none; background-color: {error}; color: {bg};
}}
button:disabled, entry:disabled {{ color: {muted}; }}
selection, textview text selection, entry selection,
.view:selected, row:selected, flowboxchild:selected {{
  background-color: {accent}; color: {bg};
}}
.sidebar, placessidebar, .navigation-sidebar {{
  background-color: {surface}; color: {fg};
}}
menu, .menu, popover.background, popover > contents {{
  background-color: {surface}; color: {fg}; border-color: {border};
}}
menuitem:hover {{ background-color: {border}; }}
notebook > header {{ background-color: {surface}; border-color: {border}; }}
notebook > header tab:checked {{ background-color: {bg}; color: {fg}; }}
notebook > header tab {{ color: {muted}; }}
separator {{ background-color: {border}; min-width: 1px; min-height: 1px; }}
progressbar progress, scale highlight {{ background-color: {accent}; border-color: {accent}; }}
progressbar trough, scale trough {{ background-color: {surface}; border-color: {border}; }}
scrollbar {{ background-color: {bg}; }}
scrollbar slider {{ background-color: {border}; }}
scrollbar slider:hover {{ background-color: {muted}; }}
tooltip, tooltip.background {{ background-color: {surface}; color: {fg}; }}
label.dim-label, .dim-label {{ color: {muted}; opacity: 1; }}
*:link {{ color: {accent}; }}
*:visited {{ color: {purple}; }}
.warning {{ color: {warning}; }}
.error {{ color: {error}; }}
.success {{ color: {success}; }}
'''

for version, resource in (
    ('3.0', 'Adwaita/gtk-contained-dark.css'),
    ('4.0', 'Default/Default-dark.css'),
):
    directory = ROOT / f'gtk-{version}'
    directory.mkdir(exist_ok=True)
    variables = ''
    if version == '4.0':
        # libadwaita 1.6+ uses CSS variables; old releases use named colors.
        variables = '\n:root {\n' + ''.join(
            f'  --{name.replace("_", "-")}: {value};\n'
            for name, value in colors.items()
            if not name.startswith(('theme_', 'insensitive_', 'unfocused_'))
        ) + '}\n'
    overrides = header + named + variables + shared
    (directory / 'palette.css').write_text(overrides)
    theme = f'@import url("resource:///org/gtk/libgtk/theme/{resource}");\n' + overrides
    (directory / 'gtk.css').write_text(theme)
    (directory / 'gtk-dark.css').write_text('@import url("gtk.css");\n')

(ROOT / 'index.theme').write_text('''[Desktop Entry]
Type=X-GNOME-Metatheme
Name=Wedgewood
Comment=Wedgewood palette from Kitty

[X-GNOME-Metatheme]
GtkTheme=Wedgewood
''')
print(f'Built GTK 3/4 theme in {ROOT}')
