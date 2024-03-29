#pragma once

#ifdef SDLCLASS_USE_IMGUI
#include "imgui/imgui.h"
#include "imgui/imgui_impl_sdl2.h"
#include "imgui/imgui_impl_sdlrenderer2.h"
#endif
#include <SDL2/SDL.h>
#include <cstdbool>
#include <cstddef>
#include <cstdint>
#include <cstdlib>

#define SDLCLASS_ALIGN_UP(value, alignment)   (((value) + (alignment)-1) & ~((alignment)-1))
#define SDLCLASS_ALIGN_DOWN(value, alignment) ((value) & ~((alignment)-1))

static inline void put_pixel(SDL_Surface *surface, unsigned int x, unsigned int y, uint8_t r, uint8_t g, uint8_t b, uint8_t a) {
    uint32_t pixel = SDL_MapRGBA(surface->format, r, g, b, a);
    *((volatile uint32_t *)((uint8_t *)surface->pixels + y * surface->pitch + (x * surface->format->BytesPerPixel))) = pixel;
}

static inline void put_pixel_bw(SDL_Surface *surface, unsigned int x, unsigned int y, bool set) {
    uint32_t pixel = set ? UINT32_MAX : 0;
    *((volatile uint32_t *)((uint8_t *)surface->pixels + y * surface->pitch + (x * surface->format->BytesPerPixel))) = pixel;
}

class SDL {
public:
    SDL() {
        if (SDL_Init(SDL_INIT_VIDEO) != 0) {
            exit(1);
        }
        SDL_SetHint(SDL_HINT_VIDEO_X11_NET_WM_BYPASS_COMPOSITOR, "0");

        sdl_window =
            SDL_CreateWindow("funnyarch", SDL_WINDOWPOS_UNDEFINED, SDL_WINDOWPOS_UNDEFINED, width, height, SDL_WINDOW_RESIZABLE | SDL_WINDOW_SHOWN);

        sdl_renderer = SDL_CreateRenderer(sdl_window, -1, 0);
        if (sdl_renderer == nullptr) {
            SDL_Log("Error initializing renderer: %s", SDL_GetError());
        }
        SDL_RendererInfo info;
        SDL_GetRendererInfo(sdl_renderer, &info);
        SDL_SetHint(SDL_HINT_RENDER_SCALE_QUALITY, "linear");
        SDL_Log("Renderer: %s", info.name);

        SDL_SetRenderDrawColor(sdl_renderer, 54, 57, 62, 255);

        SDL_ShowWindow(sdl_window);

        sdl_fb_texture = SDL_CreateTexture(sdl_renderer, SDL_PIXELFORMAT_ARGB8888, SDL_TEXTUREACCESS_STREAMING, width, height);
        if (sdl_fb_texture == nullptr) {
            SDL_Log("Error creating texture: %s", SDL_GetError());
        }

#ifdef SDLCLASS_USE_IMGUI
        imgui_init();
#endif
    }

    void set_buf(void *buf, size_t buf_size) {
        _buf = buf;
        _buf_size = buf_size;

        sdl_fb_surface = SDL_CreateRGBSurfaceWithFormatFrom(_buf, width, height, 1, width / 8, SDL_PIXELFORMAT_INDEX1LSB);
        static SDL_Color colors[2] = {{0, 0, 0, 255}, {255, 255, 255, 255}};
        SDL_SetPaletteColors(sdl_fb_surface->format->palette, colors, 0, 2);
        if (sdl_fb_surface == nullptr) {
            SDL_Log("Error creating surface: %s", SDL_GetError());
        }
    }
#ifdef SDLCLASS_USE_IMGUI
    void set_imgui_render_func(void (*render)()) {
        _imgui_render = render;
    }
#endif

    bool update_events() {
        SDL_Event event;
        while (SDL_PollEvent(&event)) {
#ifdef SDLCLASS_USE_IMGUI
            imgui_process_event(&event);
#endif
            if ((event.type == SDL_QUIT) || (event.type == SDL_WINDOWEVENT && event.window.event == SDL_WINDOWEVENT_CLOSE &&
                                             event.window.windowID == SDL_GetWindowID(sdl_window))) {
                return false;
            }
        }
        return true;
    }

    void redraw() {
#ifdef SDLCLASS_USE_IMGUI
        imgui_start_render();
        imgui_render_ui();
        SDL_RenderClear(sdl_renderer);
#endif

        if (dirty) {
            SDL_DestroyTexture(sdl_fb_texture);
            sdl_fb_texture = SDL_CreateTextureFromSurface(sdl_renderer, sdl_fb_surface);

            dirty = false;
        }

        SDL_RenderCopy(sdl_renderer, sdl_fb_texture, nullptr, nullptr);

#ifdef SDLCLASS_USE_IMGUI
        imgui_end_render();
#endif
        SDL_RenderPresent(sdl_renderer);
        SDL_GL_SwapWindow(sdl_window);
    }

    void wait_frame_start() {
        next_frame_end = SDL_GetTicks64() + (1000 / 60);
    }

    uint64_t wait_for_next_frame() {
        uint64_t tnow = SDL_GetTicks64();
        uint64_t wait_time = 0;
        if (tnow < next_frame_end) {
            wait_time = next_frame_end - tnow;
            SDL_Delay(wait_time);
        }
        return wait_time;
    }

    inline bool mem_read(uint32_t _address, uint32_t *value) {
        return false;
    }

    inline void mem_write(uint32_t _address, uint32_t value) {
        if ((_address < 0xF0000000) || (_address >= (0xF0000000 + ((width * height) / 8)))) {
            return;
        }
        dirty = true;
    }

private:
    SDL_Window *sdl_window;
    SDL_Renderer *sdl_renderer;

    SDL_Texture *sdl_fb_texture;
    SDL_Surface *sdl_fb_surface;

    void *_buf = nullptr;
    size_t _buf_size = 0;

    void (*_imgui_render)() = nullptr;

    unsigned int width = 640;
    unsigned int height = 480;

    bool dirty = true;

    uint64_t next_frame_end = 0;

#ifdef SDLCLASS_USE_IMGUI
    void imgui_init() {
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
    }

    void imgui_render_ui() {
        if (_imgui_render != nullptr) {
            _imgui_render();
        }
    }

    void imgui_end_render() {
        ImGui::EndFrame();
        ImGui::Render();
        ImGui_ImplSDLRenderer2_RenderDrawData(ImGui::GetDrawData());
    }
#endif
};
