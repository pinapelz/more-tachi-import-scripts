javascript:void(function () {
  function parseChunithmTable() {
    const rows = document.querySelectorAll("table.table tbody tr");
    const difficultyMap = {
      E: "Expert",
      A: "Advanced",
      B: "Basic",
      M: "Master"
    };
    const results = {
      meta: {
        game: "chunithm",
        playtype: "Single",
        service: "Tachi to Tachi PB Export",
      },
      scores: []
    };

    for (let i = 0; i < rows.length; i += 3) {
      const row = rows[i];
      if (!row) continue;

      const cells = row.querySelectorAll("td");
      if (cells.length < 11) continue;

      let difficulty = cells[1].innerText.trim().replace(/\n/, " ").split(" ")[0];
      if (difficulty.length === 1) {
        difficulty = difficultyMap[difficulty] || difficulty;
      }

      const songAnchor = cells[3].querySelector("a");
      const title = songAnchor?.childNodes[0]?.textContent.trim() || "";
      const artist = songAnchor?.querySelector("small")?.textContent.trim() || "";

      const scoreRank = cells[5].querySelector("strong")?.innerText.trim() || "";
      const scoreValue = parseInt(
        cells[5].innerText.replace(scoreRank, "").trim().replace(/,/g, "")
      );

      const judgementText = cells[6].innerText.trim();
      const parts = judgementText.split("-").map((x) => parseInt(x.trim()));
      const [jcrit, justice, attack, miss] = parts;

      const fastSlowMatch = judgementText.match(/\(F:(\d+)\s+S:(\d+)\)/);
      const fast = fastSlowMatch ? parseInt(fastSlowMatch[1]) : undefined;
      const slow = fastSlowMatch ? parseInt(fastSlowMatch[2]) : undefined;

      const lamp = cells[7].innerText.trim();
      const rating = parseFloat(cells[8].innerText.trim());

      const timestampText = cells[10].innerText.trim().split("\n");
      const timestampString = timestampText[1]?.trim() || "";
      const timeAchieved = timestampString ? new Date(timestampString).getTime() : 0;

      const score = {
        score: scoreValue,
        lamp,
        matchType: "songTitle",
        difficulty,
        identifier: title,
        artist,
        judgements: {
          jcrit,
          justice,
          attack,
          miss,
        },
        timeAchieved
      };

      if (fast !== undefined && slow !== undefined) {
        score.judgements.fast = fast;
        score.judgements.slow = slow;
      }

      results.scores.push(score);
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
