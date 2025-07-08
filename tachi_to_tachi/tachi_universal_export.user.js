// ==UserScript==
// @name         Tachi Universal Export
// @namespace    https://tachi.pinapelz.com/
// @version      1.0
// @description  Universal export script for Tachi scores (Chunithm, Ongeki, Wacca, MaiMaiDX)
// @author       pinapelz
// @match        https://tachi.pinapelz.com/u/*/games/chunithm/Single/sessions/*/scores
// @match        https://tachi.pinapelz.com/u/*/games/ongeki/Single/sessions/*/scores
// @match        https://tachi.pinapelz.com/u/*/games/wacca/Single/sessions/*/scores
// @match        https://tachi.pinapelz.com/u/*/games/maimaidx/Single/sessions/*/scores
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    // Utility functions
    function toUnixMillis(s) {
        try { return new Date(s).getTime(); }
        catch { return null; }
    }

    function detectGame() {
        const url = window.location.href;
        if (url.includes('/games/chunithm/')) return 'chunithm';
        if (url.includes('/games/ongeki/')) return 'ongeki';
        if (url.includes('/games/wacca/')) return 'wacca';
        if (url.includes('/games/maimaidx/')) return 'maimaidx';
        return null;
    }

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

    function downloadJSON(data, filename) {
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    // Ongeki parser
    function parseOngekiScores() {
        const rows = document.querySelectorAll("table tbody tr");
        const scores = [];

        for (let i = 0; i < rows.length; i++) {
            const row = rows[i];
            if (!row || row.classList.contains("expandable-pseudo-row") || row.classList.contains("fake-row")) continue;

            const cells = row.querySelectorAll("td");
            if (cells.length < 10) continue;

            // Chart info is in first column
            let chartText = cells[0].querySelector("div.d-none.d-lg-block")?.textContent.trim() ||
                           cells[0].querySelector("div.d-lg-none")?.textContent.trim() || "";
            let chart = chartText.split(/\s+/)[0].toUpperCase();
            if (chart === "EXP") chart = "EXPERT";
            if (!["BASIC", "ADVANCED", "EXPERT", "MASTER", "LUNATIC"].includes(chart)) continue;

            // Song info is in third column (index 2)
            const anchor = cells[2].querySelector("a");
            if (!anchor) continue;

            const [titleHtml, artistHtml] = anchor.innerHTML.split("<br>");
            const temp = document.createElement("div");
            temp.innerHTML = titleHtml;
            const title = temp.textContent.trim();
            temp.innerHTML = artistHtml || "";
            const artist = temp.textContent.trim();

            // Score info is in fourth column (index 3)
            const scoreText = cells[3].innerText.trim().split("\n").pop().replace(/,/g, "");
            const score = parseInt(scoreText, 10);
            if (isNaN(score)) continue;

            // Platinum score is in fifth column (index 4)
            let platinumScore = 0;
            const platinumText = cells[4].innerText.trim();
            const platinumMatch = platinumText.match(/\[(\d+)\/(\d+)\]/);
            if (platinumMatch) {
                platinumScore = parseInt(platinumMatch[1], 10);
            }

            // Judgements are in sixth column (index 5)
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

                // Bell count is in a separate div within the same cell
                const bellDiv = judgementDiv.nextElementSibling;
                if (bellDiv) {
                    const bellMatch = bellDiv.textContent.match(/(\d+)\/(\d+)/);
                    if (bellMatch) {
                        bellCount = parseInt(bellMatch[1]);
                        totalBellCount = parseInt(bellMatch[2]);
                    }
                }
            }

            // Damage is in seventh column (index 6)
            let damage = 0;
            const damageText = cells[6].innerText.trim();
            damage = parseInt(damageText, 10) || 0;

            // Lamp is in eighth column (index 7)
            const noteLamp = (cells[7].innerText.trim() || "UNKNOWN").toUpperCase();

            // Timestamp is in tenth column (index 9)
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

        return {
            meta: {
                game: "ongeki",
                playtype: "Single",
                service: "Tampermonkey Tachi Universal Export"
            },
            scores
        };
    }

    // Chunithm parser
    function parseChunithmScores() {
        const rows = document.querySelectorAll("table.table tbody tr");
        const difficultyMap = {
            E: "Expert",
            A: "Advanced",
            B: "Basic",
            M: "Master"
        };
        const scores = [];

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
            let clearLamp = "FAILED";
            let noteLamp = "NONE";

            if (lamp.includes("FULL COMBO")) {
                noteLamp = "FULL COMBO";
                clearLamp = "CLEAR";
            }
            if (lamp.includes("CLEAR")) {
                clearLamp = "CLEAR";
            }
            if (lamp.includes("ALL JUSTICE")) {
                noteLamp = "ALL JUSTICE";
                clearLamp = "CLEAR";
            }
            if (lamp.includes("ALL JUSTICE CRITICAL")) {
                noteLamp = "ALL JUSTICE CRITICAL";
                clearLamp = "CLEAR";
            }
            if (lamp.includes("HARD")) {
                clearLamp = "HARD";
            }
            if (lamp.includes("BRAVE")) {
                clearLamp = "BRAVE";
            }
            if (lamp.includes("ABSOLUTE")) {
                clearLamp = "ABSOLUTE";
            }
            if (lamp.includes("CATASTROPHY")) {
                clearLamp = "CATASTROPHY";
            }

            const timestampText = cells[10].innerText.trim().split("\n");
            const timestampString = timestampText[1]?.trim() || "";
            const timeAchieved = timestampString ? new Date(timestampString).getTime() : 0;

            const score = {
                score: scoreValue,
                clearLamp,
                noteLamp,
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

            scores.push(score);
        }

        return {
            meta: {
                game: "chunithm",
                playtype: "Single",
                service: "Tampermonkey Tachi Universal Export"
            },
            scores
        };
    }

    // MaiMaiDX parser
    async function parseMaimaidxScores() {
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
        const scores = [];

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

            scores.push({
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
            });
        }

        return {
            meta: {
                game: "maimaidx",
                playtype: "Single",
                service: "Tampermonkey Tachi Universal Export"
            },
            scores
        };
    }

    // Wacca parser (using Ongeki PB structure as base)
    function parseWaccaScores() {
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

        return {
            meta: {
                game: "wacca",
                playtype: "Single",
                service: "Tampermonkey Tachi Universal Export"
            },
            scores
        };
    }

    // Add export button to page
    function addExportButton() {
        const button = document.createElement("button");
        button.textContent = "Export Scores";
        button.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            background: #007bff;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        `;
        button.onmouseover = () => button.style.background = "#0056b3";
        button.onmouseout = () => button.style.background = "#007bff";

        button.onclick = async () => {
            const game = detectGame();
            if (!game) {
                alert("Could not detect game type from URL");
                return;
            }

            button.textContent = "Exporting...";
            button.disabled = true;

            try {
                let result;
                let filename;

                switch (game) {
                    case 'ongeki':
                        result = parseOngekiScores();
                        filename = "ongeki_session_scores.json";
                        break;
                    case 'chunithm':
                        result = parseChunithmScores();
                        filename = "chunithm_session_scores.json";
                        break;
                    case 'maimaidx':
                        result = await parseMaimaidxScores();
                        filename = "maimaidx_session_scores.json";
                        break;
                    case 'wacca':
                        result = parseWaccaScores();
                        filename = "wacca_session_scores.json";
                        break;
                    default:
                        throw new Error("Unsupported game: " + game);
                }

                if (result.scores.length === 0) {
                    alert("No scores found to export");
                    return;
                }

                downloadJSON(result, filename);
                alert(`Exported ${result.scores.length} scores for ${game.toUpperCase()}`);
            } catch (error) {
                console.error("Export error:", error);
                alert("Error exporting scores: " + error.message);
            } finally {
                button.textContent = "Export Scores";
                button.disabled = false;
            }
        };

        document.body.appendChild(button);
    }

    // Initialize when page loads
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', addExportButton);
    } else {
        addExportButton();
    }
})();
