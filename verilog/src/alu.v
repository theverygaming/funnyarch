module alu (
    input [3:0] opcode,
    input [31:0] in1,
    in2,
    output reg [31:0] out,
    output reg carry,
    zero
);
  wire signed [31:0] in1s = in1;
  wire signed [31:0] in2s = in2;
  reg [32:0] tmp;
  always @(opcode or in1 or in2) begin
    case (opcode)
      4'h1: tmp = {1'b0, in1} + {1'b0, in2};  /* add */
      4'h2: tmp = {1'b0, in1} - {1'b0, in2};  /* sub */
      4'h3: tmp = {1'b0, in1} << {1'b0, in2[4:0]};  /* shl (logical) */
      4'h4: tmp = {1'b0, in1} >> {1'b0, in2[4:0]};  /* shr (logical) */
      4'h5: tmp = {1'b0, in1s >>> in2s[4:0]};  /* sar (arithmetic) */
      4'h6: tmp = {1'b0, in1} & {1'b0, in2};  /* and */
      4'h7: tmp = {1'b0, in1} | {1'b0, in2};  /* or */
      4'h8: tmp = {1'b0, in1} ^ {1'b0, in2};  /* xor */
      4'h9: tmp = ~{1'b0, in1};  /* not */
      default: tmp = 0;
    endcase
    out   = tmp[31:0];
    carry = tmp[32];
    zero  = tmp[31:0] == 0;
  end
endmodule
