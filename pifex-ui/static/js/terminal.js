$(document).ready(function () {
    const socket = io();


    // Memory Panel
    const memoryOutputPanel = document.getElementById('memory-output');
    const memoryAddressInput = document.getElementById('memory-address');
    const memorySizeInput = document.getElementById('memory-size');
    const memoryReadButton = document.getElementById('read-memory');

    function appendToMemoryOutput(message) {
        const outputLine = document.createElement('div');
        outputLine.textContent = message;
        memoryOutputPanel.appendChild(outputLine);
        memoryOutputPanel.scrollTop = memoryOutputPanel.scrollHeight;
    }

    // Handle memory read response
    socket.on('memory_output', (data) => {
        appendToMemoryOutput(data.data);
    });

    // Send memory read request
    memoryReadButton.addEventListener('click', () => {
        const address = memoryAddressInput.value.trim();
        const size = memorySizeInput.value.trim();

        if (!address) {
            appendToMemoryOutput('Error: Address is empty.');
            return;
        }

        if (!size || isNaN(size) || size <= 0) {
            appendToMemoryOutput('Error: Invalid size. Please enter a positive number.');
            return;
        }

        appendToMemoryOutput(`Reading ${size} words from address: ${address}`);
        socket.emit('memory_read', { address, size: parseInt(size, 10) });
    });
    // GDB Terminal
    const gdbTerminal = document.getElementById('gdb-terminal');
    const gdbInput = document.getElementById('gdb-input');
    const startGdbButton = document.getElementById('start-gdb');
    const stopGdbButton = document.getElementById('stop-gdb');

    function appendToGdbTerminal(message) {
        const codeBlock = document.createElement('code');
        codeBlock.className = 'language-c'; // Use the appropriate language class for GDB (e.g., C-like syntax)
        codeBlock.textContent = message.trim();
        gdbTerminal.appendChild(codeBlock);
        gdbTerminal.appendChild(document.createElement('br'));
        Prism.highlightElement(codeBlock); // Highlight the code block
        gdbTerminal.scrollTop = gdbTerminal.scrollHeight;
    }

    socket.on('gdb_output', (data) => {
        appendToGdbTerminal(data.data);
    });

    startGdbButton.addEventListener('click', () => {
        socket.emit('start_gdb');
    });

    stopGdbButton.addEventListener('click', () => {
        socket.emit('stop_gdb');
    });

    gdbInput.addEventListener('keydown', (event) => {
        if (event.key === 'Enter') {
            const command = gdbInput.value.trim();
            if (command) {
                appendToGdbTerminal('(gdb) ' + command);
                socket.emit('command_gdb', { command });
            }
            gdbInput.value = '';
        }
    });

    // Telnet Terminal
    const telnetTerminal = document.getElementById('telnet-terminal');
    const telnetInput = document.getElementById('telnet-input');

    function appendToTelnetTerminal(message) {
        telnetTerminal.textContent += message + '\n';
        telnetTerminal.scrollTop = telnetTerminal.scrollHeight;
    }

    socket.on('telnet_output', (data) => {
        appendToTelnetTerminal(data.data);
    });

    telnetInput.addEventListener('keydown', (event) => {
        if (event.key === 'Enter') {
            const command = telnetInput.value.trim();
            if (command) {
                appendToTelnetTerminal('> ' + command);
                socket.emit('command_telnet', { command });
            }
            telnetInput.value = '';
        }
    });
});
