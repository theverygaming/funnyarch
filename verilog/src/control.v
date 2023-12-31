module control (
    input clk,
    reset,

    // memory
    input [31:0] data_in,
    output reg [31:0] data_out,
    output reg data_rw,  // write if 1
    output reg [31:0] address,

    // ALU
    output reg [3:0] alu_opcode,
    output reg [31:0] alu_op1,
    output reg [31:0] alu_op2,
    input [31:0] alu_out,
    input alu_carry,
    alu_zero

    // definitions
    `define STATE_FETCH 3'h0
    `define STATE_DECODE 3'h1
    `define STATE_WRITEBACK 3'h2
    `define STATE_WAIT 3'h5

    // register definitions
    `define REG_LR 28
    `define REG_RSP 29
    `define REG_RIP 30
    `define REG_RF 31
    `define SYSREG_IRIP 4
    `define SYSREG_IBPTR 5
    `define SYSREG_PCST 6
);
  `include "src/config.vh"

  function void interrupt;
    input reg [7:0] intnum;
    input reg exception;
    begin
      sysregarr[`SYSREG_IRIP] <= (exception == 1) ? (regarr[`REG_RIP] - 4) : regarr[`REG_RIP];
      sysregarr[`SYSREG_PCST][31:24] <= intnum;
      if (sysregarr[`SYSREG_IBPTR][0] != 0)
        regarr[`REG_RIP] <= {sysregarr[`SYSREG_IBPTR][31:2], 2'h0};
      else regarr[`REG_RIP] <= {sysregarr[`SYSREG_IBPTR][31:2], 2'h0} + {22'h0, intnum, 2'h0};
      state <= `STATE_FETCH;
    end
  endfunction

  reg [31:0] instr;
  reg [2:0] state;
  reg [2:0] state_next;

  reg [31:0] regarr[31:0];
  reg [31:0] sysregarr[6:0];

  always @(posedge clk) begin
    if (reset == 1) begin
      //$display("CPU: reset");
      regarr[`REG_RIP] <= `INITIAL_RIP;
      regarr[`REG_RF] <= 32'b0;

      state <= `STATE_FETCH;
    end  // fetch
    else if (state == `STATE_FETCH) begin
      //$display("CPU: fetch rip: 0x%h", {regarr[`REG_RIP][31:2], 2'b0});
      address = {regarr[`REG_RIP][31:2], 2'b0};
      data_rw <= 0;
      regarr[`REG_RIP] <= {regarr[`REG_RIP][31:2], 2'b0} + 4;
      state <= `STATE_WAIT;
      state_next <= `STATE_DECODE;
    end  // decode
    else if (state == `STATE_DECODE) begin
      instr = data_in;
      if ((instr[8:6] == 0) ||  // always
          (instr[8:6] == 1 && regarr[`REG_RF][1] == 1) ||  // if equal
          (instr[8:6] == 2 && regarr[`REG_RF][1] == 0) ||  // if not equal
          (instr[8:6] == 3 && regarr[`REG_RF][0] == 1) ||  // if less than
          (instr[8:6] == 4 && regarr[`REG_RF][0] == 0) ||  // if greater than or equal
          (instr[8:6] == 5 && regarr[`REG_RF][1:0] == 0) ||  // if greater than
          (instr[8:6] == 6 && regarr[`REG_RF][1:0] != 0) ||  // if less than or equal
          (instr[8:6] == 7)  // always
          ) begin
        //$display("CPU: decoding opcode 0x%h", instr[5:0]);
        case (instr[5:0])
          6'h00: begin  /* NOP */
            state <= `STATE_FETCH;
          end
          6'h01: begin  /* STRPI(E2) */
            if ((sysregarr[`SYSREG_PCST][0] != 0) && (((regarr[instr[18:14]] + {{20{instr[31]}}, instr[30:19]}) & 32'b11) != 0)) begin
              interrupt(254, 1);
            end else begin
              regarr[instr[18:14]] <= regarr[instr[18:14]] + {{20{instr[31]}}, instr[30:19]};
              address = regarr[instr[18:14]] + {{20{instr[31]}}, instr[30:19]};
              data_rw <= 1;
              data_out <= regarr[instr[13:9]];
              state <= `STATE_WAIT;
              state_next <= `STATE_FETCH;
            end
          end
          6'h02: begin  /* JMP(E4) */
            regarr[`REG_RIP] <= {7'b0, instr[31:9], 2'b0};
            state <= `STATE_FETCH;
          end
          6'h03: begin  /* RJMP(E4) */
            regarr[`REG_RIP] <= regarr[`REG_RIP] + {{8{instr[31]}}, instr[30:9], 2'b0};
            state <= `STATE_FETCH;
          end
          6'h04: begin  /* MOV(E7) */
            regarr[instr[18:14]] <= regarr[instr[13:9]];
            state <= `STATE_FETCH;
          end
          6'h05: begin  /* MOV(E3) MOVH(E3) */
            if (instr[14] == 1) regarr[instr[13:9]] <= {instr[31:16], regarr[instr[13:9]][15:0]};
            else regarr[instr[13:9]] <= {16'b0, instr[31:16]};
            state <= `STATE_FETCH;
          end
          6'h06: begin  /* LDR(E2) */
            if ((sysregarr[`SYSREG_PCST][0] != 0) && (((regarr[instr[13:9]] + {{20{instr[31]}}, instr[30:19]}) & 32'b11) != 0)) begin
              interrupt(254, 1);
            end else begin
              address = regarr[instr[13:9]] + {{20{instr[31]}}, instr[30:19]};
              state <= `STATE_WAIT;
              state_next <= `STATE_WRITEBACK;
            end
          end
          6'h07: begin  /* LDRI(E2) */
            if ((sysregarr[`SYSREG_PCST][0] != 0) && (regarr[instr[13:9]][1:0] != 0)) begin
              interrupt(254, 1);
            end else begin
              regarr[instr[13:9]] <= regarr[instr[13:9]] + {{20{instr[31]}}, instr[30:19]};
              address = regarr[instr[13:9]];
              state <= `STATE_WAIT;
              state_next <= `STATE_WRITEBACK;
            end
          end
          6'h08: begin  /* STR(E2) */
            if ((sysregarr[`SYSREG_PCST][0] != 0) && (((regarr[instr[18:14]] + {{20{instr[31]}}, instr[30:19]}) & 32'b11) != 0)) begin
              interrupt(254, 1);
            end else begin
              address = regarr[instr[18:14]] + {{20{instr[31]}}, instr[30:19]};
              data_rw <= 1;
              data_out <= regarr[instr[13:9]];
              state <= `STATE_WAIT;
              state_next <= `STATE_FETCH;
            end
          end
          6'h09: begin  /* STRI(E2) */
            if ((sysregarr[`SYSREG_PCST][0] != 0) && (regarr[instr[18:14]][1:0] != 0)) begin
              interrupt(254, 1);
            end else begin
              regarr[instr[18:14]] <= regarr[instr[18:14]] + {{20{instr[31]}}, instr[30:19]};
              address = regarr[instr[18:14]];
              data_rw <= 1;
              data_out <= regarr[instr[13:9]];
              state <= `STATE_WAIT;
              state_next <= `STATE_FETCH;
            end
          end
          6'h0a: begin  /* JAL(E4) */
            regarr[`REG_LR] <= regarr[`REG_RIP];
            regarr[`REG_RIP] <= {7'b0, instr[31:9], 2'b0};
            state <= `STATE_FETCH;
          end
          6'h0b: begin  /* RJAL(E4) */
            regarr[`REG_LR] <= regarr[`REG_RIP];
            regarr[`REG_RIP] <= regarr[`REG_RIP] + {{8{instr[31]}}, instr[30:9], 2'b0};
            state <= `STATE_FETCH;
          end
          6'h0c: begin  /* CMP(E7) */
            alu_op1 <= regarr[instr[18:14]];
            alu_op2 <= regarr[instr[13:9]];
            alu_opcode <= 4'h2;
            state <= `STATE_WRITEBACK;
          end
          6'h0d: begin  /* CMP(E3) */
            alu_op1 <= regarr[instr[13:9]];
            alu_op2 <= {16'b0, instr[31:16]};
            alu_opcode <= 4'h2;
            state <= `STATE_WRITEBACK;
          end
          6'h0e: begin  /* INT(E4) */
            // exceptions cannot be thrown with the int instruction
            if (instr[16:9] >= 254) begin
              interrupt(255, 1);
            end else begin
              interrupt(instr[16:9], 0);
            end
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
          6'h12: begin  /* ADD(E3) ADDH(E3) */
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
          6'h15: begin  /* SUB(E3) SUBH(E3) */
            alu_op1 <= regarr[instr[13:9]];
            if (instr[14] == 1) alu_op2 <= {instr[31:16], 16'b0};
            else alu_op2 <= {16'b0, instr[31:16]};
            alu_opcode <= 4'h2;
            state <= `STATE_WRITEBACK;
          end
          6'h16: begin  /* SHL(E1) */
            alu_op1 <= regarr[instr[13:9]];
            alu_op2 <= regarr[instr[18:14]];
            alu_opcode <= 4'h3;
            state <= `STATE_WRITEBACK;
          end
          6'h17: begin  /* SHL(E2) */
            alu_op1 <= regarr[instr[13:9]];
            alu_op2 <= {19'b0, instr[31:19]};
            alu_opcode <= 4'h3;
            state <= `STATE_WRITEBACK;
          end
          6'h18: begin  /* SHR(E1) */
            alu_op1 <= regarr[instr[13:9]];
            alu_op2 <= regarr[instr[18:14]];
            alu_opcode <= 4'h4;
            state <= `STATE_WRITEBACK;
          end
          6'h19: begin  /* SHR(E2) */
            alu_op1 <= regarr[instr[13:9]];
            alu_op2 <= {19'b0, instr[31:19]};
            alu_opcode <= 4'h4;
            state <= `STATE_WRITEBACK;
          end
          6'h1A: begin  /* SAR(E1) */
            alu_op1 <= regarr[instr[13:9]];
            alu_op2 <= regarr[instr[18:14]];
            alu_opcode <= 4'h5;
            state <= `STATE_WRITEBACK;
          end
          6'h1B: begin  /* SAR(E2) */
            alu_op1 <= regarr[instr[13:9]];
            alu_op2 <= {19'b0, instr[31:19]};
            alu_opcode <= 4'h5;
            state <= `STATE_WRITEBACK;
          end
          6'h1C: begin  /* AND(E1) */
            alu_op1 <= regarr[instr[13:9]];
            alu_op2 <= regarr[instr[18:14]];
            alu_opcode <= 4'h6;
            state <= `STATE_WRITEBACK;
          end
          6'h1D: begin  /* AND(E2) */
            alu_op1 <= regarr[instr[13:9]];
            alu_op2 <= {19'b0, instr[31:19]};
            alu_opcode <= 4'h6;
            state <= `STATE_WRITEBACK;
          end
          6'h1E: begin  /* AND(E3) ANDH(E3) */
            alu_op1 <= regarr[instr[13:9]];
            if (instr[14] == 1) alu_op2 <= {instr[31:16], 16'b0};
            else alu_op2 <= {16'b0, instr[31:16]};
            alu_opcode <= 4'h6;
            state <= `STATE_WRITEBACK;
          end
          6'h1F: begin  /* OR(E1) */
            alu_op1 <= regarr[instr[13:9]];
            alu_op2 <= regarr[instr[18:14]];
            alu_opcode <= 4'h7;
            state <= `STATE_WRITEBACK;
          end
          6'h20: begin  /* OR(E2) */
            alu_op1 <= regarr[instr[13:9]];
            alu_op2 <= {19'b0, instr[31:19]};
            alu_opcode <= 4'h7;
            state <= `STATE_WRITEBACK;
          end
          6'h21: begin  /* OR(E3) ORH(E3) */
            alu_op1 <= regarr[instr[13:9]];
            if (instr[14] == 1) alu_op2 <= {instr[31:16], 16'b0};
            else alu_op2 <= {16'b0, instr[31:16]};
            alu_opcode <= 4'h7;
            state <= `STATE_WRITEBACK;
          end
          6'h22: begin  /* XOR(E1) */
            alu_op1 <= regarr[instr[13:9]];
            alu_op2 <= regarr[instr[18:14]];
            alu_opcode <= 4'h8;
            state <= `STATE_WRITEBACK;
          end
          6'h23: begin  /* XOR(E2) */
            alu_op1 <= regarr[instr[13:9]];
            alu_op2 <= {19'b0, instr[31:19]};
            alu_opcode <= 4'h8;
            state <= `STATE_WRITEBACK;
          end
          6'h24: begin  /* XOR(E3) XORH(E3) */
            alu_op1 <= regarr[instr[13:9]];
            if (instr[14] == 1) alu_op2 <= {instr[31:16], 16'b0};
            else alu_op2 <= {16'b0, instr[31:16]};
            alu_opcode <= 4'h8;
            state <= `STATE_WRITEBACK;
          end
          6'h25: begin  /* NOT(E7) */
            alu_op1 <= regarr[instr[13:9]];
            alu_opcode <= 4'h9;
            state <= `STATE_WRITEBACK;
          end
          6'h26: begin  /* MTSR(E7) MFSR(E7) */
            if ((instr[31:19] == 13'h1 && instr[13:9] >= 7) || (instr[31:19] == 13'h0 && instr[18:14] >= 7)) begin
              interrupt(255, 1);
            end else begin
              if (instr[31:19] == 13'h1) begin  // MFSR
                regarr[instr[18:14]] = sysregarr[instr[13:9][2:0]];
              end else begin  // MTSR
                sysregarr[instr[18:14][2:0]] <= regarr[instr[13:9]];
              end
              state <= `STATE_FETCH;
            end
          end
          default: begin  /* invalid opcode */
            interrupt(255, 1);
          end
        endcase
      end else begin
        state <= `STATE_FETCH;
      end
    end  // writeback
    else if (state == `STATE_WRITEBACK) begin
      //$display("CPU: writeback");
      case (instr[5:0])
        6'h06: begin  /* LDR(E2) */
          regarr[instr[18:14]] <= data_in;
          state <= `STATE_FETCH;
        end
        6'h07: begin  /* LDRI(E2) */
          regarr[instr[18:14]] <= data_in;
          state <= `STATE_FETCH;
        end
        6'h0c: begin  /* CMP(E7) */
          regarr[`REG_RF][0] <= alu_carry;
          regarr[`REG_RF][1] <= alu_zero;
          state <= `STATE_FETCH;
        end
        6'h0d: begin  /* CMP(E3) */
          regarr[`REG_RF][0] <= alu_carry;
          regarr[`REG_RF][1] <= alu_zero;
          state <= `STATE_FETCH;
        end
        6'h10: begin  /* ADD(E1) */
          regarr[instr[23:19]] <= alu_out;
          state <= `STATE_FETCH;
        end
        6'h11: begin  /* ADD(E2) */
          regarr[instr[18:14]] <= alu_out;
          state <= `STATE_FETCH;
        end
        6'h12: begin  /* ADD(E3) */
          regarr[instr[13:9]] <= alu_out;
          state <= `STATE_FETCH;
        end
        6'h13: begin  /* SUB(E1) */
          regarr[instr[23:19]] <= alu_out;
          state <= `STATE_FETCH;
        end
        6'h14: begin  /* SUB(E2) */
          regarr[instr[18:14]] <= alu_out;
          state <= `STATE_FETCH;
        end
        6'h15: begin  /* SUB(E3) */
          regarr[instr[13:9]] <= alu_out;
          state <= `STATE_FETCH;
        end
        6'h16: begin  /* SHL(E1) */
          regarr[instr[23:19]] <= alu_out;
          state <= `STATE_FETCH;
        end
        6'h17: begin  /* SHL(E2) */
          regarr[instr[18:14]] <= alu_out;
          state <= `STATE_FETCH;
        end
        6'h18: begin  /* SHR(E1) */
          regarr[instr[23:19]] <= alu_out;
          state <= `STATE_FETCH;
        end
        6'h19: begin  /* SHR(E2) */
          regarr[instr[18:14]] <= alu_out;
          state <= `STATE_FETCH;
        end
        6'h1A: begin  /* SAR(E1) */
          regarr[instr[23:19]] <= alu_out;
          state <= `STATE_FETCH;
        end
        6'h1B: begin  /* SAR(E2) */
          regarr[instr[18:14]] <= alu_out;
          state <= `STATE_FETCH;
        end
        6'h1C: begin  /* AND(E1) */
          regarr[instr[23:19]] <= alu_out;
          state <= `STATE_FETCH;
        end
        6'h1D: begin  /* AND(E2) */
          regarr[instr[18:14]] <= alu_out;
          state <= `STATE_FETCH;
        end
        6'h1E: begin  /* AND(E3) */
          regarr[instr[13:9]] <= alu_out;
          state <= `STATE_FETCH;
        end
        6'h1F: begin  /* OR(E1) */
          regarr[instr[23:19]] <= alu_out;
          state <= `STATE_FETCH;
        end
        6'h20: begin  /* OR(E2) */
          regarr[instr[18:14]] <= alu_out;
          state <= `STATE_FETCH;
        end
        6'h21: begin  /* OR(E3) */
          regarr[instr[13:9]] <= alu_out;
          state <= `STATE_FETCH;
        end
        6'h22: begin  /* XOR(E1) */
          regarr[instr[23:19]] <= alu_out;
          state <= `STATE_FETCH;
        end
        6'h23: begin  /* XOR(E2) */
          regarr[instr[18:14]] <= alu_out;
          state <= `STATE_FETCH;
        end
        6'h24: begin  /* XOR(E3) */
          regarr[instr[13:9]] <= alu_out;
          state <= `STATE_FETCH;
        end
        6'h25: begin  /* NOT(E7) */
          regarr[instr[18:14]] <= alu_out;
          state <= `STATE_FETCH;
        end
        default: begin  /* TODO: it should not be possible to reach this */
          //$display("UNREACHABLE EXECUTED!!!");
          state <= `STATE_FETCH;
        end
      endcase
    end else if (state == `STATE_WAIT) begin
      state <= state_next;
    end else begin
      state <= state + 1;
    end
  end
endmodule
