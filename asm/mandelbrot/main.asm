// reference C code (below) converted to assembly by deneb (https://github.com/DenebTM) and theverygaming

.origin 0x0
entry:
  rjmp main

#include "macros.asm"

#define WIDTH 640
#define HEIGHT 480

#define MAX_ITER 128

#define FIXED_POINT_SHIFT 14

#define REG_const_cx_step r10
#define REG_const_cy_step r11
#define REG_const_threshold r12

#define REG_cx r13
#define REG_cy r14

#define REG_x r15
#define REG_y r16
#define REG_x_2 r17
#define REG_y_2 r18

#define REG_pix32 r19

#define REG__32 r20
#define REG_px r21
#define REG_py r22
#define REG_iteration r23

#define FB_ADDR_LO 0x0000
#define FB_ADDR_HI 0xF000

main:
  mov r0, #0b1 // set alignment flag
  mtsr pcst, r0
  mov r0, entry
  or r0, r0, #0x1 // no jump table
  mtsr ibptr, r0
  mov rsp, #0x2100
  push(lr)

  // initialize variables
  mov REG_const_cx_step, #0x4c
  mov REG_const_cy_step, #0x44
  mov REG_const_threshold, #0x0
  movh REG_const_threshold, #0x4000
  mov REG_cx, #0x7000
  movh REG_cx, #0xffff
  mov REG_cy, #0xc000
  movh REG_cy, #0xffff

  // for (py = 0; py < HEIGHT; py++) {
  mov REG_py, #0
  .L0:
  cmp REG_py, #HEIGHT
  ifgteq rjmp .L0_END

    // since cx is reset to its initial value every line, we push it to the stack and restore it again
    push(REG_cx)

    // for (px = 0; px < WIDTH; px += 32) {
    mov REG_px, #0
    .L1:
    cmp REG_px, #WIDTH
    ifgteq rjmp .L1_END

      // pix32 = 0
      mov REG_pix32, #0

      // for (_32 = 0; _32 < 32; _32++) {
      mov REG__32, #0
      .L3:
      cmp REG__32, #32
      ifgteq rjmp .L3_END

        mov REG_x, #0
        mov REG_y, #0

        // x_2 = 0
        mov REG_x_2, #0
        // y_2 = 0
        mov REG_y_2, #0

        // for (iteration = 0; iteration < MAX_ITER; iteration++) {
        mov REG_iteration, #0
        .L4:
        cmp REG_iteration, #MAX_ITER
        ifgteq rjmp .L4_END

          shl r0, REG_x, #1                     // y = ((2 * x ...
          mov r1, REG_y                         // ... * y) ...
          rcall(mult)
          sar r0, r0, #FIXED_POINT_SHIFT        // ... / SCALE)
          add REG_y, r0, REG_cy                 // ... + cy

          mov REG_x, REG_x_2                    // x = (x_2 ...
          sub REG_x, REG_x, REG_y_2             // ... - y_2) ...
          sar REG_x, REG_x, #FIXED_POINT_SHIFT  // ... / SCALE ...
          add REG_x, REG_x, REG_cx              // ... + cx

          // x_2 = x * x
          mov r0, REG_x
          mov r1, REG_x
          rcall(mult)
          mov REG_x_2, r0

          // y_2 = y * y
          mov r0, REG_y
          mov r1, REG_y
          rcall(mult)
          mov REG_y_2, r0

          // if (x_2 + y_2 > threshold) {
          add r0, REG_x_2, REG_y_2
          cmp r0, REG_const_threshold
            // pix32 |= (1 << _32)
            ifgt mov r2, #1
            ifgt shl r2, r2, REG__32
            ifgt or REG_pix32, REG_pix32, r2
            // break
            ifgt rjmp .L4_END

        // END: for (iteration = 0; iteration < MAX_ITER; iteration++) {
        add REG_iteration, #1
        rjmp .L4
        .L4_END:

        // cx += cx_step
        add REG_cx, REG_cx, REG_const_cx_step

      // END: for (_32 = 0; _32 < 32; _32++) {
      add REG__32, #1
      rjmp .L3
      .L3_END:

      // write pixels to 640x480 framebuffer
      mov r0, #80 // 640/8
      mov r1, REG_py
      rcall(mult)
      sar r1, REG_px, #3  // x = x/8
      add r0, r0, r1      // dest = y + x
      addh r0, #FB_ADDR_HI
      str r0, REG_pix32, #0

    // END: for (px = 0; px < WIDTH; px += 32) {
    add REG_px, #32
    rjmp .L1
    .L1_END:

    // since cx is reset to its initial value every line, we push it to the stack and restore it again
    pop(REG_cx)

    // cy += cy_step
    add REG_cy, REG_cy, REG_const_cy_step

  // END: for (py = 0; py < HEIGHT; py++) {
  add REG_py, #1
  rjmp .L0
  .L0_END:


  pop(lr)
