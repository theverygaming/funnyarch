#pragma once

#include <SDL2/SDL.h>
#include <cstdbool>
#include <cstddef>
#include <cstdint>
#include <cstdlib>

static inline void put_pixel(SDL_Surface *surface, int x, int y, uint8_t r, uint8_t g, uint8_t b, uint8_t a) {
    uint32_t pixel = SDL_MapRGBA(surface->format, r, g, b, a);
    *((uint32_t *)((uint8_t *)surface->pixels + y * surface->pitch + x * surface->format->BytesPerPixel)) = pixel;
}

static inline void put_pixel_bw(SDL_Surface *surface, int x, int y, bool set) {
    uint32_t pixel = set ? UINT32_MAX : 0;
    *((uint32_t *)((uint8_t *)surface->pixels + y * surface->pitch + x * surface->format->BytesPerPixel)) = pixel;
}

class SDL {
public:
    SDL() {
        SDL_Init(SDL_INIT_VIDEO);
        sdlwin = SDL_CreateWindow("balls", SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, width, height, 0);
        surface = SDL_GetWindowSurface(sdlwin);
    }

    bool update() {
        SDL_Event event;
        while (SDL_PollEvent(&event)) {
            if (event.type == SDL_QUIT) {
                return false;
            }
        }

        SDL_UpdateWindowSurface(sdlwin);
        return true;
    }

    void redraw(void *buf, size_t buf_size) {
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
    }

private:
    SDL_Window *sdlwin;
    SDL_Surface *surface;

    unsigned width = 640;
    unsigned height = 480;
};
