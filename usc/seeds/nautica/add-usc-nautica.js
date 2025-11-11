const { Command } = require("commander");
const sqlite3 = require("better-sqlite3");
const fs = require("fs");
const {
	CreateChartID,
	ReadCollection,
	WriteCollection,
	GetFreshSongIDGenerator,
} = require("../../util");

const program = new Command();
program.requiredOption("-d, --db <maps.db>");
program.requiredOption("-f, --filter <path_filter>");
program.option("--debug", "Show debug logs", false);
program.parse(process.argv);
const options = program.opts();

const DEBUG = options.debug;
const db = sqlite3(options.db);
const dbRows = db.prepare(`SELECT * FROM Charts WHERE path LIKE '%${options.filter}%'`).all();
console.log(`Found ${dbRows.length} charts.`);

const songs = ReadCollection("songs-usc.json");
const charts = ReadCollection("charts-usc.json");
const folderIdToSongId = {};

let newSongs = 0;
let newCharts = 0;

const getFreshSongID = GetFreshSongIDGenerator("usc");
const log = DEBUG ? console.log : () => undefined;

function makeUscEditionName(title, artist) {
	return `${title} (${artist} Nautica Edition)`;
}

for (const chart of dbRows) {
	// 1️⃣ Skip if chart already exists (same hash)
	const existingChart = charts.find((c) => c.data.hashSHA1 === chart.hash);
	if (existingChart) {
		log(
			`Chart ${chart.title} ${existingChart.difficulty} already exists (hash match, internalId=${chart.internalId}).`
		);
		continue;
	}

	// 2️⃣ Determine song
	if (!folderIdToSongId[chart.folderid]) {
		const splitPath = chart.path.replaceAll("\\", "/").split("/");
		const folderName = splitPath[splitPath.length - 2];

		const matchingSongs = songs.filter(
			(s) => s.title === chart.title && s.artist === chart.artist
		);

		let songID;
		if (matchingSongs.length === 0) {
			// normal song
			songID = getFreshSongID();
			songs.push({
				id: songID,
				title: chart.title,
				altTitles: [],
				artist: chart.artist,
				data: {},
				searchTerms: [folderName],
			});
			newSongs++;
			log(`Added song ${songID} for folder ${folderName}.`);
		} else {
			// duplicate name/artist → make USC Edition
			const effectorName = chart.effector ? chart.effector : "Unknown Effector";
			const uscTitle = makeUscEditionName(chart.title, effectorName);

			const existingUsc = songs.find((s) => s.title === uscTitle && s.artist === chart.artist);
			if (existingUsc) {
				songID = existingUsc.id;
				log(`Found existing USC edition song for ${chart.title}.`);
			} else {
				songID = getFreshSongID();
				songs.push({
					id: songID,
					title: uscTitle,
					altTitles: [chart.title],
					artist: chart.artist,
					data: {},
					searchTerms: [folderName],
				});
				newSongs++;
				log(`Duplicate name detected → created USC edition song ${uscTitle} (ID ${songID}).`);
			}
		}

		folderIdToSongId[chart.folderid] = songID;
	}

	const songID = folderIdToSongId[chart.folderid];

	// 3️⃣ Add charts, skip duplicates
	for (const playtype of ["Controller", "Keyboard"]) {
		const duplicate = charts.find(
			(c) =>
				c.songID === songID &&
				c.playtype === playtype &&
				c.difficulty === chart.diff_shortname &&
				c.isPrimary === true
		);

		if (duplicate) {
			log(
				`Skipped duplicate chart: ${chart.title} ${chart.diff_shortname} (${playtype}, songID=${songID}, internalId=${chart.internalId}).`
			);
			continue;
		}

		charts.push({
			chartID: CreateChartID(),
			data: {
				effector: chart.effector,
				hashSHA1: chart.hash,
				isOfficial: false,
				tableFolders: [],
			},
			difficulty: chart.diff_shortname,
			isPrimary: true,
			level: chart.level.toString(),
			levelNum: 0,
			playtype,
			songID,
			versions: [],
		});

		newCharts++;
		log(
			`Added chart ${chart.title} ${chart.diff_shortname} (${playtype}, internalId=${chart.internalId}).`
		);
	}
}

console.log(`Added ${newSongs} new songs and ${newCharts} new charts.`);

WriteCollection("songs-usc.json", songs);
WriteCollection("charts-usc.json", charts);
