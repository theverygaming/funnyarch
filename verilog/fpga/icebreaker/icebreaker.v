module top (
    BTN1,
    CLK,
    LED1,
    LED2,
    LED3,
    LED4,
    LED5
);
  input BTN1, CLK;
  output LED1, LED2, LED3, LED4, LED5;

  wire [31:0] dbg;
  fpga_cpu_top fpga_cpu_top (
      CLK,
      BTN1,
      dbg
  );

  assign {LED5, LED4, LED3, LED2, LED1} = dbg[4:0];
endmodule
