module control (
    input clk,
    reset,

    // memory
    input [31:0] data_in,
    output reg [31:0] data_out,
    output reg data_rw,  // write if 1
    output reg [31:0] address,

    // ALU
    output [ 3:0] alu_opcode,
    output [31:0] alu_op1,
    output [31:0] alu_op2,
    input  [31:0] alu_out

    // definitions
    `define STATE_FETCH 3'h0
    `define STATE_DECODE 3'h1
    `define STATE_WRITEBACK 3'h2
);
  reg [31:0] instr;
  reg [ 2:0] state;

  reg [31:0] regarr[31:0];

  always @(posedge clk) begin
    if (reset == 1) begin
      $display("CPU: reset");
      regarr[30] <= 32'h0;
      regarr[31] <= 32'b0;

      state <= `STATE_FETCH;
    end  // fetch
    else if (state == `STATE_FETCH) begin
      $display("CPU: fetch rip: 0x%h", {regarr[30][31:2], 2'b0});
      address = {regarr[30][31:2], 2'b0};

      data_rw <= 0;
      regarr[30] <= regarr[30] + 4;
      state <= `STATE_DECODE;
    end  // decode
    else if (state == `STATE_DECODE) begin
      instr = data_in;
      if (instr[8:6] == 0) begin
        $display("CPU: decoding opcode 0x%h", instr[5:0]);
        case (instr[5:0])
          6'h00: begin  /* NOP */
            state <= `STATE_FETCH;
          end
          6'h01: begin  /* JMP(E5) */
            regarr[30] <= regarr[instr[13:9]];
            state <= `STATE_FETCH;
          end
          6'h02: begin  /* JMP(E4) */
            regarr[30] <= {7'b0, instr[31:9], 2'b0};
            state <= `STATE_FETCH;
          end
          6'h03: begin  /* RJMP(E4) */
            if (instr[31] == 0) regarr[30] <= regarr[30] + {8'b0, instr[30:9], 2'b0};
            else regarr[30] <= regarr[30] + {8'hff, instr[30:9], 2'b0};
            state <= `STATE_FETCH;
          end
          6'h04: begin  /* MOV(E7) */
            regarr[instr[18:14]] <= regarr[instr[13:9]];
            state <= `STATE_FETCH;
          end
          6'h05: begin  /* MOV(E3) */
            if (instr[14] == 1) regarr[instr[13:9]] <= {instr[31:16], regarr[instr[13:9]][15:0]};
            else regarr[instr[13:9]] <= {16'b0, instr[31:16]};
            state <= `STATE_FETCH;
          end
          6'h06: begin  /* LDR(E2) */
            if (instr[31] == 0) address = regarr[instr[13:9]] + {20'b0, instr[30:19]};
            else address = regarr[instr[13:9]] + {20'hfffff, instr[30:19]};
            state <= `STATE_WRITEBACK;
          end
          6'h07: begin  /* LDRI(E2) */
            if (instr[31] == 0) regarr[instr[13:9]] <= regarr[instr[13:9]] + {20'b0, instr[30:19]};
            else regarr[instr[13:9]] <= regarr[instr[13:9]] + {20'hfffff, instr[30:19]};
            address = regarr[instr[13:9]];
            state <= `STATE_WRITEBACK;
          end
          6'h08: begin  /* STR(E2) */
            if (instr[31] == 0) address = regarr[instr[18:14]] + {20'b0, instr[30:19]};
            else address = regarr[instr[18:14]] + {20'hfffff, instr[30:19]};
            data_rw <= 1;
            data_out <= regarr[instr[13:9]];
            state <= `STATE_FETCH;
          end
          6'h09: begin  /* STRI(E2) */
            if (instr[31] == 0)
              regarr[instr[18:14]] <= regarr[instr[18:14]] + {20'b0, instr[30:19]};
            else regarr[instr[18:14]] <= regarr[instr[18:14]] + {20'hfffff, instr[30:19]};
            address = regarr[instr[18:14]];
            data_rw <= 1;
            data_out <= regarr[instr[13:9]];
            state <= `STATE_FETCH;
          end
          6'h10: begin  /* ADD(E1) */
            alu_op1 <= regarr[instr[13:9]];
            alu_op2 <= regarr[instr[18:14]];
            alu_opcode <= 4'h1;
            state <= `STATE_WRITEBACK;
          end
          6'h11: begin  /* ADD(E2) */
            alu_op1 <= regarr[instr[13:9]];
            alu_op2 <= {19'b0, instr[31:19]};
            alu_opcode <= 4'h1;
            state <= `STATE_WRITEBACK;
          end
          6'h12: begin  /* ADD(E3) */
            alu_op1 <= regarr[instr[13:9]];
            if (instr[14] == 1) alu_op2 <= {instr[31:16], 16'b0};
            else alu_op2 <= {16'b0, instr[31:16]};
            alu_opcode <= 4'h1;
            state <= `STATE_WRITEBACK;
          end
          6'h13: begin  /* SUB(E1) */
            alu_op1 <= regarr[instr[13:9]];
            alu_op2 <= regarr[instr[18:14]];
            alu_opcode <= 4'h2;
            state <= `STATE_WRITEBACK;
          end
          6'h14: begin  /* SUB(E2) */
            alu_op1 <= regarr[instr[13:9]];
            alu_op2 <= {19'b0, instr[31:19]};
            alu_opcode <= 4'h2;
            state <= `STATE_WRITEBACK;
          end
          6'h15: begin  /* SUB(E3) */
            alu_op1 <= regarr[instr[13:9]];
            if (instr[14] == 1) alu_op2 <= {instr[31:16], 16'b0};
            else alu_op2 <= {16'b0, instr[31:16]};
            alu_opcode <= 4'h2;
            state <= `STATE_WRITEBACK;
          end
          default: begin  /* invalid opcode */
            state <= `STATE_FETCH;
          end
        endcase
      end else begin
        state <= `STATE_FETCH;
      end
    end  // writeback
    else if (state == `STATE_WRITEBACK) begin
      $display("CPU: writeback");
      case (instr[5:0])
        6'h06: begin  /* LDR(E2) */
          regarr[instr[18:14]] = data_in;
          state <= `STATE_FETCH;
        end
        6'h07: begin  /* LDRI(E2) */
          regarr[instr[18:14]] = data_in;
          state <= `STATE_FETCH;
        end
        6'h10: begin  /* ADD(E1) */
          regarr[instr[23:19]] = alu_out;
          state <= `STATE_FETCH;
        end
        6'h11: begin  /* ADD(E2) */
          regarr[instr[18:14]] = alu_out;
          state <= `STATE_FETCH;
        end
        6'h12: begin  /* ADD(E3) */
          regarr[instr[13:9]] = alu_out;
          state <= `STATE_FETCH;
        end
        6'h13: begin  /* SUB(E1) */
          regarr[instr[23:19]] = alu_out;
          state <= `STATE_FETCH;
        end
        6'h14: begin  /* SUB(E2) */
          regarr[instr[18:14]] = alu_out;
          state <= `STATE_FETCH;
        end
        6'h15: begin  /* SUB(E3) */
          regarr[instr[13:9]] = alu_out;
          state <= `STATE_FETCH;
        end
        default: begin  /* invalid opcode */
          state <= `STATE_FETCH;
        end
      endcase
    end  // writeback
    /*else if (state == 3) begin
      $display("CPU: writeback");
      //write_data0 <= alu_out;
      state <= 0;
    end  // store
    else if (state == 4) begin
      $display("CPU: store");
      state <= 0;
    end*/
  end
endmodule