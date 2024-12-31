const control = {
    address: window.location.host,
    userId: -1,
    commandId: 0,
    ClientCommand: null,
    ClientQuery: null,
    UplinkMessage: null,
    DownlinkMessage: null,
    sio: null,

    // Function called when connected to the server
    _onConnect() {
        console.log('Connected to server.');
    },

    // Function called when disconnected from the server
    _onDisconnect() {
        console.log('Disconnected from server');
    },

    // Function to handle the reception of user ID
    _onReceiveUserId(data) {
        this.userId = data.user_id;
        console.log("user id", this.userId);
        const event = new CustomEvent('onSetUserId', {});
        window.dispatchEvent(event);
    },

    // Wait for the user ID to be set
    async _waitForUserId() {
        return new Promise((resolve) => {
            const handler = () => {
                window.removeEventListener('onSetUserId', handler);
                resolve(true);
            };
            window.addEventListener('onSetUserId', handler);
        });
    },

    // Function to handle the reception of downlink messages
    _onReceiveDownlinkMessage(data) {
        data = new Uint8Array(data);
        let downlinkMessage = this.DownlinkMessage.decode(data);
        downlinkMessage = this.DownlinkMessage.toObject(downlinkMessage);
        console.log("receive", downlinkMessage);
        if (downlinkMessage.error) {
            throw Error(downlinkMessage.error.error);
        }
        if (downlinkMessage.commandId) {
            this.commandId = downlinkMessage.commandId;
        }
        const event = new CustomEvent('onReceiveDownlinkMessage', {
            detail: { message: downlinkMessage }
        });
        window.dispatchEvent(event);
    },

    // Initialize the connection and set up event listeners
    async initConnection() {
        const root = await protobuf.load("static/message.proto");
        this.ClientCommand = root.lookupType("ClientCommand");
        this.ClientQuery = root.lookupType("ClientQuery");
        this.UplinkMessage = root.lookupType("UplinkMessage");
        this.DownlinkMessage = root.lookupType("DownlinkMessage");

        this.sio = io(this.address, {
            cors: {
                origin: this.address
            }
        });
        this.sio.on('user_id', this._onReceiveUserId.bind(this));
        this.sio.on('connect', this._onConnect.bind(this));
        this.sio.on('disconnect', this._onDisconnect.bind(this));
        this.sio.on('downlink_message', this._onReceiveDownlinkMessage.bind(this));
        await this._waitForUserId();
    },

    // Send an uplink message to the server
    _sendUplinkMessage(uplinkMessage) {
        uplinkMessage.userId = this.userId;
        let err = this.UplinkMessage.verify(uplinkMessage);
        if (err) {
            throw Error(err);
        }
        uplinkMessage = this.UplinkMessage.fromObject(uplinkMessage);
        console.log("send", this.UplinkMessage.toObject(uplinkMessage));
        let data = this.UplinkMessage.encode(uplinkMessage).finish();
        data = data.buffer.slice(data.byteOffset, data.byteOffset + data.byteLength); // socket.io only supports Uint8Array
        this.sio.emit('uplink_message', data);
    },

    // Send a command to the server
    sendCommand(command, args) {
        this._sendUplinkMessage({ userId: this.userId, clientCommand: { commandId: this.commandId + 1, [command]: args } });
    },

    // Send a query to the server
    sendQuery(command, args) {
        this._sendUplinkMessage({ userId: this.userId, clientQuery: { [command]: args } });
    }
};