from time import sleep
from ulora import LoRa, ModemConfig, SPIConfig

def on_recv(payload):
#    print("From:", payload.header_from)
    print("Received:", payload.message.decode())  # Decode bytes to string
#    print("RSSI: {}; SNR: {}".format(payload.rssi, payload.snr))

RFM95_RST = 7
RFM95_SPIBUS = SPIConfig.rp2_0
RFM95_CS = 5
RFM95_INT = 6
RF95_FREQ = 433.0
RF95_POW = 20
CLIENT_ADDRESS = 1
SERVER_ADDRESS = 2

lora = LoRa(RFM95_SPIBUS, RFM95_INT, SERVER_ADDRESS, RFM95_CS, reset_pin=RFM95_RST, freq=RF95_FREQ, tx_power=RF95_POW, acks=True)

lora.on_recv = on_recv

lora.set_mode_rx()

while True:
    sleep(0.1)

