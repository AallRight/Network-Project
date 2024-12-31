let mediaRecorder;
let audioStream;
let isRecording = false;

async function startMediaRecorder(sio) {
    if (!isRecording && navigator.mediaDevices && typeof MediaRecorder !== 'undefined') {
        try {
            const constraints = { audio: true, video: false };

            audioStream = await navigator.mediaDevices.getUserMedia(constraints);
            mediaRecorder = new MediaStreamRecorder(audioStream);
            mediaRecorder.mimeType = 'audio/pcm';
            mediaRecorder.audioChannels = 1;

            mediaRecorder.ondataavailable = (blob) => {
                sio.emit('media', blob);
            };

            mediaRecorder.start(5);
            isRecording = true;
        } catch (error) {
            console.error("Error accessing audio media: ", error);
        }
    } else {
        console.warn("MediaRecorder is not supported or already recording.");
    }
}

function stopMediaRecorder() {
    if (isRecording && mediaRecorder) {
        mediaRecorder.stop();
        audioStream.getTracks().forEach(track => track.stop());
        isRecording = false;
    } else {
        console.warn("No recording is in progress.");
    }
}