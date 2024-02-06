import json
import re

from botasaurus import AntiDetectDriver, browser
from selenium.webdriver.common.by import By


def add_arguments(data, options):
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")


maps = [
    # "anubis",
    # "inferno",
    "mirage",
    # "vertigo",
    # "overpass",
    # "nuke",
    # "ancient",
    # "dust2",
    # "office",
]


def get_cache(filename):
    try:
        f = open("output/" + filename, "r").read()
        if f:
            return json.loads(f)
        return {}
    except:  # noqa: E722
        return {}


def write_cache(filename, data):
    f = open("output/" + filename, "w")
    f.write(json.dumps(data, indent=2))
    f.close()


def scrape_leaderboard(driver: AntiDetectDriver, url: str):
    driver.get(url)
    data_rows = driver.get_elements_or_none_by_selector(
        "div#leaderboard-cs2 > div.data-table > div.data-row"
    )
    results = []
    print(url)
    for data_row in data_rows:
        player_page_url_elems = data_row.find_elements(
            By.CSS_SELECTOR, ".player-name > a"
        )
        if not player_page_url_elems:
            continue
        player_page_url = player_page_url_elems[0].get_attribute("href")
        tracked = (
            True
            if data_row.find_elements(By.CSS_SELECTOR, "div:nth-child(3) > i")
            else False
        )
        wins_text = data_row.find_element(
            By.CSS_SELECTOR, "div:nth-child(4)"
        ).get_attribute("innerText")
        wins = int(wins_text or 0)
        rank_url = data_row.find_element(
            By.CSS_SELECTOR, "div:nth-child(5) > img"
        ).get_attribute("src")
        match = re.search(r"/(\d+)\.png$", rank_url)
        current_rank = None
        if match:
            current_rank = int(match.group(1))
        results.append(
            {
                "player_page_url": player_page_url,
                "tracked": tracked,
                "wins": wins,
                "current_rank": current_rank,
            }
        )
    return results


@browser(headless=True, add_arguments=add_arguments)
def scrape_all_leaderboards(driver: AntiDetectDriver, data):
    leaderboard_details: list[dict] = []
    for name in maps:
        leaderboard_details.append(
            {
                "name": name,
                "url": "https://csstats.gg/leaderboards/map/" + name,
                "cache_name": name + "_ranks.json",
            }
        )
        leaderboard_details.append(
            {
                "name": name,
                "url": "https://csstats.gg/leaderboards/map/" + name + "/wins",
                "cache_name": name + "_wins.json",
            }
        )
    results = {}
    for leaderboard_detail in leaderboard_details:
        lb_cache = get_cache(leaderboard_detail["cache_name"])
        map_result = lb_cache or scrape_leaderboard(driver, leaderboard_detail["url"])
        player_details = scrape_players(driver, leaderboard_detail, map_result)
        results[leaderboard_detail["name"]] = player_details

    # print(json.dumps(results))
    # Save the data as a JSON file in output/all.json
    return results


def scrape_players(driver: AntiDetectDriver, detail: dict, leaderboard: list[dict]):
    short_name = detail["name"]
    map_name = "cs_" + short_name if short_name == "office" else "de_" + short_name
    query = "?maps=" + map_name + "&modes=Competitive"

    for player_entry in leaderboard:
        if "won" in player_entry and "lost" in player_entry and "tied" in player_entry:
            continue
        url = player_entry["player_page_url"] + query
        print(url)
        driver.get(url)

        rate_limit_elems = driver.find_elements(By.CSS_SELECTOR, "h2.text-gray-600")
        if rate_limit_elems:
            print("rate limited")
            exit(429)

        counts_div = driver.find_element(
            By.CSS_SELECTOR,
            "#player-overview > .col-sm-8 > .col-sm-7 > div:nth-child(4) > .stat-panel > div > div:nth-child(4)",
        )
        player_entry["won"] = int(
            counts_div.find_element(
                By.CSS_SELECTOR, "div:nth-child(2) > span.total-value"
            ).get_attribute("innerText")
        )
        player_entry["lost"] = int(
            counts_div.find_element(
                By.CSS_SELECTOR, "div:nth-child(3) > span.total-value"
            ).get_attribute("innerText")
        )
        player_entry["tied"] = int(
            counts_div.find_element(
                By.CSS_SELECTOR, "div:nth-child(4) > span.total-value"
            ).get_attribute("innerText")
        )
        write_cache(detail["cache_name"], leaderboard)
    return leaderboard
