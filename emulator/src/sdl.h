#pragma once

namespace sdl {
    void init();
    void loop();
}

namespace fb {
    void init();
    void redraw();
    extern void *buf;
    extern size_t buf_size;
}
