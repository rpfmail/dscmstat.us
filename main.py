#!/usr/bin/env python3
import copy
import gzip
import io
import json
import operator
import sys
import time
import urllib.request

PHANTOM_LOADING = -1
PHANTOM_HUMAN = 0
PHANTOM_COOP = 1
PHANTOM_INVADER = 2
PHANTOM_HOLLOW = 8

PHANTOM_TYPES = {
    -1: "loading",
    0: "human",
    1: "coop",
    2: "invader",
    8: "hollow"
}

WORLDS = {
  "-1--1": "None or loading",
  "10-0": "Depths",
  "10-1": "Undead Burg/Parish",
  "10-2": "Firelink Shrine",
  "11-0": "Painted World",
  "12-0": "Darkroot Garden",
  "12-1": "Oolacile",
  "13-0": "Catacombs",
  "13-1": "Tomb of the Giants",
  "13-2": "Great Hollow / Ash Lake",
  "14-0": "Blighttown",
  "14-1": "Demon Ruins",
  "15-0": "Sen's Fortress",
  "15-1": "Anor Londo",
  "16-0": "New Londo Ruins",
  "17-0": "Duke's Archives / Caves",
  "18-0": "Kiln",
  "18-1": "Undead Asylum"
}

def ungzip_response(response):
    if response.info().get("Content-Encoding") == "gzip":
        f = gzip.GzipFile(fileobj=response)
        return f.read()
    else:
        return response.read()

def load_json(url):
    headers = { "Accept-Encoding": "gzip" }
    request = urllib.request.Request(url, headers=headers)
    response = urllib.request.urlopen(request)
    response_bytes = ungzip_response(response)
    response_text = str(response_bytes, "UTF-8")
    return json.loads(response_text)

data = load_json("http://dscm-net.chronial.de:8811/list")
all_nodes = list(filter(lambda n: 0 < n["sl"], data["nodes"]))

human_nodes = list(filter(lambda n: n["phantom_type"] == PHANTOM_HUMAN, all_nodes))
hollow_nodes = list(filter(lambda n: n["phantom_type"] == PHANTOM_HOLLOW, all_nodes))
invader_nodes = list(filter(lambda n: n["phantom_type"] == PHANTOM_INVADER, all_nodes))
coop_nodes = list(filter(lambda n: n["phantom_type"] == PHANTOM_COOP, all_nodes))
loading_nodes = list(filter(lambda n: n["phantom_type"] == PHANTOM_LOADING, all_nodes))

f_sl = lambda n: n["sl"]
all_sls = list(map(f_sl, all_nodes))
human_sls = list(map(f_sl, human_nodes))
hollow_sls = list(map(f_sl, hollow_nodes))
invader_sls = list(map(f_sl, invader_nodes))
coop_sls = list(map(f_sl, coop_nodes))
loading_sls = list(map(f_sl, loading_nodes))

world_counts = copy.copy(WORLDS)

for world_key, _ in world_counts.items():
    world_counts[world_key] = {
        "total": 0, "human": 0, "hollow": 0,
        "invader": 0, "coop": 0, "loading": 0
    }

for node in all_nodes:
    phantom_type = PHANTOM_TYPES[node["phantom_type"]]

    world_counts[node["world"]]["total"] += 1
    world_counts[node["world"]][phantom_type] += 1

world_counts_readable = {}
for world_key, value in world_counts.items():
    world_counts_readable[WORLDS[world_key]] = value

output = {
    "worlds": world_counts_readable,
    "players": {
        "total": len(all_sls),
        "human": len(human_sls),
        "hollow": len(hollow_sls),
        "invader": len(invader_sls),
        "coop": len(coop_sls),
        "loading": len(loading_sls)
    },
    "lastUpdated": time.strftime("%d/%m/%Y %H:%M:%S")
}

with open("stats.json", "w") as fp:
    json.dump(output, fp)

