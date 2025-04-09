javascript:(function(){
  var rows = document.querySelectorAll("table tbody tr"),
      songs = [];
  rows.forEach(function(row) {
    var songAnchor = row.querySelector("td:nth-child(4) a");
    if (!songAnchor) return;
    var cells = row.cells;
    var chartDiv = cells[1].querySelector("div.d-none.d-lg-block"),
        chart = chartDiv ? chartDiv.textContent.trim() : cells[1].textContent.trim();
    var songTitle = "", artist = "";
    if (songAnchor) {
      var parts = songAnchor.innerHTML.split("<br>");
      if (parts.length >= 2) {
        var temp = document.createElement("div");
        temp.innerHTML = parts[0];
        songTitle = temp.textContent.trim();
        temp.innerHTML = parts[1];
        artist = temp.textContent.trim();
      } else {
        songTitle = songAnchor.textContent.trim();
      }
    }

    var scoreCell = cells[5],
        scoreText = scoreCell.textContent.replace((scoreCell.querySelector("strong") || {}).textContent.trim() || "", "").trim(),
        scorePoints = parseInt(scoreText.replace(/,/g, ""));

    var judgementText = cells[6].textContent.trim(),
        judgements = judgementText.split("-").map(function(item) {
          return parseInt(item.trim());
        });

    var lamp = cells[7].textContent.trim();

    var timeCell = cells[10];
    var timeString = timeCell ? timeCell.querySelector("small")?.textContent?.trim() : null;
    var timeUnix = timeString ? new Date(timeString).getTime() : null;

    songs.push({
      difficulty: chart.split(" ")[0],
      matchType: "songTitle",
      identifier: songTitle,
      artist: artist,
      score: scorePoints,
      judgements: {
        marvelous: judgements[0],
        great: judgements[1],
        good: judgements[2],
        miss: judgements[3]
      },
      lamp: lamp,
      timeAchieved: timeUnix
    });
  });

  const results = {
    meta: {
      game: "wacca",
      playtype: "Single",
      service: "Tachi to Tachi PB Export"
    },
    scores: songs
  };

  var json = JSON.stringify(results, null, 2),
      blob = new Blob([json], { type: "application/json" }),
      url = URL.createObjectURL(blob),
      a = document.createElement("a");
  a.setAttribute("download", "songs.json");
  a.setAttribute("href", url);
  a.style.display = "none";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
})();
