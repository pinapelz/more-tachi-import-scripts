tl;dr:
- e-amusement doesn't let you see entire play history even with premium
- Web-UI only shows your best scores. If you get a score lower than your best, the score will be lost
- Please keep an old version of your CSV before your play-session (script helps with this) so the script can tell what plays are new
- Limit each session to 20 plays since play timestamp is only available for recent 20

> [!NOTE]
> You must be subscribed to e-amusement Basic Course to use this


# e-amusement SDVX CSV to Tachi WARNING!!!
The CSV provided by Konami doesn't contain any information regarding the date which you played/obtained a particular score. It only keeps your BEST score.

This causes for duplicate imports if you use this script more than once

## Solution
The first time you import, run `sdvx_csv_to_tach.py` and import the output JSON file normally. However **KEEP THE OLD CSV FILE**

The next time you play, export the CSV again but first run `eamuse_merge_csv.py --old <file> --new <file>`. Passing the old and new CSV files accordingly.

This will check for differences between the 2 files and remove lines of the same value in the new file so that only newly obtained best scores are uploaded.

**Run the `sdvx_csv_to_tachi.csv` on the new file created by `eamuse_merge_csv`**

The merge script can automatically handle this process. Choose (y) when prompted

# What if I want all plays?
I don't think there's a method right now to automatically import arcade data into Tachi for each play. Play history is locked behind the eAmusement basic subscription plan.

The best you can do is download the eAmusement app, subscribe the the basic course and manually make your own score CSV in the same format. Then run `sdvx_csv_to_tach.py`

Alternatively, you can take pictures of each play result screen and build your own JSON so that there is even more info available!

# Adding Correct Date Data
The e-amusement WEBUI only provides the time-played for your 20 most recent plays. If you want accurate tracking for session-length please limit each import to 20 plays, otherwise there is no way to know when that score was achieved.

To get this data. Navigate to the e-amusement URL below and press CTRL+S to save the page as HTML. Then pass the filepath to this file as `-d`
```
https://p.eagate.573.jp/game/sdvx/vi/playdata/profile/index.html
```

## Automatically Pulling Date Data
You can do this by passing in `--cookie` instead of a date-file.

> [How to get Cookies?](../../common_docs/how_to_get_cookie_header.md)
>
> Get the cookies from this page: https://p.eagate.573.jp/game/sdvx/vi/playdata/profile/index.html

# Arguments
## `sdvx_csv_to_tachi`

| Argument      | Short   | Description                                                                                                                 | Default                |
|:-------------:|:-------:|:---------------------------------------------------------------------------------------------------------------------------:|:----------------------:|
| `csv_filename`| —       | Path to the CSV file                                                                                                       | —                      |
| `--service`   | `-s`    | Service description to be shown on Tachi (Note for where this score came from)                                              | `SDVX Arcade Import`   |
| `--output`    | `-o`    | Output filename                                                                                                             | `sdvx_tachi.json`      |
| `--game`      | `-g`    | Version of the game. Surely there will be another one right...                                                              | `EXCEED_GEAR`          |
| `--time`      | `-t`    | UNIX time (in milliseconds) that should be added to the scores. Defaults to current UNIX time                                | `None`                 |
| `--date_file` | `-d`    | SDVX e-amusement profile site saved HTML. See README in sdvx/eamuse_csv for instructions. Overrides with --time input if missing | —                   |
| `--timezone`  | `-tz`   | Only needed if -d is used, specifies what timezone to convert to                                                            | —                      |
| `--cookie`  | `-c`   | Automatically pull profile data from e-amusement using cookie                                                            | —                      |

## `eamuse_merge_to_csv`

| Argument    | Short | Description                                           | Default            |
|:-----------:|:-----:|:-----------------------------------------------------:|:------------------:|
| `--old`     | —     | Old CSV file                                          | (Required)         |
| `--new`     | —     | New CSV file                                          | (Required)         |
| `--output`  | —     | Output File                                           | `sdvx_merged.csv`  |
