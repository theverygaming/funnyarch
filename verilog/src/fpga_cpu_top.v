module fpga_cpu_top (
    input clk_12m,
    reset,
    output [31:0] dbg
);
  wire [31:0] address;
  wire [31:0] data_in;
  wire [31:0] data_out;
  wire write;
  wire clk;

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
      address,
      dbg
  );

  rom rom (
      clk,
      address[6:0],
      data_in,
      address[12] == 0 && write == 0
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
    input [4:0] address,
    input [31:0] data_in,
    output reg [31:0] data_out,
    input write,
    cs
);
  reg [7:0] mem[20];

  always @(posedge clk) begin
    mem[8] <= 8'h03;
    if (write && cs) begin
      mem[address]   <= data_in[7:0];
      mem[address+1] <= data_in[15:8];
      mem[address+2] <= data_in[23:16];
      mem[address+3] <= data_in[31:24];
    end

    if ((write == 0) && cs) begin
      data_out <= {mem[address+3], mem[address+2], mem[address+1], mem[address]};
    end
  end
endmodule


module rom (
    input clk,
    input [6:0] address,
    output reg [31:0] data_out,
    input cs
);
  reg [7:0] mem[77];

  always @(posedge clk) begin
    mem[0]  = 8'h5;
    mem[1]  = 8'h0;
    mem[2]  = 8'h40;
    mem[3]  = 8'h0;
    mem[4]  = 8'hb;
    mem[5]  = 8'he;
    mem[6]  = 8'h0;
    mem[7]  = 8'h0;
    mem[8]  = 8'h5;
    mem[9]  = 8'h2;
    mem[10] = 8'h5;
    mem[11] = 8'h0;
    mem[12] = 8'h5;
    mem[13] = 8'h0;
    mem[14] = 8'h48;
    mem[15] = 8'h0;
    mem[16] = 8'hb;
    mem[17] = 8'h8;
    mem[18] = 8'h0;
    mem[19] = 8'h0;
    mem[20] = 8'h15;
    mem[21] = 8'h2;
    mem[22] = 8'h1;
    mem[23] = 8'h0;
    mem[24] = 8'hd;
    mem[25] = 8'h2;
    mem[26] = 8'h0;
    mem[27] = 8'h0;
    mem[28] = 8'h83;
    mem[29] = 8'hf6;
    mem[30] = 8'hff;
    mem[31] = 8'hff;
    mem[32] = 8'h3;
    mem[33] = 8'hfe;
    mem[34] = 8'hff;
    mem[35] = 8'hff;
    mem[36] = 8'h7;
    mem[37] = 8'h40;
    mem[38] = 8'h8;
    mem[39] = 8'h0;
    mem[40] = 8'h1e;
    mem[41] = 8'h2;
    mem[42] = 8'hff;
    mem[43] = 8'h0;
    mem[44] = 8'hd;
    mem[45] = 8'h2;
    mem[46] = 8'h0;
    mem[47] = 8'h0;
    mem[48] = 8'h43;
    mem[49] = 8'h4;
    mem[50] = 8'h0;
    mem[51] = 8'h0;
    mem[52] = 8'h4;
    mem[53] = 8'h2;
    mem[54] = 8'h6;
    mem[55] = 8'h0;
    mem[56] = 8'h3;
    mem[57] = 8'hf4;
    mem[58] = 8'hff;
    mem[59] = 8'hff;
    mem[60] = 8'h4;
    mem[61] = 8'hb8;
    mem[62] = 8'h7;
    mem[63] = 8'h0;
    mem[64] = 8'h68;
    mem[65] = 8'h65;
    mem[66] = 8'h6c;
    mem[67] = 8'h6c;
    mem[68] = 8'h6f;
    mem[69] = 8'h0;
    mem[70] = 8'h66;
    mem[71] = 8'h66;
    mem[72] = 8'h68;
    mem[73] = 8'h65;
    mem[74] = 8'h68;
    mem[75] = 8'h65;
    mem[76] = 8'h0;

    if (cs) begin
      data_out <= {mem[address+3], mem[address+2], mem[address+1], mem[address]};
    end
  end
endmodule
