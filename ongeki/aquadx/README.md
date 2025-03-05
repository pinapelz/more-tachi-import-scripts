AquaDX currently does not have a built-in export function. If you are playing on the publicly hosted ver the best way to get some scores for now is to scrape your recent plays:


**No access to DB (playing on a hosted version):**
- Go to ONGEKI player page
- `CTRL + SHIFT + I`-> Open Network tab
- Find URL for request made to `/aqua/api/v2/game/ongeki`
- Download the JSON and use this as your input

The script should grab the latest all-music.json. But in case it doesn't, a potentially outdated backup has been included
