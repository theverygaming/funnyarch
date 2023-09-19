#pragma once
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
        SDL_Init(SDL_INIT_VIDEO);
        sdlwin = SDL_CreateWindow("funnyarch", SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, width, height, 0);
    }

    void set_buf(void *buf, size_t buf_size) {
        _buf = buf;
        _buf_size = buf_size;
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

        SDL_Surface *surface = SDL_GetWindowSurface(sdlwin);
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
                    put_pixel_bw(SDL_GetWindowSurface(sdlwin), xpos, ypos, (byte & (1 << i)) != 0);
                }
            }
        }
    cleanup:
        SDL_UpdateWindowSurface(sdlwin);
        dirty = false;
        reset_dirty_rectangle();
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
        /*
        SDL_Surface *surface = SDL_GetWindowSurface(sdlwin);
        for (int i = 0; i < 4; i++) {
            uint8_t byte = (value >> (i * 8)) & 0xFF;
            for (int j = 0; j < 8; j++) {
                unsigned int xpos = x + (i * 8) + j;
                unsigned int ypos = y + (xpos / width);
                xpos %= width;
                if (ypos >= height) {
                    return;
                }
                put_pixel_bw(surface, xpos, ypos, (byte & (1 << j)) != 0);
            }
        }*/
    }

private:
    SDL_Window *sdlwin;

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
