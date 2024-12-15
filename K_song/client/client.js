const SERVER_IP = "127.0.0.1"; // 替换为服务器地址
let pc = null; // PeerConnection 实例
let stream = null; // 本地音频流
let connectionId = null; // 保存服务器返回的 connection_id

// 向服务器发送消息
async function sendToServer(endpoint, data) {
    const url = `http://${SERVER_IP}:9000/${endpoint}`;
    const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
    });
    if (!response.ok) {
        console.error("Error sending data to server:", response.statusText);
    }
    return response.json();
}

// 调整发送器的参数（可选，用于优化延时和音质）
function adjustSenderParameters(pc) {
    const audioSender = pc.getSenders().find(sender => sender.track && sender.track.kind === 'audio');
    if (audioSender) {
        const params = audioSender.getParameters();
        if (!params.encodings) params.encodings = [{}];
        params.encodings[0].ptime = 10; // 设置帧时间为 10ms
        params.encodings[0].maxBitrate = 32000; // 最大比特率 32kbps
        audioSender.setParameters(params);
    }
}

// 点击连接音频按钮
document.getElementById("connect").addEventListener("click", async () => {
    try {
        // 获取本地音频流
        stream = await navigator.mediaDevices.getUserMedia({ audio: true });

        // 创建 RTCPeerConnection 实例
        pc = new RTCPeerConnection();

        // 将音频轨道添加到 RTCPeerConnection
        stream.getTracks().forEach(track => pc.addTrack(track, stream));

        // 调整发送器参数
        adjustSenderParameters(pc);

        // 创建 SDP Offer 并发送到服务器
        const offer = await pc.createOffer();
        let sdp = offer.sdp;
        await pc.setLocalDescription(offer);

        const response = await sendToServer("offer", { sdp: sdp });

        // 保存服务器返回的 connection_id
        connectionId = response.connection_id;
        console.log("Connection ID:", connectionId);

        // 处理 ICE 候选
        pc.onicecandidate = async (event) => {
            if (event.candidate) {
                await sendToServer(`ice-candidate/${connectionId}`, { candidate: event.candidate });
            }
        };

        // 设置服务器返回的 SDP Answer
        await pc.setRemoteDescription({
            type: response.type,
            sdp: response.sdp,
        });

        console.log("Recording started and connected to server!");

        // 启用结束按钮
        document.getElementById("connect").disabled = true;
        document.getElementById("disconnect").disabled = false;

    } catch (error) {
        console.error("Error during setup:", error);
    }
});

// 点击断开音频按钮
document.getElementById("disconnect").addEventListener("click", async () => {
    try {
        // 停止音频轨道
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
        }

        // 通知服务器关闭连接
        if (connectionId) {
            await sendToServer(`close/${connectionId}`, {});
            console.log("Connection closed on server.");
        }

        // 关闭 PeerConnection
        if (pc) {
            pc.close();
            pc = null;
        }

        console.log("Recording stopped and connection closed!");

        // 重置按钮状态
        document.getElementById("connect").disabled = false;
        document.getElementById("disconnect").disabled = true;

    } catch (error) {
        console.error("Error during cleanup:", error);
    }
});

// 点击播放歌曲音频按钮
document.getElementById("play").addEventListener("click", async () => {
    try {
        await sendToServer("play_local", {});

        // 重置按钮状态
        document.getElementById("pause").disabled = false;
        document.getElementById("play").disabled = true;
        document.getElementById("forward").disabled = false;
        document.getElementById("backward").disabled = false;
    } catch (error) {
        console.error("Error playing song:", error);
    }
});

// 点击暂停歌曲音频按钮
document.getElementById("pause").addEventListener("click", async () => {
    try {
        await sendToServer("pause_local", {});

        // 重置按钮状态
        document.getElementById("play").disabled = false;
        document.getElementById("pause").disabled = true;
        document.getElementById("forward").disabled = true;
        document.getElementById("backward").disabled = true;
    } catch (error) {
        console.error("Error pausing song:", error);
    }
});

// 点击快进歌曲音频按钮
document.getElementById("forward").addEventListener("click", async () => {
    try {
        const time = 10;
        await sendToServer('adjust_time', { time: time });
    } catch (error) {
        console.error("Error forwarding song:", error);
    }
});

// 点击快退歌曲音频按钮
document.getElementById("backward").addEventListener("click", async () => {
    try {
        const time = -10;
        await sendToServer('adjust_time', { time: time });
    } catch (error) {
        console.error("Error backwarding song:", error);
    }
});

// 点击打开麦克风按钮
document.getElementById("open_mic").addEventListener("click", async () => {
    try {
        await sendToServer("open_mic", {});

        // 重置按钮状态
        document.getElementById("open_mic").disabled = true;
        document.getElementById("close_mic").disabled = false;
    } catch (error) {
        console.error("Error opening mic:", error);
    }
});

// 点击关闭麦克风按钮
document.getElementById("close_mic").addEventListener("click", async () => {
    try {
        await sendToServer("close_mic", {});

        // 重置按钮状态
        document.getElementById("open_mic").disabled = false;
        document.getElementById("close_mic").disabled = true;
    } catch (error) {
        console.error("Error closing mic:", error);
    }
});

// 点击提高麦克风音量按钮
document.getElementById("mic_volume_up").addEventListener("click", async () => {
    try {
        await sendToServer("mic_volume", { volume: 0.1 });
    } catch (error) {
        console.error("Error increasing volume:", error);
    }
});

// 点击降低麦克风音量按钮
document.getElementById("mic_volume_down").addEventListener("click", async () => {
    try {
        await sendToServer("mic_volume", { volume: -0.1 });
    } catch (error) {
        console.error("Error decreasing volume:", error);
    }
});

// 点击提高音乐音量按钮
document.getElementById("music_volume_up").addEventListener("click", async () => {
    try {
        await sendToServer("music_volume", { volume: 0.1 });
    } catch (error) {
        console.error("Error increasing volume:", error);
    }
});

// 点击降低音乐音量按钮
document.getElementById("music_volume_down").addEventListener("click", async () => {
    try {
        await sendToServer("music_volume", { volume: -0.1 });
    } catch (error) {
        console.error("Error decreasing volume:", error);
    }
});