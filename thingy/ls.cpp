#include <cinttypes>
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
        // printf("dread: %u-%u\n", boff, boff + n);
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
    struct inode_io_handle root;
    if (open_root_node(&ctx, &root) != 0) {
        return 1;
    }

    auto print_inode_info = [](const char *name, struct inode *node) {
        char ftype[1 + 9];
        switch (node->i_mode & I_MODE_FTYPE_MASK) {
        case I_MODE_F_DEL:
            ftype[0] = 'X';
            break;
        case I_MODE_F_DIR:
            ftype[0] = 'd';
            break;
        case I_MODE_F_SYM:
            ftype[0] = 'l';
            break;
        case I_MODE_F_SPE:
            ftype[0] = 's';
            break;
        case I_MODE_F_REG:
            ftype[0] = '-';
            break;
        }
        ftype[1] = (node->i_mode & I_MODE_P_UR) ? 'r' : '-';
        ftype[2] = (node->i_mode & I_MODE_P_UW) ? 'w' : '-';
        ftype[3] = (node->i_mode & I_MODE_P_UX) ? 'x' : '-';
        ftype[4] = (node->i_mode & I_MODE_P_GR) ? 'r' : '-';
        ftype[5] = (node->i_mode & I_MODE_P_GW) ? 'w' : '-';
        ftype[6] = (node->i_mode & I_MODE_P_GX) ? 'x' : '-';
        ftype[7] = (node->i_mode & I_MODE_P_ER) ? 'r' : '-';
        ftype[8] = (node->i_mode & I_MODE_P_EW) ? 'w' : '-';
        ftype[9] = (node->i_mode & I_MODE_P_EX) ? 'x' : '-';
        printf("%.*s %" PRIu32 " %" PRIu32 " %" PRIu32 " %.52s\n",
               (int)sizeof(ftype),
               ftype,
               node->i_ids & 0xFFFF,
               (node->i_ids >> 16) & 0xFFFF,
               node->i_size,
               name);
    };

    struct dirent de;
    struct inode_io_handle node;
    for (int i = 0; i < root.node.i_size; i += sizeof(de)) {
        if (ino_read(&ctx, &root, (char *)&de, sizeof(de)) != sizeof(de)) {
            return 1;
        }
        if (ino_open(&ctx, &node, &de.d_ptr) != 0) {
            return 1;
        }
        print_inode_info(de.d_name, &node.node);
    }

    printf("OK\n");
    return 0;
}
