import csv
import json

import statsmodels.api as sm

from csstatsgg_stats.generate_plot import generate_plot

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

rank_names = {
    1: "S1",
    2: "S2",
    3: "S3",
    4: "S4",
    5: "SE",
    6: "SEM",
    7: "GN1",
    8: "GN2",
    9: "GN3",
    10: "GNM",
    11: "MG1",
    12: "MG2",
    13: "MGE",
    14: "DMG",
    15: "LE",
    16: "LEM",
    17: "SMFC",
    18: "GE",
}


def analyze_map(map_name):
    dataset: list[dict] = []

    f = open("output/" + map_name + "_ranks.json", "r").read()
    dataset += json.loads(f)

    f = open("output/" + map_name + "_wins.json", "r").read()
    # concat both datasets
    dataset += json.loads(f)

    seen_urls = set()
    # chatGPT insanity
    unique_dataset = [
        d
        for d in dataset
        if (
            tuple(d.items())[:-1] not in seen_urls
            and not seen_urls.add(tuple(d.items())[:-1])
        )
    ]

    rank_sorted: dict[int, list[float]] = {}
    for player in unique_dataset:
        rank = player["current_rank"]

        if "won" not in player:
            continue
        total = player["won"] + player["lost"] + player["tied"]
        winrate = (player["won"] + (player["tied"] / 2)) / total
        weight = player["won"] / player["wins"]

        if total >= 10 and rank > 0:
            if rank not in rank_sorted:
                rank_sorted[rank] = []
            rank_sorted[rank].append([winrate, weight])

    stats_dicts = []
    print(map_name)

    for rank, rank_data in sorted(rank_sorted.items()):
        winrates = list(map(lambda x: x[0], rank_data))
        weights = list(map(lambda x: x[1], rank_data))
        weighted_stats = sm.stats.DescrStatsW(winrates, weights=weights)
        minimum = min(winrates)
        q1, q3 = weighted_stats.quantile([0.25, 0.75], return_pandas=False)
        mean = weighted_stats.mean
        maximum = max(winrates)
        n = len(winrates)
        stdev = weighted_stats.std
        print("%4s: mean=%.2f, stdev=%.3f, n=%i" % (rank_names[rank], mean, stdev, n))
        stats_dicts.append(
            {
                "rank": rank_names[rank],
                "minimum": minimum,
                "q1": q1,
                "mean": mean,
                "q3": q3,
                "maximum": maximum,
                "n": n,
                "stdev": stdev,
            }
        )

    generate_plot(stats_dicts, map_name.title(), map_name)

    # Writing to CSV file
    fieldnames = [
        "rank",
        "minimum",
        "q1",
        "q3",
        "maximum",
        "mean",
        "stdev",
        "n",
    ]
    with open("output/" + map_name + ".csv", "w", newline="") as csv_file:
        csv_writer = csv.DictWriter(
            csv_file,
            fieldnames=fieldnames,
        )
        csv_writer.writeheader()
        csv_writer.writerows(stats_dicts)


for map_name in maps:
    analyze_map(map_name)
