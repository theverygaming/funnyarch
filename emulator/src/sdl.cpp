#include <SDL2/SDL.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdlib.h>

#include "sdl.h"

#define WIDTH  640
#define HEIGHT 480

static SDL_Window *sdlwin;

static void sdlinit() {
    SDL_Init(SDL_INIT_VIDEO);
    sdlwin = SDL_CreateWindow("balls", SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, WIDTH, HEIGHT, 0);
}

static inline void put_pixel(SDL_Surface *surface, int x, int y, uint8_t r, uint8_t g, uint8_t b, uint8_t a) {
    uint32_t pixel = SDL_MapRGBA(surface->format, r, g, b, a);
    *((uint32_t *)((uint8_t *)surface->pixels + y * surface->pitch + x * surface->format->BytesPerPixel)) = pixel;
}

static SDL_Surface *surface = SDL_GetWindowSurface(sdlwin);
static SDL_Event event;

void sdl::init() {
    sdlinit();
    surface = SDL_GetWindowSurface(sdlwin);
}

void sdl::loop() {
    while (SDL_PollEvent(&event)) {
        if (event.type == SDL_QUIT) {
            exit(0);
        }
    }

    SDL_UpdateWindowSurface(sdlwin);
}

void *fb::buf;
size_t fb::buf_size;

void fb::init() {
    buf_size = (WIDTH * HEIGHT) / 8;
    if ((WIDTH * HEIGHT) % 8 != 0) {
        buf_size += 1;
    }

    buf = malloc(buf_size);
    memset(buf, 0, buf_size);
}

void fb::redraw() {
    for (size_t y = 0; y < HEIGHT; y++) {
        for (size_t x = 0; x < WIDTH; x++) {
            size_t bit = (y * WIDTH) + x;
            size_t byte = bit / 8;
            size_t byte_off = bit % 8;
            if ((((uint8_t *)buf)[byte] & (1 << byte_off)) != 0) {
                put_pixel(surface, x, y, 255, 255, 255, 255);
            } else {
                put_pixel(surface, x, y, 0, 0, 0, 255);
            }
        }
    }
}
