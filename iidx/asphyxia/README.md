# duel0213 Asphyxia IIDX to Batch Manual

> Important, this is only compatible with [duel's Asphyxia plugin](https://github.com/duel0213/asphyxia-plugins). If you use something else it probably won't work as save formats differ.

# Get Score file
1. Go to the Web UI and select IIDX
2. Select `Profiles`
3. Select `Data`
4. Choose `Score Export`
5. If a page opens instead of a file downloading, hit `CTRL+S` and save it somewhere

Command Line Arguments
- `-f, --file` (required): Path to your Asphyxia score export JSON file
- `-so, --sp-output`: Output filename for Single Play scores (default: `iidx_scores_sp.json`)
- `-do, --dp-output`: Output filename for Double Play scores (default: `iidx_scores_dp.json`)
- `-s, --service`: Service description shown on Tachi (default: `"beatmania IIDX Asphyxia Export"`)

Output

The script generates two separate JSON files:

- **SP file**: Contains all Single Play scores (NORMAL, HYPER, ANOTHER, LEGGENDARIA)
- **DP file**: Contains all Double Play scores (DP NORMAL, DP HYPER, DP ANOTHER, DP LEGGENDARIA)
