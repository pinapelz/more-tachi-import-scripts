import csv
import json
import argparse
import time
import requests

DIFFICULTY_MAPPING = {
    "NOVICE": "NOV",
    "ADVANCED": "ADV",
    "EXHAUST": "EXH",
    "INFINITE": "INF",
    "GRAVITY": "GRV",
    "HEAVENLY": "HVN",
    "VIVID": "VVD",
    "EXCEED": "XCD",
    "MAXIMUM": "MXM"
}

LAMP_MAPPING = {
    "PLAYED": "FAILED",
    "COMPLETE": "CLEAR",
    "MAXXIVE COMPLETE": "MAXXIVE CLEAR",
    "ULTIMATE CHAIN": "ULTIMATE CHAIN",
    "EXCESSIVE COMPLETE": "EXCESSIVE CLEAR"
}

GAME_DATA = {
    "EXCEED_GEAR": {
        "PROFILE_URL": "https://p.eagate.573.jp/game/sdvx/vi/playdata/profile/index.html"
    }
}

def get_site_data_with_cookie(url, cookie_header):
    cookies = {}
    for cookie in cookie_header.split(";"):
        name, value = cookie.strip().split("=", 1)
        cookies[name] = value
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    response = requests.get(url, cookies=cookies, headers=headers)
    response.raise_for_status()
    return response.text

def create_date_dict(game_ver:str, raw_site_data: str) -> dict:
    from bs4 import BeautifulSoup
    from datetime import datetime
    import pytz
    if game_ver == "EXCEED_GEAR":
        soup = BeautifulSoup(raw_site_data, 'html.parser')
        cat_divs = soup.find_all('div', class_='cat')[5:]
        jst = pytz.timezone('Asia/Tokyo')
        date_data = {}
        for div in cat_divs:
            inners = div.find_all('div', class_='inner')
            date = inners[0].get_text(strip=True)
            music_name = inners[1].find('p', class_='music_name').get_text(strip=True)
            date_obj = datetime.strptime(date, "%Y/%m/%d %H:%M:%S")
            date_obj_jst = jst.localize(date_obj)
            date_obj_unixtime = int(date_obj_jst.timestamp() * 1000)
            date_data[music_name] = date_obj_unixtime
        return date_data
    else:
        print("NO VALID GAME VERSION SPECIFIED TO CREATE DATE DATA. SEE README")
        exit(1)

def convert_sdvx_csv_to_tachi_json(csv_file, game, playtype, service, unixtime, date_dict):
    encodings = ['utf-8-sig', 'utf-8', 'shift-jis', 'cp932']

    for encoding in encodings:
        try:
            batch_manual = {
                "meta": {
                    "game": game,
                    "playtype": playtype,
                    "service": service,
                },
                "scores": []
            }

            with open(csv_file, newline='', encoding=encoding) as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames
                required_fields = ["楽曲名", "難易度", "クリアランク", "ハイスコア"]
                if not all(field in fieldnames for field in required_fields):
                    continue


                for row in reader:
                    lamp = LAMP_MAPPING[row["クリアランク"].upper()]
                    if row.get("ULTIMATE CHAIN") == "1":
                        lamp = "ULTIMATE CHAIN"
                    if row.get("PERFECT") == "1":
                        lamp = "PERFECT ULTIMATE CHAIN"
                    time_stamp = date_dict.get(row["楽曲名"], unixtime if unixtime != "now" else int(time.time())*1000)

                    score_entry = {
                        "score": int(row["ハイスコア"]),
                        "lamp": lamp,
                        "matchType": "songTitle",
                        "identifier": row["楽曲名"],
                        "difficulty": DIFFICULTY_MAPPING[row["難易度"].upper()],
                        "timeAchieved": time_stamp
                    }
                    optional_fields = {}
                    if row.get("EXスコア"):
                        optional_fields["exScore"] = int(row["EXスコア"])
                    if row.get("fast"):
                        optional_fields["fast"] = int(row["fast"])
                    if row.get("slow"):
                        optional_fields["slow"] = int(row["slow"])
                    if row.get("maxCombo"):
                        optional_fields["maxCombo"] = int(row["maxCombo"])
                    if row.get("gauge"):
                        optional_fields["gauge"] = float(row["gauge"])
                    if optional_fields:
                        score_entry["optional"] = optional_fields
                    batch_manual["scores"].append(score_entry)
                return batch_manual
        except UnicodeDecodeError:
            continue
        except Exception as e:
            print(f"Error with encoding {encoding}: {str(e)}")
            continue

    raise ValueError("Failed to read CSV file with any supported encoding")


if __name__ == "__main__":
    print("!!!!! WARNING !!!!!")
    print("Please make sure you have read the README about SDVX's official CSV files before importing")
    print("If you pass in a date file make sure the HTML is unformatted otherwise the spacing for song names will be wrong!")
    parser = argparse.ArgumentParser(
        prog="sdvx_csv_to_tachi",
        description="Converts CSV data exported from SDVX eAmuse site to Tachi compatibile JSON",
        epilog="Note that not all information can be derived from the CSV so some fields will be missing from Tachi"
    )
    parser.add_argument("csv_filename", help="Path to the CSV file")
    parser.add_argument("-s", "--service", help="Service description to be shown on Tachi (Note for where this score came from)", default="SDVX Arcade Import")
    parser.add_argument("-o", "--output", help="Output filename", default="sdvx_tachi.json")
    parser.add_argument("-g", "--game", help="Version of the game. Surely there will be another one right...", default="EXCEED_GEAR")
    parser.add_argument("-t", "--time", help="UNIX time (in milliseconds) that should be added to the scores. Defaults to current UNIX time", default=None)
    parser.add_argument("-d", "--date_file", help="SDVX e-amusement profile site saved HTML. See README in sdvx/eamuse_csv for instructions. Overrides with --time input if missing", required=False)
    parser.add_argument("-tz", "--timezone", help="Only needed if -d is used, specifies what timezone to convert to", required=False)
    parser.add_argument("-c", "--cookie", help="Pass in a cookie header to automatically pull date data")
    args = parser.parse_args()
    assert args.game in ["EXCEED_GEAR"]
    curr_time = int(time.time() * 1000) if (args.time == "now" or args.time is None) else args.time

    if args.date_file and not args.timezone:
        print("ERROR: A date file is provided but no target timezone (-tz) has been specified. Please pass the timezone in which you played the scores")
        exit(1)

    date_data = {}
    if args.date_file:
        with open(args.date_file, "r") as file:
            site_data = file.read()
            date_data = create_date_dict(args.game, site_data)
    elif args.cookie:
        site_data = get_site_data_with_cookie(GAME_DATA[args.game]["PROFILE_URL"], args.cookie)
        date_data = create_date_dict(args.game, site_data)
try:
    output_json = convert_sdvx_csv_to_tachi_json(args.csv_filename, "sdvx", "Single", args.service, curr_time, date_data)

    with open(args.output, "w", encoding="utf-8") as json_file:
        json.dump(output_json, json_file, ensure_ascii=False, indent=4)

    print("Conversion completed. JSON saved as " + args.output)
except Exception as e:
    print(f"Error: {str(e)}")
