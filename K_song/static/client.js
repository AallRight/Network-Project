// 配置服务器地址
// const SERVER_IP = "10.180.250.50"; // 替换为服务器地址
const SERVER_IP = "127.0.0.1"; // 替换为服务器地址
const SERVER_PORT = 9000; // websocket 服务器端口
const RTC_PORT = 5000; // RTC 服务器端口

let peerConnection = null; // RTCPeerConnection 实例
let localStream = null; // 本地音频流
let connectionId = null; // 服务器返回的连接 ID

// 工具函数：发送数据到服务器
async function sendToServer(endpoint, data) {
    const url = `http://${SERVER_IP}:${SERVER_PORT}/${endpoint}`;
    try {
        const response = await fetch(url, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data),
        });
        if (!response.ok) throw new Error(response.statusText);
        return await response.json();
    } catch (error) {
        console.error(`Error sending to ${endpoint}:`, error);
    }
}

// 工具函数：发送数据到 RTC 服务器
async function sendToRTC(endpoint, data) {
    const url = `http://${SERVER_IP}:${RTC_PORT}/${endpoint}`;
    try {
        const response = await fetch(url, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data),
        });
        if (!response.ok) throw new Error(response.statusText);
        return await response.json();
    } catch (error) {
        console.error(`Error sending to ${endpoint}:`, error);
    }
}


// 工具函数：启用/禁用按钮
function toggleButtonState(buttonId, isEnabled) {
    const button = document.getElementById(buttonId);
    if (button) button.disabled = !isEnabled;
}

// 调整发送器参数（优化延时与音质）
function configureSenderParameters(pc) {
    const audioSender = pc.getSenders().find(sender => sender.track && sender.track.kind === "audio");
    if (audioSender) {
        const params = audioSender.getParameters();
        if (!params.encodings) params.encodings = [{}];
        params.encodings[0].ptime = 10; // 设置帧时间 10ms
        params.encodings[0].maxBitrate = 32000; // 最大比特率 32kbps
        audioSender.setParameters(params);
    }
}

// 事件处理器：开始录音
async function startRecording() {
    try {
        // 获取本地音频流
        localStream = await navigator.mediaDevices.getUserMedia({ audio: true });

        // 初始化 RTCPeerConnection
        peerConnection = new RTCPeerConnection();
        localStream.getTracks().forEach(track => peerConnection.addTrack(track, localStream));
        configureSenderParameters(peerConnection);

        // 创建 Offer 并发送到服务器
        const offer = await peerConnection.createOffer();
        await peerConnection.setLocalDescription(offer);

        const response = await sendToRTC("offer", { sdp: offer.sdp });
        connectionId = response.connection_id;

        // 设置服务器返回的 Answer
        await peerConnection.setRemoteDescription({
            type: response.type,
            sdp: response.sdp,
        });

        // 处理 ICE 候选
        peerConnection.onicecandidate = async event => {
            if (event.candidate) {
                await sendToRTC(`ice-candidate/${connectionId}`, { candidate: event.candidate });
            }
        };

        console.log("Recording started and connected to server!");
        toggleButtonState("connect", false);
        toggleButtonState("disconnect", true);
    } catch (error) {
        console.error("Error during setup:", error);
    }
}

// 事件处理器：停止录音
async function stopRecording() {
    try {
        if (localStream) localStream.getTracks().forEach(track => track.stop());
        if (connectionId) await sendToRTC(`close/${connectionId}`, {});
        if (peerConnection) peerConnection.close();

        peerConnection = null;
        localStream = null;
        connectionId = null;

        console.log("Recording stopped and connection closed!");
        toggleButtonState("connect", true);
        toggleButtonState("disconnect", false);
    } catch (error) {
        console.error("Error during cleanup:", error);
    }
}

// 事件处理器：播放歌曲
async function playMusic() {
    try {
        await sendToServer("play_local", {});
        toggleButtonState("play-music", false);
        toggleButtonState("pause-music", true);
        toggleButtonState("forward-music", true);
        toggleButtonState("backward-music", true);
    } catch (error) {
        console.error("Error playing music:", error);
    }
}

// 事件处理器：暂停歌曲
async function pauseMusic() {
    try {
        await sendToServer("pause_local", {});
        toggleButtonState("play-music", true);
        toggleButtonState("pause-music", false);
        toggleButtonState("forward-music", false);
        toggleButtonState("backward-music", false);
    } catch (error) {
        console.error("Error pausing music:", error);
    }
}

// 事件处理器：调整歌曲播放时间
async function adjustPlaybackTime(offset) {
    try {
        await sendToServer("adjust_time", { time: offset });
    } catch (error) {
        console.error(`Error adjusting playback time by ${offset} seconds:`, error);
    }
}

// 事件处理器：打开麦克风
async function openMicrophone() {
    try {
        await sendToServer("open_mic", {});
        toggleButtonState("open-mic", false);
        toggleButtonState("close-mic", true);
    } catch (error) {
        console.error("Error opening microphone:", error);
    }
}

// 事件处理器：关闭麦克风
async function closeMicrophone() {
    try {
        await sendToServer("close_mic", {});
        toggleButtonState("open-mic", true);
        toggleButtonState("close-mic", false);
    } catch (error) {
        console.error("Error closing microphone:", error);
    }
}

// 事件处理器：调整音量
async function adjustVolume(endpoint, increment) {
    try {
        await sendToServer(endpoint, { volume: increment });
    } catch (error) {
        console.error(`Error adjusting volume (${endpoint}):`, error);
    }
}

// 按钮事件绑定
document.getElementById("connect").addEventListener("click", startRecording);
document.getElementById("disconnect").addEventListener("click", stopRecording);
document.getElementById("play-music").addEventListener("click", playMusic);
document.getElementById("pause-music").addEventListener("click", pauseMusic);
document.getElementById("forward-music").
    addEventListener("click", () => adjustPlaybackTime(10));
document.getElementById("backward-music").
    addEventListener("click", () => adjustPlaybackTime(-10));
document.getElementById("open-mic").addEventListener("click", openMicrophone);
document.getElementById("close-mic").addEventListener("click", closeMicrophone);
document.getElementById("mic-volume-up").addEventListener("click", () => adjustVolume("mic_volume", 0.1));
document.getElementById("mic-volume-down").addEventListener("click", () => adjustVolume("mic_volume", -0.1));
document.getElementById("music-volume-up").addEventListener("click", () => adjustVolume("music_volume", 0.1));
document.getElementById("music-volume-down").addEventListener("click", () => adjustVolume("music_volume", -0.1));
