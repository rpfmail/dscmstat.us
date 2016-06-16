document.addEventListener("DOMContentLoaded", function() {
  Chart.defaults.global.animation.duration = 0;

  var id = document.getElementById.bind(document);

  var eachProperty = function(object, callback) {
    if (typeof callback !== "function") {
      throw "callback is not a function";
    }

    for (var key in object) {
      if (object.hasOwnProperty(key)) {
        callback(key, object[key]);
      }
    }
  };

  var Colors = {
    invader: "#c0392b",
    human: "#ecf0f1",
    coopPhantom: "#f1c40f",
    hollow: "#ccc"
  };

  var playerStatusChart = new Chart(id("player-status-chart"), {
      type: "pie",
      data: {
        labels: ["Hollows", "Humans", "Coop Phantoms", "Invaders"],
        datasets: []
      }
  });

  var playersPerAreaChart = new Chart(id("players-per-area-chart"), {
      type: "bar",
      data: { labels: [], datasets: [] },
      options: {
        scales: {
          yAxes: [{ stacked: true }],
          xAxes: [{ stacked: true }]
        }
      }
  });

  /**
   * Symmetric bubblesort. Any index in `a` will correspond to the same value
   * in every array within `s`, before and after sorting.
   */
  var symmetricSort = function(a, s) {
    var n = a.length;
    var swapped = true;

    while (swapped) {
      swapped = false;
      for (var i = 1; i < n; i++) {
        if (a[i] < a[i - 1]) {
          var tmp  = a[i - 1];
          a[i - 1] = a[i    ];
          a[i    ] = tmp;

          for (var j = 0; j < s.length; j++) {
            var b     = s[j    ];
            tmp       = b[i - 1];
            b[i - 1 ] = b[i    ];
            b[i     ] = tmp;
          }

          swapped = true;
        }
      }
    }
  };

  var transformWorldData = function(playersPerWorld) {
    var labels = [];
    var values = { total: [], hollow: [], human: [], coop: [], invader: [] };

    eachProperty(playersPerWorld, function(worldName, world) {
      if (worldName === "None or loading") { return; }

      eachProperty(world, function(phantomType, count) {
        if (values.hasOwnProperty(phantomType)) {
          values[phantomType].push(count);
        }
      });

      labels.push(worldName);
    });

    symmetricSort(values.total, [values.hollow, values.human, values.coop, values.invader, labels]);

    return {
      labels: labels,
      datasets: [
        { label: "Hollows", backgroundColor: Colors.hollow, data: values.hollow },
        { label: "Humans", backgroundColor: Colors.human, data: values.human },
        { label: "Coop Phantoms", backgroundColor: Colors.coopPhantom, data: values.coop },
        { label: "Invaders", backgroundColor: Colors.invader, data: values.invader },
      ]
    };
  };

  var fetchStats = function(callback) {
    var r = new XMLHttpRequest();
    r.open("GET", "/stats.json", true);
    r.onreadystatechange = function() {
      if (r.readyState != 4 || r.status != 200) {
        return;
      }
      callback(JSON.parse(r.responseText));
    };
    r.send();
  };

  var updateCharts = function(stats) {
    id("last-updated").innerHTML = "Last update at " + stats.lastUpdated + ".";

    playerStatusChart.data.datasets = [{
      data: [
        stats.players.hollow,
        stats.players.human,
        stats.players.coop,
        stats.players.invader
      ],
      backgroundColor: [ Colors.hollow, Colors.human, Colors.coopPhantom, Colors.invader ]
    }];
    playerStatusChart.update();

    var worldData = transformWorldData(stats.worlds);
    playersPerAreaChart.data.labels = worldData.labels;
    playersPerAreaChart.data.datasets = worldData.datasets;
    playersPerAreaChart.update();
  };

  var updateFunc = fetchStats.bind(null, updateCharts);
  updateFunc();
  setInterval(updateFunc, 15 * 1000);

});
