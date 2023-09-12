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

class SDL {
public:
    SDL() {
        SDL_Init(SDL_INIT_VIDEO);
        sdlwin = SDL_CreateWindow("balls", SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, width, height, 0);
        surface = SDL_GetWindowSurface(sdlwin);
    }

    void update() {
        SDL_Event event;
        while (SDL_PollEvent(&event)) {
            if (event.type == SDL_QUIT) {
                exit(0);
            }
        }

        SDL_UpdateWindowSurface(sdlwin);
    }

    void redraw(void *buf, size_t buf_size) {
        for (size_t y = 0; y < height; y++) {
            for (size_t x = 0; x < width; x++) {
                size_t bit = (y * width) + x;
                size_t byte = bit / 8;
                size_t byte_off = bit % 8;
                if (byte >= buf_size) {
                    break;
                }
                if ((((uint8_t *)buf)[byte] & (1 << byte_off)) != 0) {
                    put_pixel(surface, x, y, 255, 255, 255, 255);
                } else {
                    put_pixel(surface, x, y, 0, 0, 0, 255);
                }
            }
        }
        update();
    }

private:
    SDL_Window *sdlwin;
    SDL_Surface *surface;

    int width = 640;
    int height = 480;
};
