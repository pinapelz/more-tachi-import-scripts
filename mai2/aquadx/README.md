maimai DX. Both self-hosted and the primary AquaDX server is supported:

Please note currently all scores are set as DX variant of scores.

# Arguments

| Argument    | Short | Description                                                                                                    | Default                     |
|:-----------:|:----:|:---------------------------------------------------------------------------------------------------------------:|:--------------------------:|
| `--file`    | `-f` | Specify the path to the playdata JSON file exported from AquaDX. Expected to be in the format of AquaNet CHUNITHM export                                     | —                          |
| `--service` | `-s` | Service description to be shown on Tachi (Note for where this score came from).                                | `AquaDX Chuni Import`      |
| `--token`   | `-t` | Use your AquaNet Token to grab your play data directly from the API. Get it from the browser's Network tab. | —                          |
| `--url`     | `-u` | AquaNet API endpoint. No need to change this unless you self-host AquaDX. The full URL before `/api` is expected                                      | `https://aquadx.net/aqua`  |
| `--output`  | `-o` | Output filename.                                                                                               | `aquadx_chuni_tachi.json`  |
| `--music`  | `-m` | Music file containing map of song ids to song titles. Usually not needed to be specified as script will grab the latest from AquaDX                                                                                            | `online`  |

> [!IMPORTANT]
> You only need to specify either `--file` or `--token`/`--url`

# How to get token?
1. Go to AquaDX
2. CTRL+SHIFT+I (Open Dev Tools panel)
3. Go to Network tab
4. Refresh the page with the Dev Tools Panel Open
5. Search for `/api/v2`
6. Click on any of the requests and check the url. There will be a part of the url that starts with `token=`
7. Copy everything after the `=` up until either the end of the URL or the next `&`

**DO NOT SHARE THIS TOKEN WITH OTHER PEOPLE**
