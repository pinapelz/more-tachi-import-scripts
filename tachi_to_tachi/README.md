# Tachi to Tachi
Supports:
- ONGEKI
- WACCA
- CHUNITHM
- maimai DX

Install a browser extension capable of running/managing userscripts (such as Tampermonkey)

Then [install the Tachi export script](https://gitea.tendokyu.moe/pinapelz/more-tachi-import-scripts/raw/branch/main/tachi_to_tachi/tachi_universal_export.user.js)

Visit the session page for a particular supported game i.e:
`https://kamai.tachi.ac/u/{USERNAME}/games/{GAME}/Single/sessions/{SESSION ID}/scores`

Select the `All Scores` option (if you are not on this tab already)

Then refresh the page, a button will show on the top right that exports all scores for the current session.

** Ensure that all scores are displayed on screen when scraping. (Suggested to always scroll down and change the display amount to 100)
