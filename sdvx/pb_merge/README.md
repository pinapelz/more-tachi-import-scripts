# e-amusement PB de-duplicator
This script takes in a e-amusement SDVX CSV and generates a new CSV with only UNIQUE PBs (aka doesn't already exist on Tachi). This is done by looking up your player info on Tachi.

| Argument              | Short | Long        | Required | Default                           | Description                              |
|-----------------------|-------|-------------|----------|-----------------------------------|------------------------------------------|
| `file`                | `-f`  | `--file`    | ✅ Yes   | –                                 | SOUND VOLTEX score CSV (`score.csv`)      |
| `output`              | `-o`  | `--output`  | ❌ No    | `merged_sdvx_scores.csv`          | Output filename                          |
| `tachi`               | `-t`  | `--tachi`   | ❌ No    | `https://kamai.tachi.ac`          | API URL for your Tachi instance          |
| `username`            | `-u`  | `--username`| ❌ No    | `""` (empty string)               | Your unique username on Tachi            |
