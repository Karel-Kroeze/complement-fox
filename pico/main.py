import network
import rp2
import os
# import asyncio

from time import sleep_ms, ticks_ms, time
from machine import PWM, SPI, Pin
from helpers import get_config, pulse_pwm
from i2s_audio import play_wav_file
from messages import check_new_messages, num_received_messages, play_new_message
from sdcard import SDCard
from http import request, stream_to_file

# Set up button
btn = Pin(6, Pin.IN, pull=Pin.PULL_UP)
btn_led = PWM(Pin(7, Pin.OUT))
btn_led.freq(100)

button_debounce_timer = ticks_ms()
button_pressed = False


def btn_handler(_) -> None:
    global button_pressed, button_debounce_timer

    if ticks_ms() - button_debounce_timer > 250:
        button_debounce_timer = ticks_ms()
        button_pressed = True


btn.irq(btn_handler, Pin.IRQ_FALLING)

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
except Exception as e:
    play_wav_file("no-sdcard.wav")
    raise e

# Set up WiFi
print("=== initializing WiFi ===")
rp2.country("NL")

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

wifi = get_config("/sd/wifi.txt")
try:
    print("ssid:", wifi['ssid'])
    print("password:", len(wifi['password']) * '*')
    print()
except ValueError as err:
    print(err)
    while True:
        play_wav_file("/sd/no-internet.wav")
        sleep_ms(2000)


while not wlan.isconnected():
    wlan.connect(wifi['ssid'], wifi['password'])
    max_wait: int = 60
    print("waiting for connection...", end="")
    while max_wait > int(0):
        if wlan.status() < 0 or wlan.status() >= 3:
            print()
            break

        max_wait -= 1
        print(".", end="")
        pulse_pwm(btn_led)
        sleep_ms(500)

    if wlan.status() is not 3:
        print(f"connection failed [{wlan.status()}]")
    else:
        print('connected')
        status = wlan.ifconfig()
        print(status)


last_check = 0
last_pulse = 0


def main() -> None:
    global button_pressed, last_check, last_pulse

    print("=== MAIN ===")
    print("starting main loop...\n")
    pulse_pwm(btn_led, 5, 300, 30)

    while True:
        if button_pressed:
            button_pressed = False
            if num_received_messages() > 0:
                play_new_message()
            else:
                # todo random complement
                print("todo: random complement")

        time_since_last_pulse = time() - last_pulse
        if not button_pressed and num_received_messages() > 0 and time_since_last_pulse > 2:
            pulse_pwm(btn_led, num_received_messages())
            last_pulse = time()

        time_since_last_check = time() - last_check
        if not button_pressed and time_since_last_check > 10:
            check_new_messages()
            last_check = time()

        sleep_ms(100)


main()
