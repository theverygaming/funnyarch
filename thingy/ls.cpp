#include <cstdint>
#include <cstdio>
#include <fstream>

#define DRV_IMPL
#include "drv.h"

int main() {
    struct drv_ctx ctx;
    std::fstream inf("./fs.bin", std::ios::in | std::ios::out | std::ios::binary);
    ctx.rw_ctx = &inf;
    ctx.dread = [](void *rw_ctx, uint32_t boff, char *dst, uint32_t n) {
        std::fstream *inf = (std::fstream *)rw_ctx;
        inf->seekg(boff, std::ios::beg);
        inf->read(dst, n);
        return (uint32_t)inf->gcount();
    };
    /*ctx.dwrite = [](void *rw_ctx, uint32_t boff, const char *src, uint32_t n) {
        std::fstream *inf = (std::fstream *)rw_ctx;
        inf->seekg(boff, std::ios::beg);
        inf->write(src, n);
        return (uint32_t)inf->gcount();
    };*/
    if (drv_init(&ctx) != 0) {
        return 1;
    }
    printf("OK\n");
    return 0;
}
