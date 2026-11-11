"use strict";

async function measureAnimationFrameFPS(sampleTimeMs) {
    return new Promise(resolve => {
        let last;
        let frames = 0;
        let total = 0;

        function loop(timestamp) {
            if (last !== undefined) {
                total += timestamp - last;
                frames++;
            }

            last = timestamp;

            if (total >= sampleTimeMs) {
                const avgMs = total / frames;
                const fps = 1000 / avgMs;
                resolve(fps);
                return;
            }

            window.requestAnimationFrame(loop);
        }

        window.requestAnimationFrame(loop);
    });
}

class animationFrameCompute {
    constructor(cb, fps, timeUsagePct = 95) {
        this.cb = cb;
        this.frameMs = 1000 / fps;
        this.usagePct = timeUsagePct;
        this.running = false;
        this.animation_frame_id = null;
    }

    start() {
        if (!this.running) {
            this.running = true;
            this.#requestFrame();
        }
    }

    stop() {
        this.running = false;
        if (this.animation_frame_id != null) {
            cancelAnimationFrame(this.animation_frame_id);
            this.animation_frame_id = null;
        }
    }

    setFPS(fps) {
        this.frameMs = 1000 / fps;
    }

    setTimeUsagePct(timeUsagePct) {
        this.usagePct = timeUsagePct;
    }

    #runTimed() {
        const start = performance.now();
        this.cb();
        const duration = performance.now() - start;
        return duration;
    }

    #runForMs(ms) {
        const start = performance.now();
        while (true) {
            const rt = this.#runTimed();
            const elapsed = performance.now() - start;
            if (elapsed + rt > ms) {
                break;
            }
        }
    }

    #run() {
        const runDuration = (this.frameMs * (this.usagePct / 100));

        const start = performance.now();
        const DIVISIONS = 4;
        for (let i = 0; i < DIVISIONS; i++) {
            if(this.running) {
                this.#runForMs(runDuration / DIVISIONS);
            } else {
                return;
            }

            // abort if we are to running too long
            if (performance.now() - start > runDuration) {
                break;
            }
        }
        if (this.running) {
            this.#requestFrame();
        }
    }

    #requestFrame() {
        this.animation_frame_id = window.requestAnimationFrame(this.#run.bind(this));
    }
}
