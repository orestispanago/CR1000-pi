import serial


def serial_port():
    # Faster than CR1000.from_url() on raspberry
    # use port=None to create a serial port object without opening the underlying port
    # Found here: https://github.com/LionelDarras/PyCampbellCR1000/issues/21
    ser = serial.Serial(
        port=None,
        baudrate=115200,
        timeout=2,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=1,
    )
    ser.port = "/dev/ttyUSB0"
    return ser
