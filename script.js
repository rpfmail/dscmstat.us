document.addEventListener("DOMContentLoaded", function() {

  Chart.defaults.global.animation.duration = 0;

  var playerStatusChart = new Chart(
    document.getElementById("player-status-chart"),
    {
      type: "pie",
      data: {
        labels: ["Hollows", "Humans", "Coop Phantoms", "Invaders"],
        datasets: []
      }
    }
  );

  var playersPerAreaChart = new Chart(
    document.getElementById("players-per-area-chart"),
    {
      type: "bar",
      data: {
        labels: [],
        datasets: []
      }
    }
  );

  var transformWorldData = function(playersPerWorld) {
    var values = [];
    var labels = [];

    for (var worldName in playersPerWorld) {
      if (playersPerWorld.hasOwnProperty(worldName) && worldName !== "None or loading") {
        values.push(playersPerWorld[worldName]);
        labels.push(worldName);
      }
    }

    var dataset = {
      label: "Players by area",
      backgroundColor: "#1abc9c",
      data: values
    };

    return { labels: labels, datasets: [ dataset ] };
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

  /**
   * Symmetric bubblesort. Any index in `a` will correspond to the same value
   * in `b`, before and after sorting.
   */
  var symmetricSort = function(a, b) {
    var n = a.length;
    var swapped = true;

    while (swapped) {
      swapped = false;
      for (var i = 1; i < n; i++) {
        if (a[i - 1] > a[i]) {
          var tmp  = a[i - 1];
          a[i - 1] = a[i];
          a[i]     = tmp;

          tmp      = b[i - 1];
          b[i - 1] = b[i];
          b[i]     = tmp;

          swapped = true;
        }
      }
    }
  };

  var updateCharts = function(stats) {
    document.getElementById("last-updated").innerHTML = "Last updated at " + stats.lastUpdated + ".";

    playerStatusChart.data.datasets = [{
      data: [
        stats.players.hollow,
        stats.players.human,
        stats.players.coop,
        stats.players.invader
      ],
      backgroundColor: ["#ccc", "#ecf0f1", "#f1c40f", "#c0392b"]
    }];
    playerStatusChart.update();

    var worldData = transformWorldData(stats.worlds);
    symmetricSort(worldData.datasets[0].data, worldData.labels);

    playersPerAreaChart.data.labels = worldData.labels;
    playersPerAreaChart.data.datasets[0] = worldData.datasets[0];

    playersPerAreaChart.update();
  };

  var updateFunc = fetchStats.bind(null, updateCharts);
  updateFunc();
  setInterval(updateFunc, 15 * 1000);

});
