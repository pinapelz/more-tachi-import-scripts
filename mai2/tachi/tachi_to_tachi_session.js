javascript:void(async function () {
  function waitForRows() {
    return new Promise((resolve) => {
      const check = () => {
        const rows = document.querySelectorAll("table tbody tr");
        if (rows.length > 0) resolve(rows);
        else setTimeout(check, 500);
      };
      check();
    });
  }

  const difficultyMap = {
    "DX Basic": "DX Basic",
    "DX Advanced": "DX Advanced",
    "DX Expert": "DX Expert",
    "DX Master": "DX Master",
    "DX Re:Master": "DX Re:Master"
  };

  const lampMap = {
    "FAILED": "FAILED",
    "CLEAR": "CLEAR",
    "FULL COMBO": "FULL COMBO",
    "FULL COMBO+": "FULL COMBO+",
    "ALL PERFECT": "ALL PERFECT",
    "ALL PERFECT+": "ALL PERFECT+"
  };

  const gradeList = ["D", "C", "B", "BB", "BBB", "A", "AA", "AAA", "S", "S+", "SS", "SS+", "SSS", "SSS+"];

  const rows = await waitForRows();

  const results = {
    meta: {
      game: "maimaidx",
      playtype: "Single",
      service: "Tachi to Tachi PB Export"
    },
    scores: []
  };

  for (let i = 0; i < rows.length; i++) {
    const row = rows[i];
    if (row.classList.contains("expandable-pseudo-row") || row.classList.contains("fake-row")) continue;

    const cells = row.querySelectorAll("td");
    if (cells.length < 9) continue;

    const difficultyText = cells[0].innerText.split("\n")[0].trim();
    const difficulty = Object.keys(difficultyMap).find(d => difficultyText.includes(d)) || difficultyText;

    const titleAnchor = cells[2].querySelector("a");
    const title = titleAnchor?.childNodes[0]?.textContent.trim() || "";
    const artist = titleAnchor?.querySelector("small")?.textContent.trim() || "";

    const percentText = cells[3].innerText.trim();
    const percent = parseFloat(percentText.match(/([\d.]+)%/)?.[1]) || 0;
    const grade = gradeList.find(g => percentText.includes(g)) || "D";

    const judgmentSpans = cells[4].querySelectorAll("span");
    const [pcrit, perfect, great, good, miss] = Array.from(judgmentSpans).map(span => parseInt(span.textContent.trim()));

    const lampText = cells[5].innerText.trim();
    const lamp = lampMap[lampText] || "FAILED";

    const timeText = cells[7].querySelector("small")?.textContent?.trim();
    let timeAchieved = null;
    if (timeText) {
      const parsed = new Date(timeText);
      if (!isNaN(parsed)) {
        timeAchieved = parsed.getTime();
      }
    }

    const score = {
      identifier: title,
      artist,
      difficulty,
      percent,
      lamp,
      judgements: {
        pcrit,
        perfect,
        great,
        good,
        miss
      },
      matchType: "songTitle",
      timeAchieved: timeAchieved
    };

    results.scores.push(score);
  }

  const blob = new Blob([JSON.stringify(results, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "maimaidx_session_scores.json";
  document.body.appendChild(a);
  a.click();
  URL.revokeObjectURL(url);
})();