end:
  rjmp end

// multiplies r0 by r1 and returns in r0
// https://en.wikipedia.org/wiki/Ancient_Egyptian_multiplication#Russian_peasant_multiplication
mult:
  push(r1)
  push(r2)
  push(r3)
  mov r2, #0
.mult_L0:
  cmp r0, #0
  ifeq rjmp .mult_end
  and r3, r0, #0x1
  cmp r3, #0
  ifneq add r2, r2, r1
  shr r0, r0, #1
  shl r1, r1, #1
  rjmp .mult_L0
.mult_end:
  mov r0, r2
  pop(r3)
  pop(r2)
  pop(r1)
  ret


// reference C code by deneb (originally written for a university assignment; modified for fixed-point operation)
/*
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#define STB_IMAGE_WRITE_IMPLEMENTATION
#include "stb_image_write.h"

#define WIDTH    640
#define HEIGHT   480
#define MAX_ITER 128

#define SCALE 16384

#define FRACTAL_XMIN (int32_t)((-2.25 / 1) * SCALE)
#define FRACTAL_XMAX (int32_t)((0.75 / 1) * SCALE)
#define FRACTAL_YMIN (int32_t)((-1.00 / 1) * SCALE)
#define FRACTAL_YMAX (int32_t)((1.00 / 1) * SCALE)

void calc_mandelbrot(uint8_t *image) {
  const uint32_t cx_step = (FRACTAL_XMAX - FRACTAL_XMIN) / WIDTH;
  const uint32_t cy_step = (FRACTAL_YMAX - FRACTAL_YMIN) / HEIGHT;

  const uint32_t threshold = 4 * (SCALE * SCALE);

  printf("constants: cx_step: 0x%x, cy_step: 0x%x, threshold: 0x%x\n", (unsigned int)cx_step, (unsigned int)cy_step, (unsigned int)threshold);

  // complex y coordinate
  uint32_t cy = FRACTAL_YMIN;
  // complex x coordinate
  uint32_t cx = FRACTAL_XMIN;

  printf("intial values: cx: 0x%x, cy: 0x%x\n", (unsigned int)cx, (unsigned int)cy);

  uint32_t x, y;
  uint32_t x_2, y_2;

  uint32_t pix32;

  uint32_t _32;
  uint32_t px;
  uint32_t py;
  uint32_t iteration;

  for (py = 0; py < HEIGHT; py++) {
    cx = FRACTAL_XMIN;

    // iterate over 4-byte words
    for (px = 0; px < WIDTH; px += 32) {
      pix32 = 0;

      // iterate over 32 pixels represented by that word
      for (_32 = 0; _32 < 32; _32++) {
        x = 0;
        y = 0;

        // x_2 = x * x;
        // y_2 = y * y;
        x_2 = 0;
        y_2 = 0;

        // check if calculation escapes boundary
        for (iteration = 0; iteration < MAX_ITER; iteration++) {
          y = (int32_t)(2 * x * y) / SCALE + cy;
          x = (int32_t)(x_2 - y_2) / SCALE + cx;;

          x_2 = x * x;
          y_2 = y * y;

          // if yes within 128 iterations, make pixel white
          if (x_2 + y_2 > threshold) {
            pix32 |= (1 << _32);
            break;
          }
        }
        cx += cx_step;
      }

      // "simulate" a 32-bit write to a 1bpp framebuffer
      for (uint32_t i = 0; i < 32; i++) {
        image[(py * WIDTH) + px + i] = (pix32 & (1 << i)) ? 0 : 255;
      }
    }
    cy += cy_step;
  }
}

int main() {
  uint8_t *image = malloc(HEIGHT * WIDTH * sizeof(*image));

  calc_mandelbrot(image);

  const int channel_nr = 1, stride_bytes = 0;
  stbi_write_png("mandelbrot.png", WIDTH, HEIGHT, channel_nr, image, stride_bytes);

  free(image);

  return EXIT_SUCCESS;
}
*/
