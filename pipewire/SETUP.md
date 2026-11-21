# Better laptop speakers on Linux: Dolby tuning via PipeWire

This guide gets Lenovo's Windows "Dolby" speaker tuning running on a Linux
laptop as a PipeWire filter. No EasyEffects and no GUI. It needs nothing from
this dotfiles repo.

It was set up and verified on a Moto Book 60 14IAH10 (same hardware as the
IdeaPad Slim 5i Gen 10, Conexant SN6140 codec, 2x 2W front-facing speakers) on
Arch Linux with PipeWire. The filter is produced by the
[speaker-tuning-to-easyeffects](https://github.com/antoinecellerier/speaker-tuning-to-easyeffects)
project, which reads the tuning from your laptop's own Windows audio driver.

## What you get

A processing chain on the built-in speakers only (headphones and HDMI are left
alone):

1. A convolver that applies Lenovo's speaker-correction curve.
2. A 200 Hz high-pass that protects the small drivers.
3. A per-band limiter with a +6 dB loudness boost, then a final limiter.

On this laptop it gave less sub-bass, more midrange and presence, and slightly
more loudness. It is clearer, not bassier. Expect that trade-off.

## Requirements

- A PipeWire + WirePlumber system.
- A Lenovo-tuned laptop with a Dolby tuning file in its Windows driver. The
  project lists confirmed models in its README. Other brands (ASUS, Framework,
  Microsoft Surface) are supported by the same tool but need their own driver
  download.
- Python 3 with NumPy and SciPy, `git`, `innoextract` (to unpack Lenovo's
  driver `.exe`) and the LSP LV2 plugins.

Install the dependencies:

```bash
# Arch
sudo pacman -S --needed python-numpy python-scipy innoextract lsp-plugins git

# Debian / Ubuntu (names may differ by release)
sudo apt install python3-numpy python3-scipy innoextract lsp-plugins-lv2 git

# Fedora (names may differ by release)
sudo dnf install python3-numpy python3-scipy innoextract lsp-plugins-lv2 git
```

Optional: `lv2info` (`lilv-tools` on Arch) lets the converter check that the
LSP plugins are present before it changes anything.

## 1. Check your hardware

```bash
cat /sys/class/dmi/id/sys_vendor /sys/class/dmi/id/product_name
cat /proc/asound/card*/codec* | grep -E "Codec:|Subsystem Id"
```

Note the speaker codec and its subsystem ID. Mine was `Conexant SN6140` with
subsystem `0x17aa3841`. On a Lenovo laptop, `product_name` is the 4-character
machine type, such as `83HT`.

## 2. Get the converter

```bash
git clone https://github.com/antoinecellerier/speaker-tuning-to-easyeffects /tmp/stte
cd /tmp/stte
```

## 3. Download your laptop's tuning

On a Lenovo laptop, the fetcher finds, downloads and checksum-verifies the audio
driver for your machine type, then unpacks only the tuning files:

```bash
python3 tools/fetch_driver/get_lenovo_dax_xml.py --dry-run   # preview
python3 tools/fetch_driver/get_lenovo_dax_xml.py             # do it
```

If the fetcher says it can't find your machine, pass the type of a sibling model
that shares the same audio driver:

```bash
python3 tools/fetch_driver/get_lenovo_dax_xml.py --machine-type 83HT
```

On this laptop, the machine type `83NY` has no Lenovo catalog because the laptop
is Motorola-branded. The IdeaPad Slim 5 14ARP10 (`83HT`) driver package contains
tuning files for the Moto Book 60 family. The converter then picks the file that
matches your own codec and PCI subsystem IDs. Check that the line it prints,
`Matched tuning XML`, names your codec subsystem (here `SUBSYS_17AA3841`). If
it doesn't, stop: the project's docs warn that a tuning for a different codec
sounds clearly wrong.

Not on a Lenovo? See the project's `docs/getting-the-xml.md` for other vendors,
or pass a mounted Windows partition with `--windows /path/to/Windows`.

## 4. Preview, then install

Preview what it would do. This changes nothing:

```bash
python3 dolby_to_pipewire.py --dry-run
```

Check for the `Matched tuning XML` line, then for
`Correction check passed`. Install it:

```bash
python3 dolby_to_pipewire.py
```

This writes two files into `~/.config/pipewire/pipewire.conf.d/`
(`Dolby_Balanced.conf` and `Dolby_Balanced.irs`) and **restarts PipeWire**, so
audio cuts out for a moment. It never needs root and refuses to run under
`sudo`.

If you use EasyEffects, quit it and turn off its autostart. Otherwise two
chains process the audio at once.

## 5. Use it

Nothing to select. The filter attaches itself to the built-in speakers and
loads every time PipeWire starts. Keep the speakers as your output device.
Selecting the `Dolby-Balanced` sink in your volume menu would only add a second
volume control.

Check it loaded:

```bash
wpctl status | grep -i dolby
python3 dolby_to_pipewire.py --doctor     # should end "No blocking problems detected."
```

If no `Dolby_Balanced` sink appears after the restart, the LSP plugins are
usually missing (see Requirements).

## Comparing before and after

To switch quickly without re-running scripts, install the three voicings as
separate outputs instead:

```bash
python3 dolby_to_pipewire.py --uninstall --yes
python3 dolby_to_pipewire.py --variant all --target-sink ''
```

You then get `Dolby-Balanced`, `Dolby-Detailed` and `Dolby-Warm` next to your
plain speakers. Switch with your sound menu or:

```bash
wpctl set-default effect_input.Dolby_Balanced
```

Match the loudness when you compare, since the filter is about 1 dB louder and
louder always sounds better. When you've picked one, remove them and install it
the normal way (step 4).

## Tweaking

Re-run the converter with extra flags, which can be combined:

| Problem | Flag |
|---|---|
| Loud parts sound crushed | `--disable volmax` |
| Volume wobbles or surges | `--disable regulator` |
| Loudest moments feel clamped | `--disable coupled-bands` |
| Sounds thin (experimental) | `--enable virtual-bass` |
| Voices hard to follow | `--enable dialog` |
| Quieter than Windows | `--enable level-restore` (can crackle on loud content) |
| Warmer or brighter shape | `--variant warm` or `--variant detailed` |

## Undo

```bash
cd /tmp/stte && python3 dolby_to_pipewire.py --uninstall
```

It lists what it will remove and asks first, then restarts PipeWire. To bypass
temporarily, move `~/.config/pipewire/pipewire.conf.d/Dolby_Balanced.conf`
elsewhere and run
`systemctl --user restart pipewire pipewire-pulse wireplumber`.

## Dotfiles tip

The generated `.conf` refers to its `.irs` file by absolute path. If you keep
`~/.config/pipewire` in a dotfiles repo, link the whole folder to the same place
on every machine (the path is `~/.config/pipewire/pipewire.conf.d/`), or
regenerate the config on each machine.

## Troubleshooting

- **No sound difference:** run `--doctor`. The project's `docs/troubleshooting.md`
  has a section on the PipeWire filter-chain.
- **Sound is gone after a reboot:** `--doctor` reports whether the filter loaded.
- **Filter also plays on headphones:** `--doctor` says what to change.
- **No tuning for your laptop:** open a device report on the project's GitHub.
  Without a tuning file there is nothing to convert, but you can still use
  EasyEffects with a community preset such as
  [JackHack96's presets](https://github.com/JackHack96/EasyEffects-Presets). A
  high-pass near 130 Hz is a good starting point for 2W speakers, and don't
  boost anything below about 60 Hz.
