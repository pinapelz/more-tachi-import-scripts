javascript:(function () {
  function toUnixMillis(s) {
    try { return new Date(s).getTime(); }
    catch { return null; }
  }

  const rows = document.querySelectorAll("table tbody tr");
  const scores = [];

  for (let i = 0; i < rows.length; i++) {
    const row = rows[i];
    if (!row || row.classList.contains("expandable-pseudo-row") || row.classList.contains("fake-row")) continue;

    const cells = row.querySelectorAll("td");
    if (cells.length < 10) continue;

    let chartText = cells[0].querySelector("div.d-none.d-lg-block")?.textContent.trim() ||
                    cells[0].querySelector("div.d-lg-none")?.textContent.trim() || "";
    let chart = chartText.split(/\s+/)[0].toUpperCase();
    if (chart === "EXP") chart = "EXPERT";
    if (!["BASIC", "ADVANCED", "EXPERT", "MASTER", "LUNATIC"].includes(chart)) continue;

    const anchor = cells[2].querySelector("a");
    if (!anchor) continue;

    const [titleHtml, artistHtml] = anchor.innerHTML.split("<br>");
    const temp = document.createElement("div");
    temp.innerHTML = titleHtml;
    const title = temp.textContent.trim();
    temp.innerHTML = artistHtml || "";
    const artist = temp.textContent.trim();

    const scoreText = cells[3].innerText.trim().split("\n").pop().replace(/,/g, "");
    const score = parseInt(scoreText, 10);
    if (isNaN(score)) continue;

    let platinumScore = 0;
    const platinumText = cells[4].innerText.trim();
    const platinumMatch = platinumText.match(/\[(\d+)\/(\d+)\]/);
    if (platinumMatch) {
      platinumScore = parseInt(platinumMatch[1], 10);
    }

    let cbreak = 0, breaks = 0, hit = 0, miss = 0, bellCount = 0, totalBellCount = 0;
    const judgementDiv = cells[5].querySelector("strong > div");
    if (judgementDiv) {
      const judgementSpans = judgementDiv.querySelectorAll("span");
      if (judgementSpans.length >= 4) {
        cbreak = parseInt(judgementSpans[0].textContent) || 0;
        breaks = parseInt(judgementSpans[1].textContent) || 0;
        hit = parseInt(judgementSpans[2].textContent) || 0;
        miss = parseInt(judgementSpans[3].textContent) || 0;
      }

      const bellDiv = judgementDiv.nextElementSibling;
      if (bellDiv) {
        const bellMatch = bellDiv.textContent.match(/(\d+)\/(\d+)/);
        if (bellMatch) {
          bellCount = parseInt(bellMatch[1]);
          totalBellCount = parseInt(bellMatch[2]);
        }
      }
    }

    let damage = 0;
    const damageText = cells[6].innerText.trim();
    damage = parseInt(damageText, 10) || 0;

    const noteLamp = (cells[7].innerText.trim() || "UNKNOWN").toUpperCase();

    let timeAchieved = null;
    const smallTags = cells[9].querySelectorAll("small");
    if (smallTags.length > 0) {
      timeAchieved = toUnixMillis(smallTags[0].textContent.trim());
    }

    scores.push({
      score,
      platinumScore,
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
      service: "bookmarklet Tachi to Tachi"
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
