# Deprecated Batch-Manual export is now available right from AquaNet!

maimai DX. Both self-hosted and the primary AquaDX server is supported:

Please note currently all scores are set as DX variant of scores.

[How to get AquaDX Token?](../../common_docs/aquadx_how_to_get_token.md)

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
