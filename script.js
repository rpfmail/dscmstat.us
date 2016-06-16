document.addEventListener("DOMContentLoaded", function() {
  var playerCtx = document.getElementById("player-chart").getContext("2d");
  var worldCtx = document.getElementById("world-chart").getContext("2d");

  var createWorldChartData = function(data) {
    var playerNumbers = [];

    for (var key in data) {
      if (data.hasOwnProperty(key))
        playerNumbers.push(data[key]);
    }

    var dataset = {
      label: "Players by area",
      backgroundColor: "#1abc9c",
      data: playerNumbers
    };

    console.log(dataset);

    return { labels: Object.keys(data), datasets: [ dataset ] };
  };

  var r = new XMLHttpRequest();
  r.open("GET", "/stats.json", true);
  r.onreadystatechange = function() {
    if (r.readyState != 4 || r.status != 200) {
      return;
    }
    createCharts(r);
  };
  r.send();

  var createCharts = function(r) {
    var stats = JSON.parse(r.responseText);
    var players = stats.players;

    var playerChart = new Chart(playerCtx, {
      type: "pie",
      data: {
        labels: [
          "Hollows",
          "Humans",
          "Coop Phantoms",
          "Invaders"
        ],
        datasets: [{
          data: [
            stats.players.hollow,
            stats.players.human,
            stats.players.coop,
            stats.players.invader
          ],
          backgroundColor: ["#ccc", "#ecf0f1", "#f1c40f", "#c0392b"]
        }]
      },
      options: {}
    });

    var worldChart = new Chart(worldCtx, {
      type: "bar",
      data: createWorldChartData(stats.world_population)
    });
  };
});
