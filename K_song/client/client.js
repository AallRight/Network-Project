// * 系统设置
const SERVER_IP = "127.0.0.1";

// * 发送消息到服务器的函数
async function sendToServer(data) {
    await fetch(`http://${SERVER_IP}:9000/ice-candidate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });
}

// * 点击按钮时，创建 RTCPeerConnection 对象，获取音频流，发送 offer 到服务器
document.getElementById("start").addEventListener("click", async () => {
    try {
        // 获取音频流
        const stream = await navigator.mediaDevices.getUserMedia({
            audio: true
        });

        // 创建 RTCPeerConnection 对象
        const pc = new RTCPeerConnection();


        // 将音频流添加到 RTCPeerConnection 对象
        stream.getTracks().forEach(track => pc.addTrack(track, stream));

        // 处理 ICE 候选
        pc.onicecandidate = (event) => {
            if (event.candidate) {
                sendToServer({ candidate: event.candidate });
            }
        };

        // SDP offer
        const offer = await pc.createOffer();
        await pc.setLocalDescription(offer);

        const response = await fetch(`http://${SERVER_IP}:9000/offer`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ sdp: offer.sdp })
        });

        const answer = await response.json();
        await pc.setRemoteDescription(answer);

        console.log("Connected to server via WebRTC!");
    } catch (error) {
        console.error("Error during WebRTC setup:", error);
    }
});