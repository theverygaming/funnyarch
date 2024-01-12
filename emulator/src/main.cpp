#include <algorithm>
#include <cassert>
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <fstream>

#ifdef __EMSCRIPTEN__
#include <emscripten.h>
#include <emscripten/html5.h>
#endif

#include "cpu.h"
#include "mem.h"

#define GRAPHICS

#ifdef GRAPHICS
#define SDLCLASS_USE_IMGUI
#include "sdl_class.h"
#endif

template <typename T, size_t size> class buf {
public:
    bool add_val(T val) {
        if (!minmax_init) {
            minmax_init = true;
            min = val;
            max = val;
        }
        if (val < min) {
            min = val;
        }
        if (val > max) {
            max = val;
        }

        arr[offset++] = val;
        if (offset >= size) {
            offset = 0;
            return true;
        }
        return false;
    }

    T *get_arr() {
        return arr;
    }

    T get_avg() {
        T val = 0;
        for (size_t i = 0; i < size; i++) {
            val += arr[i];
        }
        val /= (float)size;
        return val;
    }

    size_t get_size() {
        return size;
    }

    size_t get_offset() {
        return offset;
    }

    T get_alltime_min() {
        return min;
    }

    T get_alltime_max() {
        return max;
    }

private:
    size_t offset = 0;
    T arr[size];

    bool minmax_init = false;
    T min, max;
};

#ifdef GRAPHICS
static buf<size_t, 10> wait_time_buf;
#endif

static struct cpu::ctx cpu_ctx;

#ifdef SDLCLASS_USE_IMGUI
static bool debugger_enabled = false;
static bool debugger_step = true;
static uint64_t debugger_step_instr_count = 0;

static buf<float, 100> cpu_usage_buf;
static buf<float, 100> mips_buf;
static buf<float, 100> fps_buf;

void imgui_debug_window() {
    ImGui::Begin("Options & Statistics");
    if (ImGui::CollapsingHeader("Graphs")) {
        char buf[100];
        snprintf(buf, sizeof(buf), "average: %0.2f%%", cpu_usage_buf.get_avg());
        ImGui::PlotLines("CPU usage", cpu_usage_buf.get_arr(), cpu_usage_buf.get_size(), cpu_usage_buf.get_offset(), buf, 0, 100, ImVec2(0, 80.0f));
        snprintf(buf, sizeof(buf), "average: %0.2f", mips_buf.get_avg());
        ImGui::PlotLines(
            "MIPS", mips_buf.get_arr(), mips_buf.get_size(), mips_buf.get_offset(), buf, 0, mips_buf.get_alltime_max(), ImVec2(0, 80.0f));
        snprintf(buf, sizeof(buf), "average: %0.2f", fps_buf.get_avg());
        ImGui::PlotLines("FPS", fps_buf.get_arr(), fps_buf.get_size(), fps_buf.get_offset(), buf, 0, fps_buf.get_alltime_max(), ImVec2(0, 80.0f));
        ImGui::Text("average wait time: %zums", wait_time_buf.get_avg());
    }

    if (ImGui::CollapsingHeader("Registers")) {
        ImGui::Text("Registers: ");
        for (int i = 0; i < 32; i++) {
            ImGui::BulletText("%s: 0x%x\n", cpudesc::regnames[i], cpu_ctx.regs[i]);
        }
    }

    if (ImGui::CollapsingHeader("Options")) {
        ImGui::Checkbox("Debugger", &debugger_enabled);
        if (ImGui::Button("CPU reset")) {
            cpu::reset(&cpu_ctx);
        }
    }

    ImGui::End();

    if (!debugger_enabled) {
        return;
    }

    static int debugger_step_instr_count_add = 1;
    ImGui::Begin("Debugger", &debugger_enabled);
    ImGui::Checkbox("Single step", &debugger_step);
    if (debugger_step) {
        if (ImGui::InputInt("instructions per step", &debugger_step_instr_count_add)) {
            debugger_step_instr_count_add = std::clamp(debugger_step_instr_count_add, 1, 1000000);
        }
        if (ImGui::Button("step")) {
            debugger_step_instr_count += debugger_step_instr_count_add;
        }
    }
    ImGui::End();
}
#endif

