#include <cinttypes>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <fstream>
#include <stdexcept>
#include <utility>

// NOTE: this code only works on little-endian machines

// the block size should be divisible by the size of this structure
struct __attribute__((packed)) inode {
    uint32_t i_mode;
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

struct __attribute__((packed)) dirent {
    uint32_t d_mod;
    uint32_t d_ptr;  // pointer to the block the inode structure is in
    uint32_t d_idx;  // index of the inode structure in the block
    char d_name[52]; // filename
};
#define D_MOD_DEL (0x0001)

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

static void block_bitmap_get(std::fstream &file, uint32_t block, bool *used, bool *inode) {
    auto pos = file.tellg();

    uint32_t byteoff = block / (8 / 2);
    uint32_t bitoff = (block % (8 / 2)) * ((8 / 2) / 2);
    file.seekg(byteoff, file.cur);
    uint8_t b = file.get();
    b >>= bitoff;
    *used = b & 0b1;
    *inode = (b >> 1) & 0b1;
    file.seekg(-1, file.cur);

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
        .s_block_bitmap_nblocks = nblocks,
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
    in.i_mode = I_MODE_F_DIR | I_MODE_P_UR | I_MODE_P_UW | I_MODE_P_UX | I_MODE_P_GR | I_MODE_P_GX | I_MODE_P_ER | I_MODE_P_EX;
    file.write((char *)&in, sizeof(in));
    in.i_mode = I_MODE_F_DEL;
    for (uint32_t i = 0; i < ((blocksize / sizeof(in)) - 1); i++) {
        file.write((char *)&in, sizeof(in));
    }
}

static uint32_t alloc_data_block(std::fstream &file, struct superblock *super) {
    auto pos = file.tellg();

    file.seekg(super->s_blocksize * super->s_block_bitmap_st, std::ios::beg);

    uint32_t found = 0;
    for (uint32_t i = 0; i < super->s_block_bitmap_nblocks; i++) {
        bool used, inode;
        block_bitmap_get(file, i, &used, &inode);
        if (!used) {
            found = i;
            block_bitmap_set(file, i, true, false);
            break;
        }
    }

    file.seekg(pos);
    return found;
}

static void inode_io_bytes(std::fstream &file, struct superblock *super, struct inode *node, char *data, uint32_t nbytes, bool write) {
    if (write) {
        uint32_t required_blocks = ((node->i_size + nbytes) + (super->s_blocksize - 1)) / super->s_blocksize;
        if (required_blocks > 8) {
            throw std::runtime_error("indirect blocks unsupported");
        }
        for (uint32_t i = 0; i < required_blocks; i++) {
            if (node->i_blocks[i] == 0) {
                uint32_t alloc = alloc_data_block(file, super);
                if (alloc == 0) {
                    throw std::runtime_error("error allocating block");
                }
                node->i_blocks[i] = alloc;
            }
        }
    }
    auto pos = file.tellg();

    // TODO: argument
    uint32_t pos_beg = node->i_size;
    if (!write) {
        pos_beg = 0;
    }

    for (uint32_t i = 0; i < nbytes; i++) {
        uint32_t block = (pos_beg + i) / super->s_blocksize;
        uint32_t offset = (pos_beg + i) % super->s_blocksize;
        if (node->i_blocks[block] == 0) {
            throw std::runtime_error("error doing IO on inode");
        }
        file.seekg((node->i_blocks[block] * super->s_blocksize) + offset, std::ios::beg);
        if (write) {
            file.write(&data[i], 1);
        } else {
            file.read(&data[i], 1);
        }
    }
    if (write) {
        node->i_size += nbytes;
    }

    file.seekg(pos);
}

void do_ls(std::fstream &file) {
    file.seekg(0, std::ios::beg);
    struct superblock sb;
    file.read((char *)&sb, sizeof(sb));

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

    struct inode root;
    file.seekg((sb.s_root_ptr * sb.s_blocksize) + (sb.s_root_idx * sizeof(root)), std::ios::beg);
    file.read((char *)&root, sizeof(root));
    print_inode_info(".", &root);

    struct dirent de;
    struct inode node;
    for (int i = 0; i < root.i_size; i += sizeof(de)) {
        inode_io_bytes(file, &sb, &root, (char *)&de, sizeof(de), false);
        file.seekg((de.d_ptr * sb.s_blocksize) + (de.d_idx * sizeof(node)), std::ios::beg);
        file.read((char *)&node, sizeof(node));
        print_inode_info(de.d_name, &node);
        char *buf = (char *)malloc(node.i_size);
        inode_io_bytes(file, &sb, &node, buf, node.i_size, false);
        printf("file contents: %.*s\n", node.i_size, buf);
        free(buf);
    }
}

void create_file(std::fstream &file, const char *fname) {
    file.seekg(0, std::ios::beg);
    struct superblock sb;
    file.read((char *)&sb, sizeof(sb));

    char contents[] = "Hello world filesystem!";

    struct inode root;
    file.seekg((sb.s_root_ptr * sb.s_blocksize) + (sb.s_root_idx * sizeof(root)), std::ios::beg);
    file.read((char *)&root, sizeof(root));

    // TODO: inode alloc

    struct inode inew;
    memset(&inew, 0, sizeof(inew));
    inew.i_mode = I_MODE_F_REG | I_MODE_P_UR | I_MODE_P_UW | I_MODE_P_UX | I_MODE_P_GR | I_MODE_P_GX | I_MODE_P_ER | I_MODE_P_EX;
    struct dirent de {
        .d_mod = 0, .d_ptr = sb.s_root_ptr, .d_idx = sb.s_root_idx + 1, .d_name = {0},
    };
    strcpy(de.d_name, fname); // BUG: check length
    inode_io_bytes(file, &sb, &root, (char *)&de, sizeof(de), true);
    inode_io_bytes(file, &sb, &inew, contents, sizeof(contents), true);

    file.seekg((de.d_ptr * sb.s_blocksize) + (de.d_idx * sizeof(root)), std::ios::beg);
    file.write((char *)&inew, sizeof(inew));

    file.seekg((sb.s_root_ptr * sb.s_blocksize) + (sb.s_root_idx * sizeof(root)), std::ios::beg);
    file.write((char *)&root, sizeof(root));
}

int main(int argc, char **argv) {
    std::fstream outf("./fs.bin", std::ios::in | std::ios::out | std::ios::trunc | std::ios::binary);

    gen_empty_fs(outf, 512, 1000);
    do_ls(outf);
    create_file(outf, "test1");
    // create_file(outf, "test2");
    do_ls(outf);
    return 0;
}
