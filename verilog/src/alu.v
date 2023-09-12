module alu (
    input [3:0] opcode,
    input [31:0] in1,
    in2,
    output reg [31:0] out
);
  always @(*) begin
    case (opcode)
      4'h1: out = in1 + in2;  /* add */
      4'h2: out = in1 - in2;  /* sub */
      4'h3: out = in1 << in2;  /* shl (logical) */
      4'h4: out = in1 >> in2;  /* shr (logical) */
      4'h5: out = in1 >>> in2;  /* sar (arithmetic) */
      4'h6: out = in1 & in2;  /* and */
      4'h7: out = in1 | in2;  /* or */
      4'h8: out = in1 ^ in2;  /* xor */
      4'h9: out = ~in1;  /* not */
      default: out = 0;
    endcase
  end
endmodule
