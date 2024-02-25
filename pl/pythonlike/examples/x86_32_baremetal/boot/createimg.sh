#!/usr/bin/env sh
set -e

parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path"

cp ../obj/kernel.o root/boot/kernel.o
echo "Hello world!" > root/boot/initramfs.bin
grub-mkrescue -o ../boot.iso root/
