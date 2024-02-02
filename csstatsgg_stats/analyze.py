import csv
import json
import statistics

import numpy as np

maps = [
    "anubis",
    # "inferno",
    # "mirage",
    # "vertigo",
    # "overpass",
    # "nuke",
    # "ancient",
    # "dust2",
    # "office",
]

map_name = "mirage"

f = open("output/" + map_name + "_ranks.json", "r").read()
dataset: list[dict] = json.loads(f)

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

    if total >= 10 and rank > 0:
        if rank not in rank_sorted:
            rank_sorted[rank] = []
        rank_sorted[rank].append(winrate)

stats_dicts = []
print(map_name)

for rank, rank_data in sorted(rank_sorted.items()):
    minimum = min(rank_data)
    q1 = percentile_result = np.percentile(rank_data, 25)
    mean = statistics.mean(rank_data)
    q3 = percentile_result = np.percentile(rank_data, 75)
    maximum = max(rank_data)
    n = len(rank_data)
    stdev = statistics.stdev(rank_data) if n > 1 else 0
    print("%i: mean=%.2f, stdev=%.3f, n=%i" % (rank, mean, stdev, n))
    stats_dicts.append(
        {
            "rank": rank,
            "minimum": minimum,
            "q1": q1,
            "mean": mean,
            "q3": q3,
            "maximum": maximum,
            "n": n,
            "stdev": stdev,
        }
    )

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
