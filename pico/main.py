import network
import rp2
from time import sleep_ms
from machine import SPI, Pin
from i2s_wav import play_wav_file
from sdcard import SDCard
import os

from stream_file_to_sd import stream_to_file

# Set up SD card
print("=== Initializing SD Card ===")
spi = SPI(1,
          sck=Pin(10),
          mosi=Pin(11),
          miso=Pin(12)
)

try:
    sd = SDCard(spi, Pin(13, Pin.OUT))
    sd.init_spi(5_000_000)
    os.mount(sd, "/sd", readonly=False)
    print("=== SD Card initialized ===")
except e:
    play_wav_file("no-sdcard.wav")
    raise e

# Set up WiFi
print("=== initializing WiFi ===")
rp2.country("NL")

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

while not wlan.isconnected():
    wlan.connect("My WiFi is better than yours", "@L#X@ND#R&m1r12m")
    max_wait: int = 60
    while max_wait > int(0):
        if wlan.status() < 0 or wlan.status() >= 3:
            break

        max_wait -= 1
        print('waiting...')
        sleep_ms(1000)

    if wlan.status() is not 3:
        print(f"connection failed [{wlan.status()}]")
    else:
        print('connected')
        status = wlan.ifconfig()
        print(status)

# url = "https://www2.cs.uic.edu/~i101/SoundFiles/ImperialMarch60.wav"
# url = "https://www2.cs.uic.edu/~i101/SoundFiles/taunt.wav"
# url = "http://fox.home.karel-kroeze.nl/music.wav"
url = "http://fox.home.karel-kroeze.nl/no-internet.wav"
file = "/sd/%s" % url.split("/")[-1]
print(url, file)

# stream_to_file("no-sdcard.wav",
#                "http://fox.home.karel-kroeze.nl/no-sdcard.wav")
# play_wav_file("no-sdcard.wav")
