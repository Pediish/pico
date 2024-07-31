from machine import UART, Pin
import time
from ulora import LoRa, ModemConfig, SPIConfig

uart = UART(0, baudrate=19200, tx=Pin(16), rx=Pin(17))

RFM95_RST = 7
RFM95_SPIBUS = SPIConfig.rp2_0
RFM95_CS = 5
RFM95_INT = 6
RF95_FREQ = 433.0
RF95_POW = 20
CLIENT_ADDRESS = 1
SERVER_ADDRESS = 2

lora = LoRa(RFM95_SPIBUS, RFM95_INT, CLIENT_ADDRESS, RFM95_CS, reset_pin=RFM95_RST, freq=RF95_FREQ, tx_power=RF95_POW, acks=True)

def read_holding_registers(slave, start_register, count):
    request = bytearray(8)
    request[0] = slave                
    request[1] = 0x03                 
    request[2] = (start_register >> 8) & 0xFF  
    request[3] = start_register & 0xFF        
    request[4] = (count >> 8) & 0xFF           
    request[5] = count & 0xFF                 
    crc = calculate_crc(request[:-2])
    request[6] = crc & 0xFF
    request[7] = (crc >> 8) & 0xFF

    uart.write(request)
    time.sleep(0.1)
    
    response = uart.read()
    
    if response:
        if len(response) >= 5:
            if response[0] == slave and response[1] == 0x03:
                register_values = []
                byte_count = response[2]
                if len(response) >= 3 + byte_count:
                    for i in range(3, 3 + byte_count, 2):
                        value = (response[i] << 8) | response[i + 1]
                        register_values.append(value)
                    return register_values
                else:
                    print("Incomplete response received")
            else:
                print("Invalid slave address or function code in response")
        else:
            print("Response too short")
    else:
        print("No response received")
    return None

def calculate_crc(data):
    crc = 0xFFFF
    for pos in data:
        crc ^= pos
        for _ in range(8):
            if (crc & 1) != 0:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return crc

def save_to_file(filename, data):
    with open(filename, 'w') as file:
        for value in data:
            file.write(f"{value}\n")

def send_via_lora(data, address):
    lora.send_to_wait(data, address)
    print("Data sent via LoRa")

def format_data(register_values):
    return ','.join(map(str, register_values))

start_register = 0
count = 12
slave = 9

while True:
    register_values = read_holding_registers(slave, start_register, count)
    if register_values:
        print("Register values:", register_values)
        save_to_file('register_values.txt', register_values)
        formatted_data = format_data(register_values)
        send_via_lora(formatted_data, SERVER_ADDRESS)
    else:
        print("Failed to read registers")
    time.sleep(5)

