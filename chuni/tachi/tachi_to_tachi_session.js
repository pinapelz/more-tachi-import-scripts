javascript: void (function () {
  function parseChunithmTable() {
    const rows = document.querySelectorAll("table.table tbody tr");
    const results = {
      meta: {
        game: "chunithm",
        playtype: "Single",
        service: "Tachi to Tachi Export",
      },
      scores: [],
    };
    for (let i = 0; i < rows.length; i++) {
      const row = rows[i];
      const cells = row.querySelectorAll("td");
      if (
        cells.length < 9 ||
        row.classList.contains("expandable-pseudo-row") ||
        row.classList.contains("fake-row")
      )
        continue;
      let difficultyCell = cells[0];
      let difficultyText = difficultyCell.innerText.trim();
      let difficultyMatch = difficultyText.match(
        /(MASTER|EXPERT|ADVANCED|BASIC|M|E|A|B)/i,
      );
      let difficulty = difficultyMatch
        ? difficultyMatch[0].toUpperCase()
        : "UNKNOWN";
      const difficultyMap = {
        M: "Master",
        E: "Expert",
        A: "Advanced",
        B: "Basic",
      };
      if (difficulty.length === 1)
        difficulty = difficultyMap[difficulty] || difficulty;
      const songAnchor = cells[2].querySelector("a");
      const title = songAnchor?.childNodes[0]?.textContent.trim() || "";
      const artist =
        songAnchor?.querySelector("small")?.textContent.trim() || "";
      const scoreRank =
        cells[3].querySelector("strong")?.innerText.trim() || "";
      const scoreValue = parseInt(
        cells[3].innerText.replace(scoreRank, "").trim().replace(/,/g, ""),
      );
      const judgementText = cells[4].innerText.trim();
      const parts = judgementText.split("-").map((x) => parseInt(x.trim()));
      const [jcrit, justice, attack, miss] = parts;
      const lamp = cells[5].innerText.trim();
      const timestampCellLines = cells[7].innerText.trim().split("\n");
      const dateString =
        timestampCellLines.find((line) => /\w+ \d+, \d+/.test(line)) || "";
      const timeAchieved = dateString ? new Date(dateString).getTime() : 0;
      results.scores.push({
        score: scoreValue,
        lamp,
        matchType: "songTitle",
        difficulty,
        identifier: title,
        artist,
        judgements: { jcrit, justice, attack, miss },
        timeAchieved,
      });
    }
    return results;
  }
  function downloadJSON(data) {
    const blob = new Blob([JSON.stringify(data, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "chunithm_table.json";
    a.click();
    URL.revokeObjectURL(url);
  }
  const data = parseChunithmTable();
  downloadJSON(data);
})();
