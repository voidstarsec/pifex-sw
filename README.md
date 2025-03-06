# pifex-sw

Software modules and examples for the PiFex

# Overview

This repository contains multiple tools and utilities that help enable a Raspberry Pi as a generic hardware hacking tool. See the following blog posts for more usage information and instructions:

- [Brushing Up on Hardware Hacking Part 1 - Configuring the PiFex](TODO)
- [Brushing Up on Hardware Hacking Part 2 - SPI, UART, Pulseview and Flashrom](TODO)
- [Brushing Up on Hardware Hacking Part 3 - Hardware Level Debuggers](TODO)
- [JTAG Hacking with a Raspberry Pi](https://voidstarsec.com/blog/jtag-pifex)


# Structure

- `examples` - Contains various config files for OpenOCD
- `gadgets` - GadgetFS script to enable an ethernet/serial composite gadget
- `notebooks` - Jupyter notebooks for basic PiFex usage
- `oled` - Scripts for managing the OLED interface
- `pifex-ui` - Example web interface for OpenOCD
- `services` - SystemD service files for various PiFex services


# Image Generation

The files included in this repository can be used in conjunction with the [pi-gen]() project to build a clean Raspberry Pi images with all of the services enabled. 

In order to build an image with `pi-gen` follow these steps:

```bash
# Clone the PiGen Repository
git clone https://github.com/RPi-Distro/pi-gen.git
# Clone the PiFex software repository
git clone https://github.com/voidstarsec/pifex-sw
# Copy the necessary PiFex files into the PiGen repository
# First, copy the config file
cp pifex-sw/pi-gen/pifex-config pi-gen/
# Copy the stage 1 files
cp pifex-sw/pi-gen/stage1/00-boot-files/files/config.txt pi-gen/stage1/00-boot-files/files
cp pifex-sw/pi-gen/stage1/00-boot-files/files/cmdline.txt pi-gen/stage1/00-boot-files/files
# Copy the stage 2 files
cp pifex-sw/pi-gen/stage2/01-sys-tweaks/00-patches/07-resize-init.diff pi-gen/stage2/01-sys-tweaks/00-patches/
# Copy the stage 3 files
cp pifex-sw/pi-gen/stage3/00-packages pi-gen/stage3/00-install-packages/
cp pifex-sw/pi-gen/stage3/01-run.sh pi-gen/stage3/00-install-packages/
# Copy the pifex-sw directory to stage3
mkdir pi-gen/stage3/00-install-packages/files/pifex/
cp -r pifex-sw pi-gen/stage3/00-install-packages/files/pifex/
cd pi-gen
./build-docker.sh -c pifex-config
```