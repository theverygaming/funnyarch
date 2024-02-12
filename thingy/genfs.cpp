#include <cstdint>
#include <fstream>

// the block size should be divisible by the size of this structure
struct __attribute__((packed)) inode {
    uint32_t i_mode;           // bottom 9 bits are unix permissions, // TODO: top bits for inode type
    uint32_t i_ids;            // bottom 16 bits UID top 16 GID
    uint32_t i_ctime;          // creation time (UTC seconds since January 1st 1970)
    uint32_t i_atime;          // access time (UTC seconds since January 1st 1970)
    uint32_t i_size;           // size of contents in bytes
    uint32_t i_n_blocks;       // number of blocks the contents occupy
    uint32_t i_blocks[9];      // pointers to direct blocks
    uint32_t i_block_indirect; // pointer to first indirect block
};

struct __attribute__((packed)) dirent {
    uint32_t d_ptr; // pointer to the block the inode structure is in
    uint32_t d_idx; // index of the inode structure in the block
    char name[24];  // filename
};

struct __attribute__((packed)) superblock {
    uint32_t s_blocksize;    // block size used (power of two! and must be larger than the largest structure (which is currently the inode))
    uint32_t s_root_ptr;     // pointer to the block the root inode structure is in
    uint32_t s_root_idx;     // index of the root inode structure in the block
    uint32_t s_freelist_ptr; // pointer to the first block with a block_freelist_ent structure
};

struct __attribute__((packed)) block_freelist_ent {
    uint32_t f_prev;     // pointer to previous block that contains a block_freelist_ent
    uint32_t f_next;     // pointer to next block that contains a block_freelist_ent
    uint32_t f_n_blocks; // how many contigious blocks are free including this one
};

void gen_empty_fs(std::fstream &file, uint32_t blocksize, uint32_t nblocks) {}

int main(int argc, char **argv) {
    std::fstream outf("./fs.bin", std::ios::in | std::ios::out | std::ios::trunc | std::ios::binary);

    gen_empty_fs(outf, 512, 1000);
    return 0;
}
