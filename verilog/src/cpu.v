module cpu (
    input clk,
    reset,
    input [31:0] data_in,
    output [31:0] data_out,
    output data_rw,  // write if 1
    output [31:0] address
);
  wire [3:0] alu_opcode;
  wire [31:0] alu_in1, alu_in2, alu_out;
  wire alu_carry, alu_zero;

  control ctrl (
      clk,
      reset,
      data_in,
      data_out,
      data_rw,
      address,
      alu_opcode,
      alu_in1,
      alu_in2,
      alu_out,
      alu_carry,
      alu_zero
  );
  alu alu (
      alu_opcode,
      alu_in1,
      alu_in2,
      alu_out,
      alu_carry,
      alu_zero
  );
endmodule
