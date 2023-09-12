#include <fstream>

struct __attribute__((packed)) enc_1 {
    unsigned int opcode : 6;
    unsigned int condition : 3;
    unsigned int src1 : 5;
    unsigned int src2 : 5;
    unsigned int tgt : 5;
    unsigned int _res : 8;
};

struct __attribute__((packed)) enc_2 {
    unsigned int opcode : 6;
    unsigned int condition : 3;
    unsigned int src : 5;
    unsigned int tgt : 5;
    unsigned int imm13 : 13;
};

struct __attribute__((packed)) enc_3 {
    unsigned int opcode : 6;
    unsigned int condition : 3;
    unsigned int tgt : 5;
    unsigned int spe : 2;
    unsigned int imm16 : 16;
};

struct __attribute__((packed)) enc_4 {
    unsigned int opcode : 6;
    unsigned int condition : 3;
    unsigned int imm23 : 23;
};

#define E1(_opcode, _condition, _src1, _src2, _tgt) \
    do {                                            \
        struct enc_1 w = {                          \
            .opcode = _opcode,                      \
            .condition = _condition,                \
            .src1 = _src1,                          \
            .src2 = _src2,                          \
            .tgt = _tgt,                            \
            ._res = 0,                              \
        };                                          \
        out.write((const char *)&w, sizeof(w));     \
    } while (0)

#define E2(_opcode, _condition, _src, _tgt, _imm13) \
    do {                                            \
        struct enc_2 w = {                          \
            .opcode = _opcode,                      \
            .condition = _condition,                \
            .src = _src,                            \
            .tgt = _tgt,                            \
            .imm13 = _imm13,                        \
        };                                          \
        out.write((const char *)&w, sizeof(w));     \
    } while (0)

#define E3(_opcode, _condition, _tgt, _spe, _imm16) \
    do {                                            \
        struct enc_3 w = {                          \
            .opcode = _opcode,                      \
            .condition = _condition,                \
            .tgt = _tgt,                            \
            .spe = _spe,                            \
            .imm16 = _imm16,                        \
        };                                          \
        out.write((const char *)&w, sizeof(w));     \
    } while (0)

#define E4(_opcode, _condition, _imm23)         \
    do {                                        \
        struct enc_4 w = {                      \
            .opcode = _opcode,                  \
            .condition = _condition,            \
            .imm23 = _imm23,                    \
        };                                      \
        out.write((const char *)&w, sizeof(w)); \
    } while (0)

int main() {
    std::ofstream out("output.bin", std::ios::binary);

    /*E1(0x00, 0, 0, 0, 0); // NOP
    E2(0x00, 0, 0, 0, 0); // NOP
    E3(0x00, 0, 0, 0, 0); // NOP
    E4(0x00, 0, 0);       // NOP*/

    E2(0x11, 0, 0, 1, 5); // ADD r0, r1, 5
    E1(0x10, 0, 1, 1, 1); // ADD r1, r1, r1

    E2(0x11, 0, 0, 2, 10); // ADD r0, r2, 10

    E1(0x10, 0, 1, 2, 3); // ADD r1, r2, r3
    E1(0x10, 0, 1, 2, 4); // ADD r1, r2, r4

    E3(0x12, 0, 4, 0, 1); // ADD r4, 1

    out.close();
    return 0;
}
