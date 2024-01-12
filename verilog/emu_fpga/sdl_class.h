#pragma once
#include <SDL2/SDL.h>
#include <cstdbool>
#include <cstddef>
#include <cstdint>
#include <cstdlib>

static inline void put_pixel(SDL_Surface *surface, int x, int y, uint8_t r, uint8_t g, uint8_t b, uint8_t a) {
    uint32_t pixel = SDL_MapRGBA(surface->format, r, g, b, a);
    *((volatile uint32_t *)((uint8_t *)surface->pixels + y * surface->pitch + x * surface->format->BytesPerPixel)) = pixel;
}

static inline void put_pixel_bw(SDL_Surface *surface, int x, int y, bool set) {
    uint32_t pixel = set ? UINT32_MAX : 0;
    *((volatile uint32_t *)((uint8_t *)surface->pixels + y * surface->pitch + x * surface->format->BytesPerPixel)) = pixel;
}

class SDL {
public:
    SDL() {
        SDL_Init(SDL_INIT_VIDEO);
        sdlwin = SDL_CreateWindow("funnyarch", SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, width, height, 0);
    }

    bool update_events() {
        SDL_Event event;
        while (SDL_PollEvent(&event)) {
            if (event.type == SDL_QUIT) {
                return false;
            }
        }
        return true;
    }

    void full_redraw(void *buf, size_t buf_size) {
        SDL_Surface *surface = SDL_GetWindowSurface(sdlwin);
        for (size_t y = 0; y < height; y++) {
            for (size_t x = 0; x < width / 8; x++) {
                size_t idx = (y * (width / 8)) + x;
                if (idx >= buf_size) {
                    break;
                }
                uint8_t byte = ((uint8_t *)buf)[idx];
                for (int i = 0; i < 8; i++) {
                    put_pixel_bw(surface, (x * 8) + i, y, (byte & (1 << i)) != 0);
                }
            }
        }
        SDL_UpdateWindowSurface(sdlwin);
    }

    void redraw() {
        if (!dirty) {
            return;
        }
        dirty = false;

        SDL_UpdateWindowSurface(sdlwin);
    }

    void mem_write(uint32_t _address, uint32_t value) {
        uint64_t address = _address;
        unsigned int x = (address * 8) % width;
        unsigned int y = (address * 8) / width;
        dirty = true;

        SDL_Surface *surface = SDL_GetWindowSurface(sdlwin);
        for (int i = 0; i < 4; i++) {
            uint8_t byte = (value >> (i * 8)) & 0xFF;
            for (int j = 0; j < 8; j++) {
                put_pixel_bw(surface, x + (i * 8) + j, y, (byte & (1 << j)) != 0);
            }
        }
    }

private:
    SDL_Window *sdlwin;

    unsigned int width = 640;
    unsigned int height = 480;

    bool dirty = true;
};
