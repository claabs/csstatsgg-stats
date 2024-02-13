import json
import re

from botasaurus import AntiDetectDriver, browser
from selenium.webdriver.common.by import By


def add_arguments(data, options):
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")


maps = [
    "anubis",
    # "inferno",
    "mirage",
    # "vertigo",
    # "overpass",
    "nuke",
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


@browser(headless=True, add_arguments=add_arguments, block_resources=True)
def scrape_all_maps(driver: AntiDetectDriver, data):
    cache_files: list[str] = []
    for name in maps:
        cache_files.append(name + "_ranks.json")
        cache_files.append(name + "_wins.json")
    results = {}
    for cache_file in cache_files:
        print(cache_file)
        lb_cache = get_cache(cache_file)
        if not lb_cache:
            continue
        player_details = scrape_players(driver, lb_cache)
        results.update(player_details)

    # print(json.dumps(results))
    # Save the data as a JSON file in output/all.json
    return results


def scrape_players(driver: AntiDetectDriver, leaderboard: list[dict]):
    # Final 12 months of CSGO
    query = "/csgo?platforms=Valve&date=range&modes=Competitive&start=1664254800&end=1695877199"

    results = get_cache("csgo.json")
    for player_entry in leaderboard:
        player_page_url = player_entry["player_page_url"]
        if player_page_url in results:
            continue
        url = player_page_url + query
        print(url)
        driver.get(url)
        rate_limit_elems = driver.find_elements(By.CSS_SELECTOR, "h2.text-gray-600")
        if rate_limit_elems:
            print("rate limited")
            exit(429)

        error_elems = driver.find_elements(By.CSS_SELECTOR, ".text-gray-500")
        if error_elems:
            continue

        counts_divs = driver.find_elements(
            By.CSS_SELECTOR,
            "#player-overview > .col-sm-8 > .col-sm-7 > div:nth-child(4) > .stat-panel > div > div:nth-child(4)",
        )
        if not counts_divs:
            results[player_page_url] = {}
            write_cache("csgo.json", results)
            continue
        counts_div = counts_divs[0]

        won = int(
            counts_div.find_element(
                By.CSS_SELECTOR, "div:nth-child(2) > span.total-value"
            ).get_attribute("innerText")
        )
        lost = int(
            counts_div.find_element(
                By.CSS_SELECTOR, "div:nth-child(3) > span.total-value"
            ).get_attribute("innerText")
        )
        tied = int(
            counts_div.find_element(
                By.CSS_SELECTOR, "div:nth-child(4) > span.total-value"
            ).get_attribute("innerText")
        )
        rank = None
        player_ranks_elems = driver.find_elements(By.CSS_SELECTOR, "#player-ranks")
        if player_ranks_elems:
            header_rank_elems = player_ranks_elems[0].find_elements(
                By.CSS_SELECTOR, ".header"
            )
            if len(header_rank_elems) == 2:
                ranks_elems = player_ranks_elems[0].find_elements(
                    By.CSS_SELECTOR, ".ranks"
                )
                csgo_ranks_elem = ranks_elems[-1]
                rank_url_elems = csgo_ranks_elem.find_elements(
                    By.CSS_SELECTOR, ".rank > img"
                )
                if rank_url_elems:
                    rank_url = rank_url_elems[0].get_attribute("src")
                    match = re.search(r"/(\d+)\.png$", rank_url)
                    if match:
                        rank = int(match.group(1))

        results[player_page_url] = {
            "won": won,
            "lost": lost,
            "tied": tied,
            "rank": rank,
        }

        write_cache("csgo.json", results)
    return results


def main():
    try:
        scrape_all_maps()
    except Exception as e:
        print(e)
        if e.msg == "invalid session id":
            print("retrying")
            main()


if __name__ == "__main__":
    # Initiate the web scraping task
    main()
