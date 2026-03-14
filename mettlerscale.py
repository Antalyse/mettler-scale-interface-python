import serial
import socket
import time

class MettlerScale:
    def __init__(self, interface='serial', port=None, baudrate=9600, ip=None, tcp_port=8000, timeout=2):
        """
        Initializes the scale connection parameters.
        :param interface: 'serial', 'usb', or 'ethernet'
        :param port: COM port (e.g., 'COM3' or '/dev/ttyUSB0') for Serial/USB
        :param baudrate: Baud rate for Serial/USB
        :param ip: IP address for Ethernet
        :param tcp_port: TCP port for Ethernet (default usually 8000 for MT)
        :param timeout: Connection timeout in seconds
        """
        self.interface = interface.lower()
        self.port = port
        self.baudrate = baudrate
        self.ip = ip
        self.tcp_port = tcp_port
        self.timeout = timeout
        self.connection = None

    def connect(self):
        """Establishes the connection to the scale."""
        try:
            if self.interface in ['serial', 'usb']:
                if not self.port:
                    raise ValueError("Port must be specified for Serial/USB connections.")
                self.connection = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
                print(f"Connected via {self.interface.upper()} on {self.port}")
                
            elif self.interface == 'ethernet':
                if not self.ip:
                    raise ValueError("IP address must be specified for Ethernet connections.")
                self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.connection.settimeout(self.timeout)
                self.connection.connect((self.ip, self.tcp_port))
                print(f"Connected via ETHERNET to {self.ip}:{self.tcp_port}")
            else:
                raise ValueError("Unsupported interface. Use 'serial', 'usb', or 'ethernet'.")
        except Exception as e:
            print(f"Failed to connect: {e}")
            self.connection = None

    def disconnect(self):
        """Closes the connection."""
        if self.connection:
            self.connection.close()
            print("Connection closed.")

    def _send_receive(self, command):
        """Sends an MT-SICS command and returns the response."""
        if not self.connection:
            raise ConnectionError("Scale is not connected.")
            
        cmd_bytes = f"{command}\r\n".encode('ascii')
        
        if self.interface in ['serial', 'usb']:
            self.connection.write(cmd_bytes)
            return self.connection.readline().decode('ascii').strip()
            
        elif self.interface == 'ethernet':
            self.connection.sendall(cmd_bytes)
            # Read until newline character
            response = b""
            while not response.endswith(b"\n"):
                response += self.connection.recv(1)
            return response.decode('ascii').strip()

    def tare(self):
        """Sends the Tare command."""
        response = self._send_receive("T")
        if response.startswith("T S"):
            print("Tare successful.")
            return True
        print("Tare failed or scale unstable.")
        return False

    def getCurrentWeight(self, stable_time_seconds, max_wait_timeout=30):
        """
        Polls the scale until the weight remains unchanged for `stable_time_seconds`.
        :param stable_time_seconds: Seconds the weight must remain constant.
        :param max_wait_timeout: Max seconds to wait before giving up.
        """
        start_wait = time.time()
        stable_start = time.time()
        last_weight = None

        print(f"Waiting for weight to stabilize for {stable_time_seconds} seconds...")

        while (time.time() - start_wait) < max_wait_timeout:
            # "SI" is Send Immediate (returns weight even if scale thinks it's unstable)
            response = self._send_receive("SI")
            
            # Typical MT-SICS response: "S S    100.00 g" or "S D    100.00 g"
            parts = response.split()
            
            if len(parts) >= 4 and parts[0] == 'S':
                try:
                    current_weight = float(parts[2])
                    unit = parts[3]
                    
                    # Check if weight changed (allowing a tiny float comparison margin)
                    if last_weight is not None and abs(current_weight - last_weight) < 0.0001:
                        # Weight is the same as last check
                        elapsed_stable = time.time() - stable_start
                        if elapsed_stable >= stable_time_seconds:
                            print(f"Stable weight achieved: {current_weight} {unit}")
                            return current_weight, unit
                    else:
                        # Weight changed, reset the stability timer
                        stable_start = time.time()
                        last_weight = current_weight
                        
                except ValueError:
                    pass # Ignore parsing errors if scale sends junk

            # Small delay to prevent spamming the scale's processor
            time.sleep(0.1) 
            
        print("Timeout: Could not get a stable weight.")
        return None, None
