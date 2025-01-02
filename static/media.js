const media = {
    audioServerURL: "http://127.0.0.1:5000",

    peerConnection: null, // RTCPeerConnection instance
    localStream: null, // Local audio stream
    connectionId: null, // Connection ID returned by the server

    // Utility function: Send data to the RTC server
    async _sendToRTC(endpoint, data) {
        const url = `${this.audioServerURL}/${endpoint}`;
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
    },

    async startRecording() {
        try {
            // Get the local audio stream
            this.localStream = await navigator.mediaDevices.getUserMedia({ audio: true });

            // Initialize RTCPeerConnection
            this.peerConnection = new RTCPeerConnection();
            this.localStream.getTracks().forEach(track => this.peerConnection.addTrack(track, this.localStream));
            this._configureSenderParameters(this.peerConnection);

            // Create Offer and send to the server
            const offer = await this.peerConnection.createOffer();
            await this.peerConnection.setLocalDescription(offer);

            const response = await this._sendToRTC("offer", { sdp: offer.sdp });
            this.connectionId = response.connection_id;
            console.log("Offer created and sent to server!");

            // Set the Answer returned by the server
            await this.peerConnection.setRemoteDescription({
                type: response.type,
                sdp: response.sdp,
            });

            // Handle ICE candidates
            this.peerConnection.onicecandidate = async event => {
                if (event.candidate) {
                    await this._sendToRTC(`ice-candidate/${this.connectionId}`, { candidate: event.candidate });
                }
            };

            console.log("Recording started and connected to server!");
        } catch (error) {
            console.error("Error during setup:", error);
        }
    },

    async stopRecording() {
        try {
            if (this.localStream) this.localStream.getTracks().forEach(track => track.stop());
            if (this.connectionId) await this._sendToRTC(`close/${this.connectionId}`, {});
            if (this.peerConnection) this.peerConnection.close();

            this.peerConnection = null;
            this.localStream = null;
            this.connectionId = null;

            console.log("Recording stopped and connection closed!");
            return true;
        } catch (error) {
            console.error("Error during cleanup:", error);
            return false;
        }
    },

    // Configure sender parameters (optimize latency and audio quality)
    _configureSenderParameters(pc) {
        const audioSender = pc.getSenders().find(sender => sender.track && sender.track.kind === "audio");
        if (audioSender) {
            const params = audioSender.getParameters();
            if (!params.encodings) params.encodings = [{}];
            params.encodings[0].ptime = 10; // Set frame time to 10ms
            params.encodings[0].maxBitrate = 32000; // Set max bitrate to 32kbps
            audioSender.setParameters(params);
        }
    }
};