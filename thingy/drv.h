#pragma once
#include <cstdint>

// NOTE: this code only works on little-endian machines

struct __attribute__((packed)) inode_ptr {
    uint32_t ip_block; // pointer to the block the inode structure is in
    uint32_t ip_off;   // index of the inode structure in the block
};

struct __attribute__((packed)) superblock {
    uint32_t s_blocksize; // block size used (power of two! and must be larger than the largest structure (which is currently the inode))
    struct inode_ptr s_root_ptr;
    uint32_t s_block_bitmap_st;      // pointer to start block of the block bitmap
    uint32_t s_block_bitmap_nblocks; // number of blocks in the block bitmap
};

// the block size should be divisible by the size of this structure
struct __attribute__((packed)) inode {
    uint32_t i_mode;           // bottom 9 bits are unix permissions, // TODO: top bits for inode type
    uint32_t i_ids;            // bottom 16 bits UID top 16 GID
    uint32_t i_ctime;          // creation time (UTC seconds since January 1st 1970)
    uint32_t i_mtime;          // modification time (UTC seconds since January 1st 1970)
    uint32_t i_spe;            // used for special files
    uint32_t i_size;           // size of contents in bytes
    uint32_t i_n_blocks;       // number of blocks the contents occupy
    uint32_t i_blocks[8];      // pointers to direct blocks
    uint32_t i_block_indirect; // pointer to first indirect block
};

#define I_MODE_P_EX       (0x0001) // perms: everyone execute
#define I_MODE_P_EW       (0x0002) // perms: everyone write
#define I_MODE_P_ER       (0x0004) // perms: everyone read
#define I_MODE_P_GX       (0x0008) // perms: group execute
#define I_MODE_P_GW       (0x0010) // perms: group write
#define I_MODE_P_GR       (0x0020) // perms: group read
#define I_MODE_P_UX       (0x0040) // perms: user execute
#define I_MODE_P_UW       (0x0080) // perms: user write
#define I_MODE_P_UR       (0x0100) // perms: user read
#define I_MODE_F_DEL      (0x0200) // file type: deleted inode
#define I_MODE_F_DIR      (0x0400) // file type: directory
#define I_MODE_F_SYM      (0x0800) // file type: symlink
#define I_MODE_F_SPE      (0x1000) // file type: special file (device etc.)
#define I_MODE_F_REG      (0x2000) // file type: regular file
#define I_MODE_FTYPE_MASK (0x3E00) // file type: mask

/*
 * An indirect block consists of (blocksize/4)-1 32-bit wide pointers to blocks and at the end one last pointer to the next indirect block
 */

struct __attribute__((packed)) dirent {
    struct inode_ptr d_ptr;
    char name[24]; // filename
};

// driver structures

struct drv_ctx {
    // these must be defined by the user
    void *rw_ctx;
    uint32_t (*dread)(void *rw_ctx, uint32_t boff, char *dst, uint32_t n);
#ifdef DRV_WRITE
    uint32_t (*dwrite)(void *rw_ctx, uint32_t boff, const char *src, uint32_t n);
#endif

    // internal fields
    struct superblock super;
};

struct inode_read_handle {
    struct inode_ptr ptr;
    struct inode node;
    uint32_t pos;
};

#ifdef DRV_IMPL

int drv_init(struct drv_ctx *ctx) {
    if (ctx->dread(ctx->rw_ctx, 0, (char *)&ctx->super, sizeof(ctx->super)) != sizeof(ctx->super)) {
        return -1;
    }
    // TODO: sanity checks
    return 0;
}

int ino_open(struct drv_ctx *ctx, struct inode_ptr *ptr, struct inode_read_handle *hndl) {
    hndl->ptr = *ptr;
    if (ctx->dread(ctx->rw_ctx,
                   (hndl->ptr.ip_block + ctx->super.s_blocksize) + (hndl->ptr.ip_off * sizeof(hndl->node)),
                   (char *)&hndl->node,
                   sizeof(hndl->node)) != sizeof(hndl->node)) {
        return -1;
    }
    if (hndl->node.i_mode & I_MODE_F_DEL) {
        return -1;
    }
    return 0;
};

//int ino_read(struct drv_ctx *ctx, )

#else
int drv_init(struct drv_ctx ctx *)();
#endif
