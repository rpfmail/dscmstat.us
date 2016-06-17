import math
import copy
import gzip
import io
import json
import operator
import sys
import time
#import urllib.request
PHANTOM_LOADING = -1
from six.moves import urllib
urllib.request
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

url="http://dscm-net.chronial.de:8811/list"
headers = { "Accept-Encoding": "gzip" }
request = urllib.request.Request(url, headers=headers)
response = urllib.request.urlopen(request)
from StringIO import StringIO
buf = StringIO( response.read())
f = gzip.GzipFile(fileobj=buf)
data=f.read()
data=json.loads(data)
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

world_ranges = copy.copy(WORLDS)
for world_key, _ in world_ranges.items():
    world_ranges[world_key] = {
    "human": []
    }

for node in all_nodes:
    if not node["phantom_type"] in PHANTOM_TYPES:
        continue
    phantom_type = PHANTOM_TYPES[node["phantom_type"]]
    world_ranges[node["world"]]["human"].append(node["sl"])

world_ranges_readable={}
for world_key, value in world_ranges.items():
    world_ranges_readable[WORLDS[world_key]] = value

import matplotlib
from numpy.random import randn
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

def is_outlier(points, thresh=3.5):
    """
    Returns a boolean array with True if points are outliers and False 
    otherwise.

    Parameters:
    -----------
        points : An numobservations by numdimensions array of observations
        thresh : The modified z-score to use as a threshold. Observations with
            a modified z-score (based on the median absolute deviation) greater
            than this value will be classified as outliers.

    Returns:
    --------
        mask : A numobservations-length boolean array.

    References:
    ----------
        Boris Iglewicz and David Hoaglin (1993), "Volume 16: How to Detect and
        Handle Outliers", The ASQC Basic References in Quality Control:
        Statistical Techniques, Edward F. Mykytka, Ph.D., Editor. 
    """
    if len(points.shape) == 1:
        points = points[:,None]
    median = np.median(points, axis=0)
    diff = np.sum((points - median)**2, axis=-1)
    diff = np.sqrt(diff)
    med_abs_deviation = np.median(diff)

    modified_z_score = 0.6745 * diff / med_abs_deviation

    return modified_z_score > thresh

#def to_percent(y, position):
#    # Ignore the passed in position. This has the effect of scaling the default
#    # tick locations.
#    s = str(100 * y)
#
#    # The percent symbol needs escaping in latex
#    if matplotlib.rcParams['text.usetex'] is True:
#        return s + r'$\%$'
#    else:
#        return s + '%'

#x = randn(5000)

# Make a normed histogram. It'll be multiplied by 100 later.
#plt.hist(x, bins=50, normed=True)

# Create the formatter using the function to_percent. This multiplies all the
# default labels by 100, making them all percentages
#formatter = FuncFormatter(to_percent)

#plt.gca().yaxis.set_major_formatter(formatter)
for world_name, value in world_ranges_readable.items():
    x=world_ranges_readable[world_name]["human"]
    x=np.array(x)
    x=x[~is_outlier(x)] 
    #plt.hist(x,bins=int(math.floor(math.sqrt(len(x)))), normed=False)
    plt.hist(x,bins=int(math.floor((len(x))**(3./5.))), normed=False)
    clean_name="".join([c for c in world_name if c.isalpha() or c.isdigit() or c==' ']).rstrip()
    plt.title("Human SLs in "+clean_name+", min=%d,max=%d" %(min(x),max(x)))
    plt.savefig('Humans_'+clean_name+'.png')
    plt.clf()

