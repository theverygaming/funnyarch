"use strict";

class funnyarchHDD {
    constructor(dataArray) {
        if (!(dataArray instanceof Uint8Array)) {
            throw new Error("Invalid HDD dataArray type");
        }
        if ((dataArray.length % 512) != 0) {
            throw new Error("HDD size must be divisible by 512");
        }
        
        this.dataArray = dataArray;

        // state
        this.command = 0; // 0 = none, 1 = read, 2 = write
        this.finished = false;
        this.sector_idx = 0;
        this.numsectors = dataArray.length / 512;
        this.databuf = new Uint8Array(512);
    }

    readMMIO(address) {
        // HDD control/status register
        if (address == 0xF004B004) {
            return (this.command & 0b11) | (this.finished ? 0b100 : 0) | ((this.sector_idx & 0x1FFFFFFF) << 3);
        }
        // HDD info register
        if (address == 0xF004B008) {
            return this.numsectors & 0x1FFFFFFF;
        }
        // HDD controller control/status register
        if (address == 0xF004B00C) {
            return 0;
        }
        // HDD data buffer
        if (address >= 0xF004B010 && address < 0xF004B210) {
            let offset = address - 0xF004B010;
            offset -= offset % 4; // align
            return this.databuf[offset] | (this.databuf[offset + 1] << 8) | (this.databuf[offset + 2] << 16) | (this.databuf[offset + 3] << 24);
        }
        return null;
    }

    writeMMIO(address, data) {
        // HDD control/status register
        if (address == 0xF004B004) {
            let new_cmd = data & 0b11;
            if (new_cmd > 3) {
                new_cmd = 0;
            }
            const new_sector_idx = (data >> 3) & 0x1FFFFFFF;
            this.command = new_cmd;
            this.finished = false;
            this.sector_idx = new_sector_idx;
            
            const boffs = this.sector_idx * 512;
            switch (this.command) {
            case 1:
                this.databuf.set(this.dataArray.subarray(boffs, boffs + 512), 0);
                break;
            case 2:
                this.dataArray.set(this.databuf, boffs);
                break;
            }
            this.finished = true;
        }
        // HDD data buffer
        if (address >= 0xF004B010 && address < 0xF004B210) {
            let offset = address - 0xF004B010;
            offset -= offset % 4; // align
            if (this.command == 0 || this.finished) {
                databuf[offset] = data & 0xFF;
                databuf[offset + 1] = (data >> 8) & 0xFF;
                databuf[offset + 2] = (data >> 16) & 0xFF;
                databuf[offset + 3] = (data >> 24) & 0xFF;
            }
        }
    }
}

class funnyarchComputer {
    constructor(romArray, ramArray, serialOut = null, screenCanvas = null, hddDataArray = null) {
        if (!(romArray instanceof Uint8Array)) {
            throw new Error("Invalid romArray type");
        }
        if (!(ramArray instanceof Uint8Array)) {
            throw new Error("Invalid ramArray type");
        }
        if (romArray.length != 8192) {
            throw new Error("Invalid romArray size");
        }

        this.memoryArrays = []
        this.memoryArrays.push({ "arr": romArray, "baseAddr": 0x00, "readonly": true });
        this.memoryArrays.push({ "arr": ramArray, "baseAddr": 0x2000, "readonly": false });
        this.serialOut = serialOut;
        this.screenCanvas = screenCanvas;

        if (this.screenCanvas !== null) {
            this.screenCanvas.getContext("2d").fillStyle = 'black';
            this.screenCanvas.getContext("2d").fillRect(0, 0, this.screenCanvas.width, this.screenCanvas.height);
            this.memoryArrays.push({ "arr": new Uint8Array((640 * 480) / 8), "baseAddr": 0xF0000000, "readonly": false });
        }

        this.serialInBuf = [];

        this.cpu = new funnyarchCPU(this.#readMem.bind(this), this.#writeMem.bind(this));

        this.hdd = new funnyarchHDD(hddDataArray ? hddDataArray : new Uint8Array(512));
    }

    run(ninstrs) {
        const start = performance.now();
        this.cpu.execute(ninstrs);
        const end = performance.now();
        const mips = (ninstrs / 1000000) / ((end - start) / 1000);
        return mips;
    }

    serialIn(str) {
        for (let i = 0; i < str.length; i++) {
            this.serialInBuf.push(str.charAt(i));
        }
    }

    #readMem(address) {
        // Serial data register
        if (address == 0xF004B000) {
            if (this.serialInBuf.length == 0) {
                return 0;
            }
            return (1 << 8) | this.serialInBuf.shift().charCodeAt(0);
        }
        const hddmmio = this.hdd.readMMIO(address);
        if (hddmmio !== null) {
            return hddmmio;
        }

        for (let i = 0; i < this.memoryArrays.length; i++) {
            let marr = this.memoryArrays[i];
            if (address >= marr.baseAddr && ((address - marr.baseAddr) + 3) <= marr.arr.length) {
                return this.#readMemArray(marr.arr, address - marr.baseAddr);
            }
        }
        return Math.floor((Math.random() * 4294967296));
    }

    #writeMem(address, data) {
        if (address == 0xF004B000) {
            if (this.serialOut !== null) {
                this.serialOut(String.fromCharCode(data & 0xFF));
            }
        }
        this.hdd.writeMMIO(address, data);
        for (let i = 0; i < this.memoryArrays.length; i++) {
            let marr = this.memoryArrays[i];
            if (marr.readonly) {
                continue;
            }
            if (address >= marr.baseAddr && ((address - marr.baseAddr) + 3) <= marr.arr.length) {
                this.#writeMemArray(this.memoryArrays[i].arr, address - marr.baseAddr, data);
            }
        }

        if (this.screenCanvas !== null && address >= 0xF0000000 && ((address - 0xF0000000) + 3) <= ((640 * 480) / 8)) {
            const x = ((address - 0xF0000000) % (640 / 8)) * 8;
            const y = Math.floor((address - 0xF0000000) / (640 / 8));
            for (let i = 0; i < 32; i++) {
                if ((data & (1 << i)) != 0) {
                    this.screenCanvas.getContext("2d").fillStyle = 'white';
                } else {
                    this.screenCanvas.getContext("2d").fillStyle = 'black';
                }
                this.screenCanvas.getContext("2d").fillRect(x + i, y, 1, 1);
            }
        }
    }

    #readMemArray(array, address) {
        if (address >= 0 && (address + 3) < array.length) {
            return ((array[address + 0] << 0) | (array[address + 1] << 8) | (array[address + 2] << 16) | (array[address + 3] << 24)) >>> 0;
        }
        throw new Error("readMemArray invalid address");
    }

    #writeMemArray(array, address, data) {
        if (address >= 0 && (address + 3) < array.length) {
            array[address + 0] = (data >>> 0) & 0xFF;
            array[address + 1] = (data >>> 8) & 0xFF;
            array[address + 2] = (data >>> 16) & 0xFF;
            array[address + 3] = (data >>> 24) & 0xFF;
        } else {
            throw new Error("writeMemArray invalid address");
        }
    }
}
