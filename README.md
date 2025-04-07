# more-tachi-import-scripts
Some scripts to convert from various sources to Tachi/Kamaitachi "Batch Manual" import jsons.
Use with caution as there may be some cases missing.

- [SDVX e-amusement CSV (with limited Session/Date data)](./sdvx/eamuse_csv)
- [CHUNITHM AquaDX (Online Hosted) User Data Export JSON](./chuni/aquadx)
- [maimai DX AquaDX (Online Hosted) User Data Export JSON](./mai2/aquadx)
- [O.N.G.E.K.I AquaDX (Online Hosted) API recently played (no export functionality in AquaNet yet)](./mu3/aquadx)
- [WACCA AquaDX (Online Hosted) API recently played (no export functionality in AquaNet yet)](./wacca/aquadx)


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
