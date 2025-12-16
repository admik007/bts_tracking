from machine import Pin
import time, os, sdcard, sys, uos


# SPI configuration for SPI0
spi = machine.SPI(0,
                  baudrate=1_000_000,
                  polarity=0,
                  phase=0,
                  bits=8,
                  firstbit=machine.SPI.MSB,
                  sck=machine.Pin(18),
                  mosi=machine.Pin(19),
                  miso=machine.Pin(16))

cs = machine.Pin(17, machine.Pin.OUT)

try:
 sd = sdcard.SDCard(spi, cs)
 vfs = uos.VfsFat(sd)
 uos.mount(vfs, "/sd")
 print("SD card mounted.")
 SDCARD = True
except Exception as e:
 print("Failed to mount SD card:", e)
 SDCARD = False
 sys.exit()
