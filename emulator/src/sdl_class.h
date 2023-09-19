#pragma once

#include "imgui/imgui.h"
#include "imgui/imgui_impl_sdl2.h"
#include "imgui/imgui_impl_sdlrenderer2.h"
#include <SDL2/SDL.h>
#include <cstdbool>
#include <cstddef>
#include <cstdint>
#include <cstdlib>

#define SDLCLASS_ALIGN_UP(value, alignment)   (((value) + (alignment)-1) & ~((alignment)-1))
#define SDLCLASS_ALIGN_DOWN(value, alignment) ((value) & ~((alignment)-1))

static inline void put_pixel(SDL_Surface *surface, unsigned int x, unsigned int y, uint8_t r, uint8_t g, uint8_t b, uint8_t a) {
    uint32_t pixel = SDL_MapRGBA(surface->format, r, g, b, a);
    *((volatile uint32_t *)((uint8_t *)surface->pixels + y * surface->pitch + x * surface->format->BytesPerPixel)) = pixel;
}

static inline void put_pixel_bw(SDL_Surface *surface, unsigned int x, unsigned int y, bool set) {
    uint32_t pixel = set ? UINT32_MAX : 0;
    *((volatile uint32_t *)((uint8_t *)surface->pixels + y * surface->pitch + x * surface->format->BytesPerPixel)) = pixel;
}

class SDL {
public:
    SDL() {
        if (SDL_Init(SDL_INIT_VIDEO) != 0) {
            exit(1);
        }

        sdl_window = SDL_CreateWindow("funnyarch", SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, width, height, 0);

        sdl_renderer = SDL_CreateRenderer(sdl_window, -1, SDL_RENDERER_PRESENTVSYNC | SDL_RENDERER_ACCELERATED);
        SDL_RendererInfo info;
        SDL_GetRendererInfo(sdl_renderer, &info);
        SDL_SetHint(SDL_HINT_RENDER_SCALE_QUALITY, "linear");

        SDL_Log("Current SDL_Renderer: %s", info.name);

        sdl_fb_texture = SDL_CreateTexture(sdl_renderer, SDL_PIXELFORMAT_ARGB8888, SDL_TEXTUREACCESS_STREAMING, width, height);
        sdl_fb_surface = SDL_CreateRGBSurfaceFrom(NULL, width, height, 32, 0, 0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000);

        imgui_init();
    }

    void set_buf(void *buf, size_t buf_size) {
        _buf = buf;
        _buf_size = buf_size;
    }

    bool update_events() {
        SDL_Event event;
        while (SDL_PollEvent(&event)) {
            imgui_process_event(&event);
            if ((event.type == SDL_QUIT) || (event.type == SDL_WINDOWEVENT && event.window.event == SDL_WINDOWEVENT_CLOSE &&
                                             event.window.windowID == SDL_GetWindowID(sdl_window))) {
                return false;
            }
        }
        return true;
    }

    void redraw() {
        imgui_start_render();

        SDL_LockTexture(sdl_fb_texture, NULL, &sdl_fb_surface->pixels, &sdl_fb_surface->pitch);
        if (dirty) {
            for (size_t y = dirty_y1; y <= dirty_y2; y++) {
                for (size_t x = dirty_x1; x <= dirty_x2; x += 8) {
                    size_t idx = ((uint64_t)(y * width) + x) / 8;
                    if (idx >= _buf_size) {
                        goto cleanup;
                    }
                    uint8_t byte = ((uint8_t *)_buf)[idx];
                    for (unsigned int i = 0; i < 8; i++) {
                        unsigned int xpos = x + i;
                        unsigned int ypos = y + (xpos / width);
                        xpos %= width;
                        if (ypos >= height) {
                            goto cleanup;
                        }
                        put_pixel_bw(sdl_fb_surface, xpos, ypos, (byte & (1 << i)) != 0);
                    }
                }
            }
            dirty = false;
            reset_dirty_rectangle();
        }

    cleanup:
        SDL_Rect rect = {
            .x = 0,
            .y = 0,
            .w = width,
            .h = height,
        };

        SDL_UnlockTexture(sdl_fb_texture);
        SDL_RenderCopy(sdl_renderer, sdl_fb_texture, NULL, &rect);

        imgui_end_render();
    }

    inline uint32_t mem_read(uint32_t _address) {}

    inline void mem_write(uint32_t _address, uint32_t value) {
        if (_address < 0x3000) {
            return;
        }
        uint64_t address = _address - 0x3000;
        unsigned int y = (address * 8) / width;
        if (y >= height) {
            return;
        }
        unsigned int x = (address * 8) % width;
        dirty = true;
        update_dirty_rectangle(x, y);
    }

    void imgui_init() {
        // Setup Dear ImGui context
        IMGUI_CHECKVERSION();
        ImGui::CreateContext();
        ImGui_ImplSDL2_InitForSDLRenderer(sdl_window, sdl_renderer);
        ImGui_ImplSDLRenderer2_Init(sdl_renderer);
    }

    void imgui_process_event(SDL_Event *event) {
        ImGui_ImplSDL2_ProcessEvent(event);
    }

    void imgui_start_render() {
        ImGui_ImplSDLRenderer2_NewFrame();
        ImGui_ImplSDL2_NewFrame();
        ImGui::NewFrame();

        bool show_demo_window = true;
        ImGui::ShowDemoWindow(&show_demo_window);
        ImGui::Begin("Hello, world!"); // Create a window called "Hello, world!" and append into it.

        ImGui::Text("This is some useful text.");
        ImGui::End();
    }

    void imgui_end_render() {
        ImGui::EndFrame();
        ImGui::Render();
        ImGui_ImplSDLRenderer2_RenderDrawData(ImGui::GetDrawData());

        SDL_RenderPresent(sdl_renderer); // TODO: move
    }

private:
    SDL_Window *sdl_window;
    SDL_Renderer *sdl_renderer;

    SDL_Texture *sdl_fb_texture;
    SDL_Surface *sdl_fb_surface;

    unsigned int width = 640;
    unsigned int height = 480;

    bool dirty = true;
    unsigned int dirty_x1 = width - 1;
    unsigned int dirty_y1 = height - 1;
    unsigned int dirty_x2 = 0;
    unsigned int dirty_y2 = 0;

    void reset_dirty_rectangle() {
        dirty_x1 = width - 1;
        dirty_y1 = height - 1;
        dirty_x2 = 0;
        dirty_y2 = 0;
    }

    void update_dirty_rectangle(unsigned int x, unsigned int y) {
        x = SDLCLASS_ALIGN_UP(x, 8);
        if (x >= width) {
            x = width - 1;
        }

        if (x < dirty_x1) {
            dirty_x1 = x;
        }
        if (x > dirty_x2) {
            dirty_x2 = x;
        }

        if (y < dirty_y1) {
            dirty_y1 = y;
        }
        if (y > dirty_y2) {
            dirty_y2 = y;
        }
    }

    void *_buf = nullptr;
    size_t _buf_size = 0;
};
