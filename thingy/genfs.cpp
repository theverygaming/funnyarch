#include <cstdint>
#include <cstdio>
#include <cstring>
#include <fstream>
#include <stdexcept>

// NOTE: this code only works on little-endian machines

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

#define I_MODE_P_EX  (0x0001) // perms: everyone execute
#define I_MODE_P_EW  (0x0002) // perms: everyone write
#define I_MODE_P_ER  (0x0004) // perms: everyone read
#define I_MODE_P_GX  (0x0008) // perms: group execute
#define I_MODE_P_GW  (0x0010) // perms: group write
#define I_MODE_P_GR  (0x0020) // perms: group read
#define I_MODE_P_UX  (0x0040) // perms: user execute
#define I_MODE_P_UW  (0x0080) // perms: user write
#define I_MODE_P_UR  (0x0100) // perms: user read
#define I_MODE_F_DEL (0x0200) // file type: deleted inode
#define I_MODE_F_DIR (0x0400) // file type: directory
#define I_MODE_F_SYM (0x0800) // file type: symlink
#define I_MODE_F_SPE (0x1000) // file type: special file (device etc.)
#define I_MODE_F_REL (0x2000) // file type: regular file

struct __attribute__((packed)) dirent {
    uint32_t d_ptr; // pointer to the block the inode structure is in
    uint32_t d_idx; // index of the inode structure in the block
    char name[24];  // filename
};

struct __attribute__((packed)) superblock {
    uint32_t s_blocksize;            // block size used (power of two! and must be larger than the largest structure (which is currently the inode))
    uint32_t s_root_ptr;             // pointer to the block the root inode structure is in
    uint32_t s_root_idx;             // index of the root inode structure in the block
    uint32_t s_block_bitmap_st;      // pointer to start block of the block bitmap
    uint32_t s_block_bitmap_nblocks; // number of blocks in the block bitmap
};

/*
 * Block bitmap
 * Bytes, LSB is lowest block
 * Each block is represented by 2 bits, the LSB of the two being if the block is used and the MSB if it is an inode block
 */

// assumes the seek position is the start of the block bitmap
static void block_bitmap_set(std::fstream &file, uint32_t block, bool used, bool inode) {
    auto pos = file.tellg();

    uint32_t byteoff = block / (8 / 2);
    uint32_t bitoff = (block % (8 / 2)) * ((8 / 2) / 2);
    file.seekg(byteoff, file.cur);
    uint8_t b = file.get();
    b &= ~(0b11 << bitoff);
    b |= (used | (inode << 1)) << bitoff;
    file.seekg(-1, file.cur);
    file.put(b);

    file.seekg(pos);
}

// this function assumes the file passed is entirely empty and it's size is zero
static void gen_empty_fs(std::fstream &file, uint32_t blocksize, uint32_t nblocks) {
    if (nblocks < 3) {
        // throw new std::runtime_error("at least three blocks needed to generate FS (superblock, block bitmap, inode block)");
    }
    if (blocksize < sizeof(struct inode)) {
        throw new std::runtime_error("blocksize too low");
    }

    // ensure the file has the correct size
    file.seekg((blocksize * nblocks) - 1, std::ios::beg);
    file.put(0);

    uint32_t block_bitmap_blocks = (((nblocks / (8 / 2)) + ((8 / 2) - 1)) + (blocksize - 1)) / blocksize;

    // superblock
    file.seekg(blocksize * 0, std::ios::beg);
    struct superblock sb = {
        .s_blocksize = blocksize,
        .s_root_ptr = 1 + block_bitmap_blocks,
        .s_root_idx = 0,
        .s_block_bitmap_st = 1,
        .s_block_bitmap_nblocks = block_bitmap_blocks,
    };
    file.write((char *)&sb, sizeof(sb));

    // mark things as used in the block bitmap
    file.seekg(blocksize * 1, std::ios::beg);
    block_bitmap_set(file, 0, true, false); // superblock
    // block bitmap itself
    for (uint32_t i = 0; i < block_bitmap_blocks; i++) {
        block_bitmap_set(file, 1 + i, true, false);
    }
    block_bitmap_set(file, 1 + block_bitmap_blocks, true, true); // first inode block

    // root directory inode and first inode block
    file.seekg(blocksize * (1 + block_bitmap_blocks), std::ios::beg);
    struct inode in;
    memset(&in, 0, sizeof(in));
    in.i_mode = I_MODE_F_DIR;
    file.write((char *)&in, sizeof(in));
    in.i_mode = I_MODE_F_DEL;
    for (uint32_t i = 0; i < ((blocksize / sizeof(in)) - 1); i++) {
        file.write((char *)&in, sizeof(in));
    }
}

int main(int argc, char **argv) {
    std::fstream outf("./fs.bin", std::ios::in | std::ios::out | std::ios::trunc | std::ios::binary);

    gen_empty_fs(outf, 512, 1000);
    return 0;
}
