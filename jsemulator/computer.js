"use strict";

class funnyarchComputer {
    constructor(romArray, ramArray, serialOut = null, screenCanvas = null) {
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
        if (address == 0xF004B000) {
            if (this.serialInBuf.length == 0) {
                return 0;
            }
            return (1 << 9) | this.serialInBuf.shift().charCodeAt(0);
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
