# Nautica (ksm.dev) to maps.db
This is a "seed" generation helper for Tachi. It generates the `maps.db` file which can be used to generate a new seed file. The instructions here expect that you are already somewhat understand how Tachi works (since you're persumably running your own instance)

i.e https://github.com/zkrising/Tachi/blob/main/seeds/scripts/rerunners/usc/add-usc-converts.js

This pulls **ALL** charts from Nautica and produces the minimal requirements for seed generation in Tachi. Please run responsibly since this requires downloading all charts and producing a `SHA-1` hash for them.


```bash
python nautica_to_maps.py --start-page <START_PAGE> --db <PATH_TO_DB>
```
- START_PAGE default = 1
- PATH_TO_DB default = maps.db


As an alternative, I provide the one I have generated on Nov.10 2025 (`maps-nov-10-2025.db`)

# Merging into Tachi
Firstly, move the generated `maps.db` into Tachi's environment

Tachi relies on fuzzy matching title and artist which doesn't work great for nautica since there are many people who re-chart songs. In these cases they will have the same name.

To work around this, a custom script can be used to finally convert `maps.db` into seeds. This code is largely based off of the usc-converts re-runner.

If there is a collision in `songs-usc.json` where the name and artist of a song already exists, the string `(<EFFECTOR_NAME> Nautica Edition)` is appended to the title.

To run this script, place it in `seeds/scripts/single-use/usc` (you need to create the usc folder if it doesn't already exist in single-use). Then within Tachi's environment run `node add-usc-nautica.js -f /nautica -d maps.db`.

Then just load the seeds and you're good to go!

*It may still TECHNICALLY be possible to have collisions, but the chances of 2 effectors with the same name who create charts for the same song are unlikely. In those cases you should manually resolve the difference after running the script.*
