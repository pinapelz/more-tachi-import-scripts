Converts your e-amusement DDR scores to a Tachi Batch-Manual JSON. Due to how e-amusement stores scores, only your BEST score can be derived from each chart.

> [!NOTE]
> You must be subscribed to e-amusement Basic Course to use this

> [How to get Cookies?](../../common_docs/how_to_get_cookie_header.md)
>
> Get the cookies from this page: https://p.eagate.573.jp/game/ddr/ddrworld/playdata/music_data_single.html


# Arguments
| Argument        | Short   | Description                                                                                                                 | Default                        |
|:---------------:|:-------:|:---------------------------------------------------------------------------------------------------------------------------:|:------------------------------:|
| `--service`     | `-s`    | Service description to be shown on Tachi (Note for where this score came from)                                              | `e-amusement DDR PB Import`    |
| `--cookies`     | `-c`    | Header string of e-amusement page cookies. See this script's README.md                                                      | —                              |
| `--playstyle`   | `-p`    | Playstyle. Must be either `'SP'` or `'DP'`.                                                                         | `SP`                           |
| `--game`        | `-g`    | Version of the game                                                                                                         | `WORLD`                        |
| `--output`      | `-o`    | Output filename                                                                                                             | `ddr_pb_tachi.json`            |
