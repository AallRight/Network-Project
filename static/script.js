let element = null;
let table = null;
let laypage = null;
let slider = null;

// ================== 1. State & data ==================

let mlibraryPageData = [];
let mlibraryPage = 1;
let mlibraryCount = 0;

let waitlistData = [];

let searchPageData = [{
    "sid": "1",
    "title": "abcdefg hijk lmn",
    "artist": "abcd",
    "album": "abcdefgh ijk lmn",
}, {
    "sid": "2",
    "title": "abcdefg hijk lmn",
    "artist": "abcd",
    "album": "abcdefgh ijk lmn",
}, {
    "sid": "3",
    "title": "abcdefg hijk lmn",
    "artist": "abcd",
    "album": "abcdefgh ijk lmn",
}, {
    "sid": "4",
    "title": "abcdefg hijk lmn",
    "artist": "abcd",
    "album": "abcdefgh ijk lmn",
}]; // fake

let searchPage = 1;
let searchCount = 25;

let isPause = true;
let time = 0; // ms
let timer;
let totaltime = 0; // ms

let volume = 50;

let song;


const waitlistCols = [[
    { field: 'wid', title: '', width: 20, sort: true },
    { field: 'sid', title: 'ID', width: 20, sort: true },
    { field: 'title', title: '标题', width: "30%" },
    { field: 'artist', title: '艺术家', width: "20%" },
    { field: 'album', title: '专辑', width: "20%" },
    { width: 300, align: 'center', toolbar: '#waitlist-tool' },
]];

const mlibraryCols = [[
    { field: 'sid', title: 'ID', width: 20, sort: true },
    { field: 'title', title: '标题', width: "30%" },
    { field: 'artist', title: '艺术家', width: "20%" },
    { field: 'album', title: '专辑', width: "30%" },
    { width: 100, align: 'center', toolbar: '#mlibrary-tool' },
]];

const searchCols = [[
    { field: 'sid', title: 'ID', width: 20, sort: true },
    { field: 'title', title: '标题', width: "30%" },
    { field: 'artist', title: '艺术家', width: "20%" },
    { field: 'album', title: '专辑', width: "30%" },
    { width: 100, align: 'center', toolbar: '#search-tool' },
]];


