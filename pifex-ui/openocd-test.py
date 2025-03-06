import subprocess

files = ['/usr/share/openocd/scripts/interface/stlink.cfg']

openocd_command = ["openocd"]
for file in files:
    openocd_command += ['-f']
    openocd_command += [file]
print(openocd_command)
# Launch OpenOCD
process = subprocess.Popen(
    openocd_command,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    universal_newlines=True,
)

stdout, stderr = process.communicate()

# Return success or error response
if process.returncode == 0:
   print(stdout)
else:
    print(stderr)