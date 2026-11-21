# PipeWire speaker tuning

`pipewire.conf.d/Dolby_Balanced.{conf,irs}` is Lenovo's Dolby tuning for this
laptop (Moto Book 60 14IAH10 / IdeaPad Slim 5i Gen 10, Conexant SN6140
`17aa:3841`), converted by
[speaker-tuning-to-easyeffects](https://github.com/antoinecellerier/speaker-tuning-to-easyeffects).
It attaches to the built-in speakers automatically; headphones and HDMI are
unaffected. Keep the speakers selected as the output.

Source: Lenovo driver for machine type 83HT (IdeaPad Slim 5 14ARP10), XML
`DEV_1F87_SUBSYS_17AA3841_PCI_SUBSYS_382917AA.xml`.

Needs the LSP LV2 plugins (`lsp-plugins`).

Standalone setup guide for other machines: [SETUP.md](SETUP.md).

## Regenerate

```
git clone https://github.com/antoinecellerier/speaker-tuning-to-easyeffects /tmp/stte
cd /tmp/stte
python3 tools/fetch_driver/get_lenovo_dax_xml.py --machine-type 83HT   # needs innoextract
python3 dolby_to_pipewire.py                                           # needs python-scipy
```

Tweaks if something sounds off: `--disable volmax`, `--disable regulator`,
`--enable virtual-bass`, `--enable dialog`, `--variant warm|detailed`.
Remove with `python3 dolby_to_pipewire.py --uninstall`.

## Bypass without uninstalling

Move `pipewire.conf.d/Dolby_Balanced.conf` elsewhere and run
`systemctl --user restart pipewire pipewire-pulse wireplumber`.
