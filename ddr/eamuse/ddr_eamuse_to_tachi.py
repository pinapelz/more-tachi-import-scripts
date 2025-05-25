from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
import argparse
import requests
from datetime import datetime
import pytz

GAME_DATA = {
    "WORLD": {
        "SP_PAGES": 25,
        "DP_PAGES": 25,
        "MUSIC_DATA_PAGE": "https://p.eagate.573.jp/game/ddr/ddrworld/playdata/music_data_single.html",
        "MUSIC_DETAIL_BASE": "https://p.eagate.573.jp/game/ddr/ddrworld/playdata/",
        "DIFFICULTY_MAP" : {
            0: "BEGINNER", 1: "BASIC", 2: "DIFFICULT", 3: "EXPERT", 4: "CHALLENGE"
        }
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


def parse_detailed_score_page(url: str, version: str, cookies: str):
    site_data = get_site_data_with_cookie(url, cookies)
    score_data = {"optional": {}}
    soup = BeautifulSoup(site_data, 'html.parser')
    difficulty_param = None
    parsed_url = url.split('?')
    if len(parsed_url) > 1:
        query_params = parsed_url[1].split('&')
        for param in query_params:
            key_value = param.split('=')
            if len(key_value) == 2 and key_value[0] == 'difficulty':
                difficulty_param = int(key_value[1])
                break
    score_data['difficulty'] = GAME_DATA[version]["DIFFICULTY_MAP"].get(int(difficulty_param), "UNKNOWN MAYBE ERROR. FIX SCRIPT")
    score_data["matchType"] = "songTitle"
    music_info_table = soup.find('table', id='music_info')
    if music_info_table:
        cells = music_info_table.find_all('td')
        if len(cells) >= 2:
            title_arist_data = cells[1].get_text(separator="<br/>").split("<br/>")
            score_data['identifier'] = title_arist_data[0]
    music_detail_table = soup.find('table', id='music_detail_table')
    rows = music_detail_table.find_all('tr')
    for row in rows:
        headers = row.find_all('th')
        data_cells = row.find_all('td')
        for th, td in zip(headers, data_cells):
            if 'ハイスコア' == th.text:
                score_data['score'] = int(td.text.strip())
            elif 'フレアランク' in th.text:
                flare_rank = td.text.strip()
                if flare_rank == "なし":
                    flare_rank = "0"
                score_data["optional"]["flare"] = flare_rank
            elif '最大コンボ数' in th.text:
                score_data["optional"]["maxCombo"] = int(td.text.strip())
            elif '最終プレー時間' in th.text:
                time_played = td.text.strip()
                naive_datetime = datetime.strptime(time_played, "%Y-%m-%d %H:%M:%S")
                jst_timezone = pytz.timezone("Asia/Tokyo")
                localized_datetime = jst_timezone.localize(naive_datetime)
                score_data["timeAchieved"] = int(localized_datetime.timestamp() * 1000)
            elif 'ハイスコア時のランク' in th.text:
                if td.text.strip() == "E":
                    score_data["lamp"] = "FAILED"
                else:
                    score_data["lamp"] = "CLEAR"
    clear_detail_table = soup.find('table', id='clear_detail_table')
    rows = clear_detail_table.find_all('tr')
    for row in rows:
        headers = row.find_all('th')
        data_cells = row.find_all('td')
        for th, td in zip(headers, data_cells):
            if 'グッドフルコンボ' in th.text:
                if int(td.text.strip()) != 0:
                    score_data["lamp"] = "FULL COMBO"
            elif 'グレートフルコンボ' in th.text:
                if int(td.text.strip()) != 0:
                    score_data["lamp"] = "GREAT FULL COMBO"
            elif 'パーフェクトフルコンボ' in th.text:
                if int(td.text.strip()) != 0:
                    score_data["lamp"] = "PERFECT FULL COMBO"
            elif 'マーベラスフルコンボ' in th.text:
                if int(td.text.strip()) != 0:
                    score_data["lamp"] = "MARVELOUS FULL COMBO"
            elif 'LIFE4 クリア' in th.text and score_data["lamp"] == "CLEAR":
                if int(td.text.strip()) != 0:
                    score_data["lamp"] = "LIFE4"
    return score_data

def convert_ddr_data_to_tachi_json(version: str, playstyle: str, service: str, cookies: str, output: str):
    batch_manual = {
        "meta": {
            "game": "ddr",
            "playtype": playstyle,
            "service": service
        },
        "scores": []
    }
    to_inspect_urls = []
    for page_num in range(GAME_DATA[version][f"{playstyle}_PAGES"]):
        found_charts = 0
        print(f"Checking Page {page_num+1}/{GAME_DATA[version][f'{playstyle}_PAGES']} for scores", end="")
        url = f"{GAME_DATA[version]['MUSIC_DATA_PAGE']}?offset={page_num}"
        site_data = get_site_data_with_cookie(url, cookies)
        soup = BeautifulSoup(site_data, 'html.parser')
        rows = soup.find_all('tr', class_='data')
        for row in rows:
            cells = row.find_all('td', class_='rank')
            for cell in cells:
                score_div = cell.find('div', class_='data_score')
                if not score_div or score_div.text.strip() == '---':
                    continue
                link = cell.find('a', class_='music_info')
                if link and link.has_attr('href'):
                    to_inspect_urls.append(urljoin(GAME_DATA[version]["MUSIC_DETAIL_BASE"], link['href']))
                    found_charts += 1
        print(f"  ->  Found {found_charts} charts with scores!")
    num_urls = len(to_inspect_urls)
    progress = 0
    for url in to_inspect_urls:
        print(f"\rPulling Individual Scores ---> Progress: {progress + 1}/{num_urls}", end="")
        score = parse_detailed_score_page(url, version=version, cookies=cookies)
        batch_manual["scores"].append(score)
        progress += 1
    return batch_manual


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="ddr_eamuse_pb_to_tachi",
        description="Converts e-amusement DDR personal best records to a Tachi compatibile JSON",
    )
    parser.add_argument("-s", "--service", help="Service description to be shown on Tachi (Note for where this score came from)", default="e-amusement DDR PB Import")
    parser.add_argument("-c", "--cookies", help="Header string of e-amusement page cookies. See this script's README.md" )
    parser.add_argument("-p", "--playstyle", help="Playstyle. Must be either 'single' or 'double'", default="SP")
    parser.add_argument("-g", "--game", help="Version of the game", default="WORLD")
    parser.add_argument("-o", "--output", help="Output filename", default="ddr_pb_tachi.json")
    args = parser.parse_args()
    assert args.playstyle == "SP" or args.playstyle == "DP"
    assert args.game in ["WORLD"]
try:
    output_json = convert_ddr_data_to_tachi_json(args.game, args.playstyle, args.service, args.cookies, args.output)
    with open(args.output, "w", encoding="utf-8") as json_file:
        json.dump(output_json, json_file, ensure_ascii=False, indent=4)

    print("Conversion completed. JSON saved as " + args.output)
except Exception as e:
    print(f"Error: {str(e)}")
