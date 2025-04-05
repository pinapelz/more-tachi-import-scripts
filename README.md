# more-tachi-import-scripts
Some scripts to convert from various sources to Tachi/Kamaitachi "Batch Manual" import jsons.
Use with caution as there may be some cases missing.

- SDVX e-amusement CSV
- AquaDX (Online Hosted) User Data JSON
- AquaDX (Online Hosted) maimai DX User Data JSON
- AquaDX (Online Hosted) O.N.G.E.K.I API recently played (no export functionality in AquaNet yet)
- AquaDX (Online Hosted) WACCA API recently played (no export functionality in AquaNet yet)


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
