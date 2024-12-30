let element = null;
let table = null;
let laypage = null;
let slider = null;

// ================== 1. State & data ==================
const model = {
    mlibraryPageData: [],
    mlibraryPage: 1,
    mlibraryCount: 0,
    waitlistData: [],
    searchPageData: [
        { "sid": "1", "title": "abcdefg hijk lmn", "artist": "abcd", "album": "abcdefgh ijk lmn" },
        { "sid": "2", "title": "abcdefg hijk lmn", "artist": "abcd", "album": "abcdefgh ijk lmn" },
        { "sid": "3", "title": "abcdefg hijk lmn", "artist": "abcd", "album": "abcdefgh ijk lmn" },
        { "sid": "4", "title": "abcdefg hijk lmn", "artist": "abcd", "album": "abcdefgh ijk lmn" },
    ],
    searchPage: 1,
    searchCount: 25,
    isPause: true,
    time: 0, // ms
    timer: null,
    totaltime: 0, // ms
    volume: 50,
    song: null,
    voice: false,
    waitlistCols: [[
        { field: 'wid', title: '', width: 20, sort: true },
        { field: 'sid', title: 'ID', width: 20, sort: true },
        { field: 'title', title: '标题', width: "30%" },
        { field: 'artist', title: '艺术家', width: "20%" },
        { field: 'album', title: '专辑', width: "20%" },
        { width: 300, align: 'center', toolbar: '#waitlist-tool' },
    ]],
    mlibraryCols: [[
        { field: 'sid', title: 'ID', width: 20, sort: true },
        { field: 'title', title: '标题', width: "30%" },
        { field: 'artist', title: '艺术家', width: "20%" },
        { field: 'album', title: '专辑', width: "30%" },
        { width: 100, align: 'center', toolbar: '#mlibrary-tool' },
    ]],
    searchCols: [[
        { field: 'sid', title: 'ID', width: 20, sort: true },
        { field: 'title', title: '标题', width: "30%" },
        { field: 'artist', title: '艺术家', width: "20%" },
        { field: 'album', title: '专辑', width: "30%" },
        { width: 100, align: 'center', toolbar: '#search-tool' },
    ]],

    // Start a timer that will periodically execute a callback function.
    startTimer(interval, func) {
        if (this.timer) {
            clearInterval(this.timer);
        }
        this.timer = setInterval(func, interval);
    },

    stopTimer() {
        if (this.timer) {
            clearInterval(this.timer);
            this.timer = null;
        }
    },
}

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
        cols: model.mlibraryCols,
        data: model.mlibraryPageData,
        skin: 'line',
    });

    laypage.render({
        elem: 'mlibrary-page',
        count: model.mlibraryCount,
        limit: 10,
        curr: model.mlibraryPage,
        layout: ["prev", "next", "page"],
        jump: onMLibraryJump
    });
}

function renderWaitlist() {
    laypage.render({
        elem: 'waitlist-page',
        count: model.waitlistData.length,
        limit: 10,
        curr: 1,
        layout: ["prev", "next", "page"],
        jump: function (obj, first) {
            let page = obj.curr - 1;
            table.render({
                elem: '#waitlist-table',
                cols: model.waitlistCols,
                data: model.waitlistData.slice(10 * page, 10 * page + 10),
                skin: 'line',
            });
        }
    });
}

function renderSearch() {
    table.render({
        elem: '#search-table',
        cols: model.searchCols,
        data: model.searchPageData,
        skin: 'line',
    });

    laypage.render({
        elem: 'search-page',
        count: model.searchCount,
        limit: 10,
        curr: model.searchPage,
        layout: ["prev", "next", "page"],
        jump: model.onSearchJump
    })
}

