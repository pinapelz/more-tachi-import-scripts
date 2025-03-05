import argparse
import json
import urllib.request

ONGEKI_AQUADX_JSON = "https://aquadx.net/d/ongeki/00/all-music.json"

DIFFICULTY_MAPPING = {
    0: "BASIC",
    1: "ADVANCED",
    2: "EXPERT",
    3: "MASTER",
    4: "LUNATIC"
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
}

def convert_chuni_aquadx_json_to_tachi_json(input_json: str, output_file: str, service: str, music_json: str):
    if music_json == "online":
        req = urllib.request.Request(ONGEKI_AQUADX_JSON, headers=headers)
        with urllib.request.urlopen(req) as response:
            music_json = json.load(response)
    else:
        with open(music_json, "r", encoding="utf-8") as file:
            music_json = json.load(file)

    with open(input_json, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    batch_manual = {
        "meta": {"game": "ongeki", "playtype": "Single", "service": service},
        "scores": [],
    }

    processed_count = 0
    skipped_count = 0

    if "recent" in raw_data:
        for entry in raw_data["recent"]:
            level = entry.get("level", 0)

            processed_count += 1
            try:
                song_title = music_json[str(entry["musicId"])]["name"]
            except KeyError:
                skipped_count += 1
                continue
            clear_status = entry.get("clearStatus", 2)
            score_value = entry.get("techScore", 0)
            is_full_combo = entry.get("isFullCombo", False)
            is_full_bell = entry.get("isFullBell", False)
            is_all_break = entry.get("isAllBreak", False)
            lamp = "LOSS"
            if clear_status == 2:
                lamp = "CLEAR"
            elif is_full_combo:
                lamp = "FULL COMBO"
            elif is_all_break:
                lamp = "ALL BREAK"
            bell_lamp = "FULL BELL" if is_full_bell else "NONE"


            timestamp = entry.get("sortNumber", None)
            combo = entry.get("maxCombo",0)
            bell_count = entry.get("bellCount",0)
            total_bell_count = entry.get("totalBellCount", 0)
            plat_score = entry.get("platinumScore", 0)

            j_cbreak = entry.get("judgeCriticalBreak", 0)
            j_break = entry.get("judgeBreak", 0)
            j_hit = entry.get("judgeHit", 0)
            j_miss = entry.get("judgeMiss", 0)

            score_entry = {
                "score": score_value,
                "noteLamp": lamp,
                "bellLamp": bell_lamp,
                "matchType": "songTitle",
                "identifier": str(song_title),
                "difficulty": DIFFICULTY_MAPPING[level],
                "timeAchieved": timestamp * 1000 if timestamp else None,
                "judgements": {
                    "cbreak": j_cbreak,
                    "break": j_break,
                    "hit": j_hit,
                    "miss": j_miss,
                },
                "optional": {
                    "maxCombo": combo,
                    "bellCount": bell_count,
                    "totalBellCount": total_bell_count,
                    "platScore": plat_score
                },
            }

            batch_manual["scores"].append(score_entry)

    with open(output_file, "w", encoding="utf-8") as f:
        print("--- Processing Summary ---")
        print(f"Total scores processed: {processed_count}")
        print(f"Output saved to {output_file}")
        json.dump(batch_manual, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="ongeki_aquadx_to_tachi.py",
        description="Converts AquaDX API JSON for O.N.G.E.K.I to Tachi compatible JSON",
        epilog="damage, fast, slow, unavailable on the webui"
    )
    parser.add_argument("input_file", help="Path to the input JSON file exported from AquaDX")
    parser.add_argument(
        "-s",
        "--service",
        help="Service description to be shown on Tachi (Note for where this score came from)",
        default="AquaDX O.N.G.E.K.I Import (API JSON)",
    )
    parser.add_argument(
        "-o", "--output", help="Output filename", default="aquadx_ongeki_tachi.json"
    )
    parser.add_argument("--music", "--music-file", help="JSON file containing the mappings of song names to IDs. Check README for moe info", default="online")
    args = parser.parse_args()
    convert_chuni_aquadx_json_to_tachi_json(args.input_file, args.output, args.service, args.music)
