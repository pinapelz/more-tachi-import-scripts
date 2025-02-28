# e-amusement SDVX CSV to Tachi WARNING!!!
The CSV provided by Konami doesn't contain any information regarding the date which you played/obtained a particular score. It only keeps your BEST score.

This causes for duplicate imports if you use this script more than once

## Solution
The first time you import, run `sdvx_csv_to_tach.py` and import the output JSON file normally. Howver **KEEP THE OLD CSV FILE**

The next time you play, export the CSV again but first run `eamuse_merge_csv.py --old <file> --new <file>`. Passing the old and new CSV files accordingly.

This will check for differences between the 2 files and remove lines of the same value in the new file so that only newly obtained best scores are uploaded.

# What if I want all plays?
I don't think there's a method right now to automatically import arcade data into Tachi for each play. Play history is locked behind the eAmusement basic subscription plan.

The best you can do is download the eAmusement app, subscribe the the basic course and manually make your own score CSV in the same format. Then run `sdvx_csv_to_tach.py`

Alternatively, you can take pictures of each play result screen and build your own JSON so that there is even more info available!
