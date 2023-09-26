#!/usr/bin/env bash
set -e

yosys -ql icebreaker.log -p "synth_ice40 -top top -json icebreaker.json" fpga/icebreaker/icebreaker.v src/alu.v src/control.v src/cpu.v src/fpga_cpu_top.v

nextpnr-ice40 --up5k --package sg48 --json icebreaker.json --pcf fpga/icebreaker/icebreaker.pcf --asc icebreaker.asc

icepack icebreaker.asc icebreaker.bin
