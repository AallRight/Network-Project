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


function convertMilliseconds(ms) {
    const totalSeconds = Math.floor(ms / 1000);
    const hours = Math.floor(totalSeconds / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const seconds = totalSeconds % 60;
    if (hours === NaN || minutes === NaN || seconds === NaN)
        return "00:00:00"
    return `${hours}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}

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
    let sliderInstance = slider.render({
        elem: '#progress',
        min: 0,
        max: totaltime,
        setTips: convertMilliseconds,
    })
    delete sliderInstance.config.done;
    if (isPause) {
        stopTimer();
        sliderInstance.setValue(time);
    } else {
        sliderInstance.setValue(Math.min(Date.now() - time), 0);
        startTimer(1000, () => {
            delete sliderInstance.config.done;
            sliderInstance.setValue(Math.min(Date.now() - time));
            sliderInstance.config.done = onProgressBarJump;
        });
    }
    sliderInstance.config.done = onProgressBarJump;
}

function renderVolume() {
    let sliderInstance = slider.render({
        elem: '#volume',
        min: 0,
        max: 100,
    })
    sliderInstance.setValue(volume);
}

// ================== 3. Event Handlers ==================

// ================== 3.1 User Operations Handlers ==================

function onMLibraryJump(obj, first) {
    if (!first) {
        sendQuery("getMLibrary", { page: obj.curr });
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
    // recover
}

function onTableTool(obj) {
    console.log(obj);
    if (obj.event === "play") {
        sendCommand("play", { sid: obj.data.sid })
    } else if (obj.event === "next") {
        sendCommand("waitlistAdd", { sid: obj.data.sid })
    } else if (obj.event === "up") {
        sendCommand("waitlistMove", { wid: obj.data.wid, offset: -1 })
    } else if (obj.event === "down") {
        sendCommand("waitlistMove", { wid: obj.data.wid, offset: 1 })
    } else if (obj.event === "remove") {
        sendCommand("waitlistDelete", { wid: obj.data.wid })
    } else {
        throw Error("Uncaught layevent.")
    }
}

// ================== 3.2 Update Handlers ==================


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
        activeSong = JSON.parse(downlinkMessage.activeSong.activeSong);
        volume = activeSong.volume;
        isPause = activeSong.is_pause;
        totaltime = Math.floor(activeSong.song.track_length * 1000);
        if (isPause) {
            time = activeSong.time;
        } else {
            time = activeSong.time_stamp;
        }
        renderProgressBar();
        renderVolume();
    }
});

// ================== 3.3 Refresh & init ==================

function refresh() {
    sendQuery("getWaitlist", {})
    sendQuery("getActiveSong", {})
    sendQuery("getMlibrary", { page: 1 });

    renderMLibrary();

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

    // renderProgressBar();

    renderVolume();

    table.on('tool(mlibrary-table)', onTableTool);
    table.on('tool(waitlist-table)', onTableTool);
}

async function main() {
    await init();
    await waitForUserId();
    layui.use(function () {
        element = layui.element;
        table = layui.table;
        laypage = layui.laypage;
        slider = layui.slider;

        refresh();
    });
}

main();

