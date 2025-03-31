import sys
import os
import argparse
import struct
import time
import socket
import itertools

class OpenOcd:
    COMMAND_TOKEN = '\x1a'
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.tclRpcIp       = "127.0.0.1"
        self.tclRpcPort     = 6666
        self.bufferSize     = 4096
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __enter__(self):
        self.sock.connect((self.tclRpcIp, self.tclRpcPort))
        return self

    def __exit__(self, type, value, traceback):
        try:
            self.send("exit")
        finally:
            self.sock.close()

    def send(self, cmd):
        """Send a command string to TCL RPC. Return the result that was read."""
        data = (cmd + OpenOcd.COMMAND_TOKEN).encode("utf-8")
        if self.verbose:
            print("<- ", data)

        self.sock.send(data)
        return self._recv()

    def _recv(self):
        """Read from the stream until the token (\x1a) was received."""
        data = bytes()
        while True:
            chunk = self.sock.recv(self.bufferSize)
            data += chunk
            if bytes(OpenOcd.COMMAND_TOKEN, encoding="utf-8") in chunk:
                break
        if self.verbose:
            print("-> ", data)
        data = data.decode("utf-8").strip()
        data = data[:-1] # strip trailing \x1a
        return data

    def writeWord(self,address,val):
        write = self.send(f"mww phys 0x{address:02x} 0x{val:02x}  1")

    def writeByte(self,address,val):
        write = self.send(f"mwb phys 0x{address:02x} 0x{val:02x}  1")

    def readByte(self,address):
        mem_array = self.send(f"read_memory 0x{address:02x} 8 1 phys")
        int_vals = []
        for val in mem_array.split():
            int_vals.append(int(val,16))
        return int_vals


    def readDword(self,address):
        print(f"read_memory 0x{address:02x} 32 1  phys")
        mem_array = self.send(f"read_memory 0x{address:02x} 32 1 phys")
        int_vals = []
        for val in mem_array.split():
            int_vals.append(int(val,16))
        return int_vals

    def readDword2(self,address):
        mem_array = self.send(f"mdw phys 0x{address:02x} 1")
        #print(mem_array)
        vals = mem_array.split(":")
        target_val = vals[1].strip("")
        int_val = int(target_val,16)
        #print(hex(int_val))
        #int_val = int(vals[1],16)
        return int_val

# Processor specific variables
FMC_BASE = 0x40020000
FLSTS  =                      FMC_BASE+0x00000000  # Flash status register                                      */
FLOPMD1 =                     FMC_BASE+0x00000004  # Flash operation mode register 1                            */
FLOPMD2  =                    FMC_BASE+0x00000008  # Flash operation mode register 2                            */
FLERMD    =                   FMC_BASE+0x0000000C  # Flash erase mode register                                  */
FLCERCNT  =                   FMC_BASE+0x00000010  # Flash chip erase control register                          */
FLSERCNT  =                   FMC_BASE+0x00000014  # Flash sector erase control register                        */
FLNVSCNT  =                   FMC_BASE+0x00000018  # Flash address setup time (Tnvs) control register           */
FLPROCNT  =                   FMC_BASE+0x0000001C  # Flash program control register                             */
FLPROT    =                   FMC_BASE+0x00000020  # Flash protect control register                             */
FLPRVCNT  =                   FMC_BASE+0x00000038  # Flash program recovery time (Trcv) control register        */
FLERVCNT  =                   FMC_BASE+0x0000003C  # Flash erase recovery time (Trcv) control register          */

def erase_flash(ocd,addr):
    ocd.writeWord(FLERMD,0x8)
    ocd.writeWord(FLPROT, 0xF1)
    ocd.writeWord(FLOPMD1, 0x55)
    ocd.writeWord(FLOPMD2, 0xAA)
    ocd.writeWord(addr, 0xFFFFFFFF)
    while(ocd.readByte(FLSTS)[0] != 1):
        time.sleep(.0001)
    ocd.writeWord(FLSTS, 1)
    ocd.writeWord(FLERMD,0)
    ocd.writeWord(FLPROT, 0xF0)
    ocd.send("reset halt")
    return

'''
Program the flash 0x200 bytes at a time
'''
g_start_addr = 0
def program_flash(ocd,prog_data,start_addr):
    global g_start_addr
    ocd.writeWord(FLPROT,0xF1)
    for x in range(0,len(prog_data)):
        print(f"Start Addr: {g_start_addr:X} Programming word {x:X} of {len(prog_data):X} - {prog_data[x]:X}")
        ocd.writeByte(FLOPMD1,0xAA)
        ocd.writeByte(FLOPMD2,0x55)
        ocd.writeByte(g_start_addr,prog_data[x])
        while(ocd.readByte(FLSTS)[0] != 1):
            time.sleep(.0001)
        ocd.writeByte(FLSTS,1)
        g_start_addr += 1
    ocd.writeByte(FLPROT,0xF0)
    return

def status_reg(ocd):
    ocd.writeByte(FLPROT,0xF1)
    ocd.writeByte(FLOPMD1,0xAA)
    ocd.writeByte(FLOPMD2,0x55)
    ocd.writeByte(FLSTS,1)
    ocd.writeByte(FLPROT,0xF0)
    return

def clear_stack(ocd,start_addr,end_addr):
    for x in range(start_addr,end_addr,4):
        ocd.writeWord(x,0)

FLASH_SIZE = 64*1024
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BAT32 OpenOCD Reflash Utility")
    parser.add_argument("-o","--operation",action='store',type=str,help="Operation to perform, e = erase, f = flash",required=True)
    parser.add_argument("-f","--file",action='store', type=str,help="File to reflash")
    args = parser.parse_args()
    prog_data = []
    with OpenOcd() as ocd:
        if args.operation == 'f':
            if args.file != None:
                with open(args.file,'rb') as infile:
                    data = bytes(infile.read())
            # Erase target flash memory
            erase_flash(ocd,0)
            for page in range(0,FLASH_SIZE,0x200):
                pdat = data[page:page+0x200]
                program_flash(ocd,pdat,page)
            status_reg(ocd)
            clear_stack(ocd,0x20000000,0x20002000)
        elif args.operation == 'e':
            print("Erasing flash, please wait ... ")
            erase_flash(ocd,0)
