const address = "127.0.0.1:5001";
let userId = -1;
let commandId = 0;
let ClientCommand;
let ClientQuery;
let UplinkMessage;
let DownlinkMessage;

let sio;

function onConnect() {
    console.log('Connected to server.');
}

function onReceiveUserId(data) {
    userId = data.user_id;
    console.log("user id", userId);
    const event = new CustomEvent('onReceiveUserId', {});
    window.dispatchEvent(event);
}

async function waitForUserId() {
    return new Promise((resolve) => {
        const handleReceiveUserId = () => {
            window.removeEventListener('onReceiveUserId', handleReceiveUserId);
            resolve(true);
        };
        window.addEventListener('onReceiveUserId', handleReceiveUserId);
    });
}

function onDisconnect() {
    console.log('Disconnected from server');
}

function onReceiveDownlinkMessage(data) {
    data = new Uint8Array(data);
    let downlinkMessage = DownlinkMessage.decode(data);
    downlinkMessage = DownlinkMessage.toObject(downlinkMessage);
    console.log("receive", downlinkMessage);
    if (downlinkMessage.error)
        throw Error(downlinkMessage.error.error);
    if (downlinkMessage.commandId)
        commandId = downlinkMessage.commandId;
    const event = new CustomEvent('onReceiveDownlinkMessage', {
        detail: { message: downlinkMessage }
    });
    window.dispatchEvent(event);
}

async function init() {
    root = await protobuf.load("static/message.proto");
    ClientCommand = root.lookupType("ClientCommand");
    ClientQuery = root.lookupType("ClientQuery");
    UplinkMessage = root.lookupType("UplinkMessage");
    DownlinkMessage = root.lookupType("DownlinkMessage");
    sio = io(address, {
        cors: {
            origin: address
        }
    });
    sio.on('user_id', onReceiveUserId);
    sio.on('connect', onConnect);
    sio.on('disconnect', onDisconnect);
    sio.on('downlink_message', onReceiveDownlinkMessage);
}

function sendUplinkMessage(uplinkMessage) {
    uplinkMessage.userId = userId;
    let err = UplinkMessage.verify(uplinkMessage);
    if (err)
        throw Error(err);
    uplinkMessage = UplinkMessage.fromObject(uplinkMessage);
    console.log("send", UplinkMessage.toObject(uplinkMessage));
    let data = UplinkMessage.encode(uplinkMessage).finish();
    data = data.buffer.slice(data.byteOffset, data.byteOffset + data.byteLength);
    sio.emit('uplink_message', data);
}

function sendCommand(command, args) {
    sendUplinkMessage({ userId, clientCommand: { commandId: commandId + 1, [command]: args } });
}

function sendQuery(command, args) {
    sendUplinkMessage({ userId, clientQuery: { [command]: args } });
}