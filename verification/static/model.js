class Model {
    constructor(curVersion = 1) {
        this.curVersion = curVersion; // current version
        this.data = []; // data array
        this.pendingChanges = {}; // pending changes object
    }

    manipulate(change, basedOnVersion) {
        const appliedChanges = {};

        if (basedOnVersion === this.curVersion) {
            const applied = this._apply(change);
            if (applied) {
                Object.assign(appliedChanges, this._updateVersion());
                appliedChanges[basedOnVersion] = change;
            }
        } else if (basedOnVersion > this.curVersion) {
            if (!(basedOnVersion in this.pendingChanges)) {
                this.pendingChanges[basedOnVersion] = change;
            }
            // else discard this change
        } 
        // else discard this change

        return Object.fromEntries(Object.entries(appliedChanges).sort());
    }

    _apply(change) {
        const parts = change.split(" ");
        if (parts[0] === "push") {
            if (parts.length !== 2) return false;
            const value = parseInt(parts[1], 10);
            if (!isNaN(value)) {
                this.data.push(value);
                return true;
            }
        } else if (parts[0] === "pop") {
            if (parts.length !== 1) return false;
            if (this.data.length === 0) return true;
            this.data.pop();
            return true;
        }
        return false;
    }

    _updateVersion() {
        const appliedChanges = {};

        this.curVersion++;
        if (this.curVersion in this.pendingChanges) {
            const change = this.pendingChanges[this.curVersion];
            const basedOnVersion = this.curVersion;
            delete this.pendingChanges[this.curVersion];

            const applied = this._apply(change);
            if (applied) {
                Object.assign(appliedChanges, this._updateVersion());
                appliedChanges[basedOnVersion] = change;
            }
        }
        return appliedChanges;
    }

    serialize() {
        return JSON.stringify({
            cur_version: this.curVersion,
            data: this.data
        });
    }

    static deserialize(jsonStr) {
        try {
            const dataDict = JSON.parse(jsonStr);
            const curVersion = dataDict.cur_version;
            const data = dataDict.data;

            if (typeof curVersion !== 'number') {
                throw new Error("cur_version must be an integer.");
            }
            if (!Array.isArray(data)) {
                throw new Error("data must be a list.");
            }

            const dbInstance = new Model(curVersion);
            dbInstance.data = data;
            return dbInstance;

        } catch (error) {
            console.error("Error:", error.message);
        }
        return new Model(); // return an empty model instance
    }

    getCurVersion() {
        return this.curVersion;
    }

    getNumPendingChanges() {
        return Object.keys(this.pendingChanges).length;
    }
}

// Example usage
const db_test = new Model(1);

function logManipulate(change, basedOnVersion) {
    const appliedChanges = db_test.manipulate(change, basedOnVersion);
    console.log(`applied:`, appliedChanges);
    console.log(`db =`, db_test.serialize());
    console.log();
}

logManipulate("push 9", 1);
logManipulate("push 8", 2);
logManipulate("push 7", 5); // pending
logManipulate("push 6", 4); // pending
logManipulate("push 5", 3);
logManipulate("push 4", 5); // won't take effect
logManipulate("wrong 3", 6); // won't take effect
logManipulate("wrong 2", 7); // pending, won't take effect
logManipulate("pop", 6);