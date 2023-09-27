module fpga_cpu_top (
    input clk_12m,
    reset,
    output reg [31:0] dbg
);
  wire [31:0] address;
  wire [31:0] data_in;
  wire [31:0] data_out;
  wire write;
  wire clk;
  wire [31:0] ram_data_in;
  wire [31:0] rom_data_in;


  clkdiv clkdiv (
      clk_12m,
      clk
  );

  cpu cpu (
      clk,
      reset,
      data_in,
      data_out,
      write,
      address
  );

  always @(posedge clk) begin
    if (address == 0 && write) begin
      dbg <= data_out;
    end
  end

  assign data_in = address[31:12] == 0 ? ram_data_in : 0;

  ram ram (
      clk,
      address[11:2],
      data_out,
      ram_data_in,
      write,
      (address[31:12] == 0 && address[1:0] == 0)
  );

endmodule


module clkdiv (
    input clk_in,
    output reg clk_out
);
  reg [19:0] cnt = 20'h0;
  parameter DIV = 20'd100000;

  always @(posedge clk_in) begin
    cnt <= cnt + 1;
    if (cnt >= (DIV - 1)) cnt <= 20'h0;
    clk_out <= (cnt < (DIV / 2)) ? 1'b1 : 1'b0;
  end
endmodule


module ram (
    input clk,
    input [9:0] address,
    input [31:0] data_in,
    output reg [31:0] data_out,
    input write,
    cs
);
  reg [31:0] mem[1024];

  initial begin
    $readmemh("hex_memory_file.mem", mem);
  end

  always @(posedge clk) begin
    if ((write == 0) && cs) begin
      data_out <= mem[address];
    end

    if (write && cs) begin
      mem[address] <= data_in;
    end
  end
endmodule
