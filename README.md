# more-tachi-import-scripts
Some scripts to convert from various sources to Tachi/Kamaitachi compatible formats.
Use with caution as there may be some cases missing/not handled.

- [CHUNITHM AquaDX (AquaNet WebUI Export) User Data Export JSON](./chuni/aquadx)
- [maimai DX AquaDX (AquaNet WebUI Export) User Data Export JSON](./mai2/aquadx)
- [O.N.G.E.K.I AquaDX API recently played (no export functionality in AquaNet yet)](./ongeki/aquadx)
- [WACCA AquaDX API recently played (no export functionality in AquaNet yet)](./wacca/aquadx)

- [SDVX e-amusement CSV (with limited Session/Date data)](./sdvx/eamuse_csv)
- [DDR e-amusement scores](./ddr/eamuse)
- [SDVX 22vv0 Asphyxia](./sdvx/asphyxia)
- [jubeat Asphyxia-CZEAve](./jubeat/asphyxia)

**Export from Tachi**
This is useful if you want to use your data on Tachi for something else and you do not have access to DB. Converts scores as shown on the site back to a batch-manual format
- [Universal Tachi to Tachi Userscript](./tachi_to_tachi)

**Tools**
- [SDVX e-amusement CSV PB Deduplication (with limited Session/Date data)](./sdvx/pb_merge)

This script compares a e-amusement exported SDVX score CSV against your scores on Tachi. Then generates a new CSV in the same format with only scores that have not been successfully imported to Tachi.


> [!CAUTION]
> If you are using Kamaitachi or using someone else's Tachi instance please check the rules to ensure that you are complying with the rules before importing your scores!!!

# Usage
All scripts are self-contained and can be run on their own after pip resolves potential dependencies. A global list of dependencies can be found in `requirements.txt`

Windows (Powershell)
```bash
python -m venv venv
./venv/Scripts/activate
pip install -r requirements.txt
```

Linux
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
