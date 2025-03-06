from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import time
import telnetlib
import subprocess
import threading
import queue
import asyncio

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)
import os

# Telnet Configuration
TELNET_HOST = "127.0.0.1"
TELNET_PORT = 4444
TIMEOUT = 10

# Queue for GDB Output
gdb_output_queue = queue.Queue()

# Global GDB Process
gdb_process = None

def gdb_reader():
    """Read output from the GDB process and enqueue it."""
    global gdb_process
    while gdb_process and gdb_process.poll() is None:
        line = gdb_process.stdout.readline()
        if line:
            gdb_output_queue.put(line)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/launch_openocd', methods=['POST'])
def launch_openocd():
    """Launch OpenOCD with the selected files."""
    try:
        # Get the list of selected files from the client
        files = request.json.get('files', [])
        if not files:
            return jsonify({"status": "error", "message": "No files selected."}), 400

        # Construct the OpenOCD command
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

        # Optionally, capture output (asynchronous monitoring can be implemented)
        stdout, stderr = process.communicate()

        # Return success or error response
        #if process.returncode == 0:
        return jsonify({"status": "success", "message": "OpenOCD launched successfully.", "output": stdout})
        #else:
        #    return jsonify({"status": "error", "message": stderr}), 500

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    

@socketio.on('memory_read')
def memory_read(data):
    """Handle memory examination via mdw command with a size."""
    address = data.get('address')
    size = data.get('size', 1)  # Default size is 1 word if not provided

    if not address:
        emit('memory_output', {'data': 'Error: Address not provided.'})
        return

    try:
        with telnetlib.Telnet(TELNET_HOST, TELNET_PORT, timeout=TIMEOUT) as tn:
            # Send the mdw command for the specified size
            command = f"mdw {address} {size}\n"
            tn.write(command.encode('utf-8'))
            output = tn.read_until(b">", timeout=1).decode('utf-8')
            output = tn.read_until(b">", timeout=1).decode('utf-8')
            # Emit the response back to the client
            emit('memory_output', {'data': output})
    except Exception as e:
        emit('memory_output', {'data': f"Error: {str(e)}"})
@socketio.on('connect')
def connect():
    emit('message', {'data': 'Connected to the interactive terminal!'})

@socketio.on('command_telnet')
def handle_telnet_command(data):
    command = data.get('command', '')
    try:
        with telnetlib.Telnet(TELNET_HOST, TELNET_PORT, timeout=TIMEOUT) as tn:
            tn.write(command.encode('utf-8') + b'\n')
            output = tn.read_until(b">", timeout=1).decode('utf-8')
            output = tn.read_until(b">", timeout=10).decode('utf-8')

            emit('telnet_output', {'data': output})
    except Exception as e:
        emit('telnet_output', {'data': f"Error: {str(e)}"})

@app.route('/search', methods=['GET'])
def search_files():
    """Search for files in the server."""
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    
    base_dir = "/usr/share/openocd/scripts/"  # Base directory to search (customize as needed)
    matches = []
    for root, dirs, files in os.walk(base_dir):
        for name in files + dirs:
            if query.lower() in name.lower():
                matches.append(os.path.join(root, name))
                if len(matches) >= 100:  # Limit to 10 matches for performance
                    break
        if len(matches) >= 100:
            break
    return jsonify(matches)

@socketio.on('command_gdb')
def handle_gdb_command(data):
    global gdb_process
    command = data.get('command', '')
    if gdb_process and gdb_process.poll() is None:
        print(command)
        foo = str(command) + '\r\n'
        print(type(foo))
        gdb_process.stdin.write(foo)
        gdb_process.stdin.flush()
        time.sleep(.25)
        # Collect output from the queue
        output = ""
        while not gdb_output_queue.empty():
            output += gdb_output_queue.get()
        print("Command Output" + output)
        emit('gdb_output', {'data': output})
    else:
        emit('gdb_output', {'data': 'Error: GDB process is not running.'})

@socketio.on('start_gdb')
def start_gdb():
    print("Starting GDB!")
    global gdb_process
    if gdb_process and gdb_process.poll() is None:
        emit('gdb_output', {'data': 'GDB is already running.'})
        return

    try:
        gdb_process = subprocess.Popen(
            ["gdb-multiarch"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=1,
            universal_newlines=True
        )
        threading.Thread(target=gdb_reader, daemon=True).start()
        emit('gdb_output', {'data': 'GDB started successfully.\n'})
        get_initial_info()

    except Exception as e:
        emit('gdb_output', {'data': f"Error starting GDB: {str(e)}"})

def get_initial_info():
    time.sleep(.25)
    output = ''
    while not gdb_output_queue.empty():
        output += gdb_output_queue.get()
    print(output)
    
@socketio.on('stop_gdb')
def stop_gdb():
    global gdb_process
    if gdb_process:
        gdb_process.terminate()
        gdb_process = None
        emit('gdb_output', {'data': 'GDB stopped successfully.'})
    else:
        emit('gdb_output', {'data': 'GDB is not running.'})

if __name__ == '__main__':
    socketio.run(app, allow_unsafe_werkzeug=True,debug=True,host="0.0.0.0")