// Convert milliseconds to hh:mm:ss format for displaying progress bar hints.
function convertMilliseconds(ms) {
    const totalSeconds = Math.floor(ms / 1000);
    const hours = Math.floor(totalSeconds / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const seconds = totalSeconds % 60;
    if (hours === NaN || minutes === NaN || seconds === NaN)
        return "00:00:00";
    return `${hours}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}

// Start a timer that will periodically execute a callback function.
function startTimer(interval, func) {
    if (timer) {
        clearInterval(timer);
    }
    timer = setInterval(func, interval);
}

function stopTimer() {
    if (timer) {
        clearInterval(timer);
        timer = null;
    }
}

// ================== 2. Renderers ==================

/*
 * +---------------------------------------+
 * |                         SongTitle     |
 * | +----------+ +---------+ +----------+ |
 * | |          | |         | |          | |
 * | |          | |         | |          | |
 * | |          | |         | |          | |
 * | |          | |         | |          | |
 * | | MLibrary | | Search  | | Waitlist | |
 * | |          | |         | |          | |
 * | |          | |         | |          | |
 * | |          | |         | |          | |
 * | |          | |         | |          | |
 * | |          | |         | |          | |
 * | |          | |         | |          | |
 * | +----------+ +---------+ +----------+ |
 * +------------+---------------+----------+
 * |  Control   |  ProgressBar  | Volume   |
 * |  Panel     |               |          |
 * +------------+---------------+----------+
 */


function renderMLibrary() {
    table.render({
        elem: '#mlibrary-table',
        cols: mlibraryCols,
        data: mlibraryPageData,
        skin: 'line',
    });

    laypage.render({
        elem: 'mlibrary-page',
        count: mlibraryCount,
        limit: 10,
        curr: mlibraryPage,
        layout: ["prev", "next", "page"],
        jump: onMLibraryJump
    });
}

function renderWaitlist() {
    laypage.render({
        elem: 'waitlist-page',
        count: waitlistData.length,
        limit: 10,
        curr: 1,
        layout: ["prev", "next", "page"],
        jump: function (obj, first) {
            let page = obj.curr - 1;
            table.render({
                elem: '#waitlist-table',
                cols: waitlistCols,
                data: waitlistData.slice(10 * page, 10 * page + 10),
                skin: 'line',
            });
        }
    });
}

function renderSearch() {
    table.render({
        elem: '#search-table',
        cols: searchCols,
        data: searchPageData,
        skin: 'line',
    });

    laypage.render({
        elem: 'search-page',
        count: searchCount,
        limit: 10,
        curr: searchPage,
        layout: ["prev", "next", "page"],
        jump: onSearchJump
    })
}

function renderProgressBar() {
    let inst = slider.render({
        elem: '#progress',
        min: 0,
        max: totaltime,
        setTips: convertMilliseconds,
    })
    delete inst.config.done; // setValue will trigger the done callback function
    if (isPause) {
        stopTimer();
        inst.setValue(time);
    } else {
        inst.setValue(Math.min(Date.now() - time), 0);
        startTimer(1000, () => {
            // Render every 1 second
            delete inst.config.done;
            inst.setValue(Math.min(Date.now() - time));
            inst.config.done = onProgressBarJump;
        });
    }
    inst.config.done = onProgressBarJump;
}

function renderVolume() {
    let inst = slider.render({
        elem: '#volume',
        min: 0,
        max: 100,
    })
    delete inst.config.done; // setValue will trigger the done callback function
    inst.setValue(volume);
    inst.config.done = onVolumeSet;
}

function renderControlPanel() {
    document.querySelector("#play-button span").innerText = isPause ? String.fromCharCode(0xe614) : String.fromCharCode(0xe60f);
}

function renderSongTitle() {
    document.getElementById("song_title").innerText = song ? song.title : "没有正在播放的歌曲";
}

// ================== 3. Event Handlers ==================

// ================== 3.1 User Operations Handlers ==================

function onMLibraryJump(obj, first) {
    if (!first) {
        sendQuery("getMlibrary", { page: obj.curr });
        obj.curr = mlibraryPage; // recover
    }
}

function onSearchJump(obj, first) {
    if (!first) {
        console.log("Fetch Search page ", obj.curr); // TODO
        obj.curr = searchPage; // recover
    }
}

function onProgressBarJump(value) {
    sendCommand("jump", { time: Math.floor(value) });
    // no recover
}

function onVolumeSet(value) {
    sendCommand("adjustVolume", { volume: value });
    // no recover
}

function onPlayButtonClick() {
    if (isPause && song) {
        sendCommand("play", { sid: song.sid, time: time });
    } else {
        sendCommand("pause", {});
    }
}

function onPlayNextButtonClick() {
    sendCommand("playNext", {});
}


function onTableTool(obj) {
    console.log(obj);
    if (obj.event === "play") {
        sendCommand("play", { sid: obj.data.sid });
    } else if (obj.event === "next") {
        sendCommand("waitlistAdd", { sid: obj.data.sid });
    } else if (obj.event === "up") {
        sendCommand("waitlistMove", { wid: obj.data.wid, offset: -1 });
    } else if (obj.event === "down") {
        sendCommand("waitlistMove", { wid: obj.data.wid, offset: 1 });
    } else if (obj.event === "remove") {
        sendCommand("waitlistDelete", { wid: obj.data.wid });
    } else {
        throw Error("Uncaught layevent.");
    }
}

// ================== 3.2 Update Handler ==================


window.addEventListener('onReceiveDownlinkMessage', function (e) {
    let downlinkMessage = e.detail.message;
    if (downlinkMessage.waitlist) {
        if (downlinkMessage.waitlist.songs) {
            waitlistData = downlinkMessage.waitlist.songs.map(jsonStr => JSON.parse(jsonStr));
            waitlistData.forEach((item, index) => {
                item.wid = index + 1;
            });
        } else
            waitlistData = [];
        renderWaitlist();
    } else if (downlinkMessage.mlibrary) {
        mlibraryPage = downlinkMessage.mlibrary.page;
        mlibraryCount = downlinkMessage.mlibrary.count;
        if (downlinkMessage.mlibrary.songs)
            mlibraryPageData = downlinkMessage.mlibrary.songs.map(jsonStr => JSON.parse(jsonStr));
        else
            mlibraryPageData = [];
        renderMLibrary();
    } else if (downlinkMessage.activeSong) {
        let activeSong = JSON.parse(downlinkMessage.activeSong.activeSong);
        volume = activeSong.volume;
        isPause = activeSong.is_pause;
        if (isPause) {
            time = activeSong.time;
        } else {
            time = activeSong.time_stamp;
        }
        if (activeSong.song) {
            song = activeSong.song;
            totaltime = Math.floor(song.track_length * 1000);
            renderProgressBar();
        }
        renderVolume();
        renderControlPanel();
        renderSongTitle();
    }
});

// ================== 3.3 Refresh & init ==================

function refresh() {
    sendQuery("getWaitlist", {})
    sendQuery("getActiveSong", {})
    sendQuery("getMlibrary", { page: 1 });

    element.on('tab(main-test)', function (data) {
        if (data.index === 0) {
            renderMLibrary();
        } else if (data.index === 1) {
            renderSearch();
        } else if (data.index === 2) {
            renderWaitlist();
        }
        console.log("tabpage", data.index);
    });

    table.on('tool(mlibrary-table)', onTableTool);
    table.on('tool(waitlist-table)', onTableTool);
    document.getElementById("playnext-button").addEventListener("click", onPlayNextButtonClick);
    document.getElementById("play-button").addEventListener("click", onPlayButtonClick);
}

async function main() {
    await initConnection();
    layui.use(function () {
        element = layui.element;
        table = layui.table;
        laypage = layui.laypage;
        slider = layui.slider;
        refresh();
    });
}

document.addEventListener('DOMContentLoaded', function() {
    main();
});

