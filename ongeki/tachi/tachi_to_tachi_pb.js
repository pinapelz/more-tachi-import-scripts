javascript:(function() {
  function toUnixMillis(s) {
    try { return new Date(s).getTime(); }
    catch { return null; }
  }

  const rows = document.querySelectorAll("table tbody tr");
  const scores = [];

  for (let i = 0; i < rows.length; i++) {
    const row = rows[i];
    const cells = row.querySelectorAll("td");
    if (cells.length < 11) continue;

    let chart = cells[0].innerText.trim().split(/\s+/)[0].toUpperCase();
    if (chart === "EXP") chart = "EXPERT";
    if (!["BASIC", "ADVANCED", "EXPERT", "MASTER", "LUNATIC"].includes(chart)) continue;

    const anchor = cells[2].querySelector("a");
    if (!anchor) continue;

    const parts = anchor.innerHTML.split("<br>");
    const temp = document.createElement("div");
    temp.innerHTML = parts[0];
    const title = temp.textContent.trim();
    temp.innerHTML = parts[1] || "";
    const artist = temp.textContent.trim();

    const scoreText = cells[4].innerText.trim().split("\n").pop().replace(/,/g, "");
    const score = parseInt(scoreText, 10);
    if (isNaN(score)) continue;

    const noteLamp = (cells[7].innerText.trim() || "UNKNOWN").toUpperCase();

    const small = cells[10].querySelector("small");
    const dateText = small?.textContent.trim();
    const timeAchieved = dateText ? toUnixMillis(dateText) : null;

    const judgementDiv = cells[6].querySelector("div");
    let cbreak = 0, breaks = 0, hit = 0, miss = 0, bellCount = 0, totalBellCount = 0, damage = 0;

    if (judgementDiv) {
      const spans = judgementDiv.parentElement.querySelectorAll("span");
      if (spans.length >= 4) {
        cbreak = parseInt(spans[0].textContent) || 0;
        breaks = parseInt(spans[1].textContent) || 0;
        hit = parseInt(spans[2].textContent) || 0;
        miss = parseInt(spans[3].textContent) || 0;
      }
      const bellDamageSpans = judgementDiv.parentElement.parentElement.querySelectorAll("span");
      if (bellDamageSpans.length >= 6) {
        const bellMatch = bellDamageSpans[4].textContent.match(/(\d+)\/(\d+)/);
        if (bellMatch) {
          bellCount = parseInt(bellMatch[1]);
          totalBellCount = parseInt(bellMatch[2]);
        }
        damage = parseInt(bellDamageSpans[5].textContent) || 0;
      }
    }

    scores.push({
      score,
      noteLamp,
      bellLamp: "NONE",
      matchType: "songTitle",
      identifier: title,
      artist,
      difficulty: chart,
      timeAchieved,
      judgements: { cbreak, break: breaks, hit, miss },
      optional: { bellCount, totalBellCount, damage }
    });
  }

  const result = {
    meta: {
      game: "ongeki",
      playtype: "Single",
      service: "bookmarkelt"
    },
    scores
  };

  const blob = new Blob([JSON.stringify(result, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "ongeki_batch_manual.json";
  a.click();
  URL.revokeObjectURL(url);
})();
