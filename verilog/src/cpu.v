module cpu (
    input clk,
    reset,
    inout [31:0] data,
    output data_rw,  // write if 1
    output [31:0] address
);
  wire [3:0] alu_opcode;
  wire [31:0] alu_in1, alu_in2, alu_out;

  control ctrl (
      clk,
      reset,
      data,
      data,
      data_rw,
      address,
      alu_opcode,
      alu_in1,
      alu_in2,
      alu_out
  );
  alu alu (
      alu_opcode,
      alu_in1,
      alu_in2,
      alu_out
  );
endmodule
