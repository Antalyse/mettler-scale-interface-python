# Python Interface for Mettler-Toledo Scales

### IMPORTANT NOTE: USB and Serial connections are not testet. Only ethernet has been confirmed to work. 





A lightweight, robust Python class for interacting with Mettler Toledo laboratory and industrial scales. This module uses the **MT-SICS** (Mettler Toledo Standard Interface Command Set) protocol to communicate with your scale over Serial, USB, or Ethernet interfaces.

Features
--------

-   **Multi-Interface Support:** Connect via standard RS232 Serial, USB-to-Serial, or direct Ethernet/TCP.

-   **Custom Stability Polling:** Includes a robust `getCurrentWeight` method that continuously polls the scale (using the `SI` command) until the weight remains mathematically stable for a user-defined period, bypassing the scale's built-in (and sometimes overly strict) stability criteria.

-   **Basic Commands:** Built-in methods for taring and retrieving formatted weight data.

Requirements
------------

The script relies heavily on Python's standard library (`socket`, `time`), but you will need the `pyserial` package if you plan to use Serial or USB connections.

Bash

```
pip install pyserial

```

Usage Examples
--------------

Make sure `mettlerscale.py` is in your project directory or Python path.

### 1\. Connecting via Serial / USB

This example demonstrates how to connect to a scale via a COM port, tare it, and wait for a stable reading.

Python

```
from mettlerscale import MettlerScale

# Initialize the scale on COM3 (Windows) or /dev/ttyUSB0 (Linux/Mac)
scale = MettlerScale(interface='serial', port='COM3', baudrate=9600)

scale.connect()

if scale.connection:
    # Zero out the scale
    print("Taring the scale...")
    scale.tare()

    # Wait until the weight is stable for 3 continuous seconds
    # It will time out if stability isn't reached within 30 seconds
    print("Please place the item on the scale.")
    weight, unit = scale.getCurrentWeight(stable_time_seconds=3.0, max_wait_timeout=30)

    if weight is not None:
        print(f"Final Measurement: {weight} {unit}")
    else:
        print("Failed to get a stable reading.")

    scale.disconnect()

```

### 2\. Connecting via Ethernet (TCP/IP)

If your scale is equipped with an Ethernet port or connected to a terminal server, you can connect directly via IP.

Python

```
from mettlerscale import MettlerScale

# Initialize the scale using its IP address.
# Mettler Toledo Ethernet modules typically default to TCP port 8000.
scale = MettlerScale(interface='ethernet', ip='192.168.1.150', tcp_port=8000)

scale.connect()

if scale.connection:
    # Quickly grab a weight, requiring only 1 second of stability
    weight, unit = scale.getCurrentWeight(stable_time_seconds=1.0)

    print(f"Recorded Weight: {weight} {unit}")

    scale.disconnect()

```

API Reference
-------------

### `MettlerScale(interface, port, baudrate, ip, tcp_port, timeout)`

**Constructor parameters:**

-   `interface` (str): `'serial'`, `'usb'`, or `'ethernet'`.

-   `port` (str): The serial port (e.g., `'COM3'` or `'/dev/ttyS0'`). Required for serial/usb.

-   `baudrate` (int): The baud rate for the serial connection. Default is `9600`.

-   `ip` (str): The IP address of the scale. Required for ethernet.

-   `tcp_port` (int): The TCP port for network communication. Default is `8000`.

-   `timeout` (int): Connection timeout in seconds. Default is `2`.

### `connect()`

Establishes the hardware or socket connection based on the parameters provided during initialization.

### `disconnect()`

Safely closes the active Serial or TCP connection.

### `tare()`

Sends the `T` command to zero the scale. Returns `True` if successful, `False` if the scale rejects the command (usually due to high instability during the tare attempt).

### `getCurrentWeight(stable_time_seconds, max_wait_timeout=30)`

Polls the scale rapidly using the `SI` (Send Immediate) command.

-   `stable_time_seconds` (float): How long the weight must remain unchanged (within a variance of `< 0.0001`) to be considered valid.

-   `max_wait_timeout` (int): Maximum time in seconds to wait for stability before giving up and returning `None`.

-   **Returns:** A tuple of `(weight_float, unit_string)`, or `(None, None)` on timeout.

---

License
-------------
This Interface is licensed under the MIT License.


