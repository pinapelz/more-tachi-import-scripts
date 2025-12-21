import argparse
import json
import os
import requests


LAMP_MAP = {
    1: "FAILED",
    2: "CLEAR",
    3: "EXCESSIVE CLEAR",
    4: "ULTIMATE CHAIN",
    5: "PERFECT ULTIMATE CHAIN",
    6: "MAXXIVE CLEAR"
}

DIFFICULTY_MAP = {
    0: "NOV",
    1: "ADV",
    2: "EXH",
    3: "GAME_SPECIFIC",
    4: "MXM"
}


def load_seeds(url: str = "https://raw.githubusercontent.com/zkrising/Tachi/refs/heads/main/seeds/collections/charts-sdvx.json") -> dict:
    print("Loading seeds from:", url)
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def find_chart_difficulties(in_game_id: int, seeds: dict = None):
        low, high = 0, len(seeds) - 1
        results = []
        while low <= high:
            mid = (low + high) // 2
            chart = seeds[mid]
            if chart["data"]["inGameID"] == in_game_id:
                results.append(chart)
                left, right = mid - 1, mid + 1
                while left >= 0 and seeds[left]["data"]["inGameID"] == in_game_id:
                    results.append(seeds[left])
                    left -= 1
                while right < len(seeds) and seeds[right]["data"]["inGameID"] == in_game_id:
                    results.append(seeds[right])
                    right += 1
                break
            elif chart["data"]["inGameID"] < in_game_id:
                low = mid + 1
            else:
                high = mid - 1
        for result in results:
            if result["difficulty"] not in DIFFICULTY_MAP.values():
                return result["difficulty"]
        return None


def convert_22vv0_sdvx_to_tachi_json(file: str, output_path: str, service: str, profile_id: str):
    seeds = load_seeds()
    with open(file, "r", encoding="utf-8") as infile:
        batch_manual = {
            "meta": {"game": "sdvx", "playtype": "Single", "service": service},
        }
        scores = []
        for line in infile:
            data = json.loads(line)
            if "collection" not in data.keys():
                continue
            if data["collection"] == "music":
                music_id = data["mid"]
                difficulty = DIFFICULTY_MAP[data["type"]]
                if difficulty == "GAME_SPECIFIC":
                    difficulty  = find_chart_difficulties(music_id, seeds)
                    if difficulty is None:
                        print("[ERROR] -> Difficulty for", music_id, " was not found in Tachi seeds")
                        continue
                score = data["score"]
                exscore = data["exscore"]
                lamp = LAMP_MAP[data["clear"]]
                timestamp = data["updatedAt"]["$$date"]
                scores.append({
                    "score": score,
                    "lamp": lamp,
                    "matchType": "sdvxInGameID",
                    "identifier": str(data["mid"]),
                    "difficulty": difficulty,
                    "timeAchieved": timestamp,
                    "optional": {
                        "exScore": exscore
                    }
                })
        batch_manual["scores"] = scores
        with open(output_path, "w", encoding="utf-8") as outfile:
            json.dump(batch_manual, outfile, indent=4, ensure_ascii=False)
            print(f"Output saved to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="22vv0_kfc_to_tachi.py",
        description="Converts 22vv0 Asphyxia SDVX (KFC) save data to Tachi compatible JSON",
    )
    parser.add_argument(
        "-s",
        "--service",
        help="Service description to be shown on Tachi (Note for where this score came from)",
        default="SOUND VOLTEX Asphyxia (22vv0)",
    )
    parser.add_argument("-f", "--file", help="AsphyxiaCORE SOUND VOLTEX .db file (sdvx@asphyxia.db)", required=True)
    parser.add_argument(
        "-o", "--output", help="Output filename", default="sdvx_asphyxia_batch_manual.json"
    )
    parser.add_argument("-p", "--profile", help="Asphyxia Profile ID to export for")
    args = parser.parse_args()
    if args.file is None:
        print("ERROR: Please specify Asphyxia DB file (from savedata folder)")
        exit(1)
    if not os.path.exists(args.file):
        print(f"ERROR: The file {args.file} does not exist.")
        exit(1)

    convert_22vv0_sdvx_to_tachi_json(args.file, args.output, args.service, args.profile)