function renderProgressBar() {
    let inst = slider.render({
        elem: '#progress',
        min: 0,
        max: model.totaltime,
        setTips: convertMilliseconds,
    })
    delete inst.config.done; // setValue will trigger the done callback function
    if (model.isPause) {
        model.stopTimer();
        inst.setValue(model.time);
    } else {
        inst.setValue(Math.min(Date.now() - model.time), 0);
        model.startTimer(1000, () => {
            // Render every 1 second
            delete inst.config.done;
            inst.setValue(Math.min(Date.now() - model.time));
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
    inst.setValue(model.volume);
    inst.config.done = onVolumeSet;
}

function renderControlPanel() {
    document.querySelector("#play-button span").innerText = model.isPause ? String.fromCharCode(0xe614) : String.fromCharCode(0xe60f);
}

function renderSongTitle() {
    document.getElementById("song_title").innerText = model.song ? model.song.title : "没有正在播放的歌曲";
}

// ================== 3. Event Handlers ==================

// ================== 3.1 User Operations Handlers ==================

function onMLibraryJump(obj, first) {
    if (!first) {
        control.sendQuery("getMlibrary", { page: obj.curr });
        obj.curr = model.mlibraryPage; // recover
    }
}

function onSearchJump(obj, first) {
    if (!first) {
        console.log("Fetch Search page ", obj.curr); // TODO
        obj.curr = model.searchPage; // recover
    }
}

function onProgressBarJump(value) {
    control.sendCommand("jump", { time: Math.floor(value) });
    // no recover
}

function onVolumeSet(value) {
    control.sendCommand("adjustVolume", { volume: value });
    // no recover
}

function onPlayButtonClick() {
    if (model.isPause && model.song) {
        control.sendCommand("play", { sid: model.song.sid, time: model.time });
    } else {
        control.sendCommand("pause", {});
    }
}

function onPlayNextButtonClick() {
    control.sendCommand("playNext", {});
}

function onVoiceButtonClick() {
    if (!model.voice) {
        if (media.startRecording())
            model.voice = true;
    } else {
        if (media.stopRecording())
            model.voice = false;
    }
}

function onTableTool(obj) {
    console.log(obj);
    if (obj.event === "play") {
        control.sendCommand("play", { sid: obj.data.sid });
    } else if (obj.event === "next") {
        control.sendCommand("waitlistAdd", { sid: obj.data.sid });
    } else if (obj.event === "up") {
        control.sendCommand("waitlistMove", { wid: obj.data.wid, offset: -1 });
    } else if (obj.event === "down") {
        control.sendCommand("waitlistMove", { wid: obj.data.wid, offset: 1 });
    } else if (obj.event === "remove") {
        control.sendCommand("waitlistDelete", { wid: obj.data.wid });
    } else {
        throw Error("Uncaught layevent.");
    }
}

// ================== 3.2 Update Handler ==================


window.addEventListener('onReceiveDownlinkMessage', function (e) {
    let downlinkMessage = e.detail.message;
    if (downlinkMessage.waitlist) {
        if (downlinkMessage.waitlist.songs) {
            model.waitlistData = downlinkMessage.waitlist.songs.map(jsonStr => JSON.parse(jsonStr));
            model.waitlistData.forEach((item, index) => {
                item.wid = index + 1;
            });
        } else
            model.waitlistData = [];
        renderWaitlist();
    } else if (downlinkMessage.mlibrary) {
        model.mlibraryPage = downlinkMessage.mlibrary.page;
        model.mlibraryCount = downlinkMessage.mlibrary.count;
        if (downlinkMessage.mlibrary.songs)
            model.mlibraryPageData = downlinkMessage.mlibrary.songs.map(jsonStr => JSON.parse(jsonStr));
        else
            model.mlibraryPageData = [];
        renderMLibrary();
    } else if (downlinkMessage.activeSong) {
        let activeSong = JSON.parse(downlinkMessage.activeSong.activeSong);
        model.volume = activeSong.volume;
        model.isPause = activeSong.is_pause;
        if (model.isPause) {
            model.time = activeSong.time;
        } else {
            model.time = activeSong.time_stamp;
        }
        if (activeSong.song) {
            model.song = activeSong.song;
            model.totaltime = Math.floor(model.song.track_length * 1000);
            renderProgressBar();
        }
        renderVolume();
        renderControlPanel();
        renderSongTitle();
    }
});

// ================== 3.3 Refresh & init ==================

function refresh() {
    control.sendQuery("getWaitlist", {})
    control.sendQuery("getActiveSong", {})
    control.sendQuery("getMlibrary", { page: 1 });

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
    document.getElementById("voice-button").addEventListener("click", onVoiceButtonClick);
}

async function main() {
    await control.initConnection();
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