#ifdef GRAPHICS
static SDL sdl_ctx;
#endif

uint32_t mem_read(uint32_t addr) {
    return mem::read<uint32_t>(addr);
}

void mem_write(uint32_t addr, uint32_t data) {
    mem::write<uint32_t>(addr, data);
#ifdef GRAPHICS
    sdl_ctx.mem_write(addr, data);
#endif
}

void init_emu() {
    mem::init();
    cpu::init(&cpu_ctx);
    cpu_ctx.mem_read_ptr = &mem_read;
    cpu_ctx.mem_write_ptr = &mem_write;
}

uint64_t run_emu(uint64_t instrs) {
    uint64_t cycles = cpu::execute(&cpu_ctx, instrs);
    return cycles;
}

static bool running = true;

static inline void main_loop() {
    static std::chrono::time_point<std::chrono::high_resolution_clock> frame_tm = std::chrono::high_resolution_clock::now();

#ifdef __EMSCRIPTEN__
    if (!running) {
        emscripten_cancel_main_loop();
    }
#endif

    static uint64_t instr_count = 3000000;

#ifdef GRAPHICS
    sdl_ctx.wait_frame_start();
#endif

    uint64_t clock_cycles;

#ifdef SDLCLASS_USE_IMGUI
    if (debugger_enabled && debugger_step) {
        if (debugger_step_instr_count > 0) {
            clock_cycles = run_emu(debugger_step_instr_count);
            debugger_step_instr_count = 0;
        }
    } else {
#endif
        clock_cycles = run_emu(instr_count);
#ifdef SDLCLASS_USE_IMGUI
    }
#endif

#ifdef SDLCLASS_USE_IMGUI
    if (!debugger_enabled) {
        double cycles_min = ((double)instr_count * 3);
        double cycles_max = ((double)instr_count * 5);
        double usage = (((double)clock_cycles - cycles_min) / (cycles_max - cycles_min)) * 100;
        cpu_usage_buf.add_val(usage);
    }
#endif

#ifdef GRAPHICS
    if (!sdl_ctx.update_events()) {
        running = false;
        return;
    }
    sdl_ctx.redraw();
    if (!debugger_enabled) {
        cpu::hwinterrupt(&cpu_ctx, 0);
    }

#ifdef SDLCLASS_USE_IMGUI
    auto tnow = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> frametime = std::chrono::duration_cast<std::chrono::duration<double>>(tnow - frame_tm);
    frame_tm = tnow;
    if (!debugger_enabled) {
        fps_buf.add_val(1.0f / frametime.count());
        mips_buf.add_val((1.0f / (frametime.count() / instr_count)) / 1000000);
    }
#endif

    uint64_t waited = sdl_ctx.wait_for_next_frame();

#ifdef SDLCLASS_USE_IMGUI
    if (wait_time_buf.add_val(waited) && !debugger_enabled) {
#else
    if (wait_time_buf.add_val(waited)) {
#endif
        uint64_t scale = instr_count / 2;
        scale = scale == 0 ? 1 : scale;
        if (wait_time_buf.get_avg() >= 2) {
            instr_count += scale;
        } else if ((instr_count > scale) && (wait_time_buf.get_avg() < 1)) {
            instr_count -= scale;
        }
    }
#endif
}

int main(int, char *[]) {
    init_emu();
#ifdef SDLCLASS_USE_IMGUI
    sdl_ctx.set_imgui_render_func(&imgui_debug_window);
    sdl_ctx.set_buf(mem::mem_fb, FB_BYTES);
#endif

    std::ifstream input("output.bin", std::ios::binary);
    if (!input.good()) {
        fprintf(stderr, "failed to read output.bin\n");
        return 1;
    }
    input.read((char *)&mem::mem_rom[0], ROM_BYTES);
    input.close();

#ifdef __EMSCRIPTEN__
    emscripten_set_main_loop(main_loop, 0, 1);
#else
    while (running) {
        main_loop();
    }
#endif

    return 0;
}
