# Simple-uPy-NTRIP-Client-
A very simple micropython ntrip client nominally for use on an ESP32

Inspired by:
  https://github.com/jcmb/NTRIP/blob/master/NTRIP%20Client/NtripClient.py

Description:
  Receives the RTCM binary data stream from the specified NTRIP caster and routes it to
  UART#1 at the specified baud-rate. Simply set the operating parameters to suit your
  application and save to your target device as main.py.

  It's assumed that micropython is installed on the ESP32 and that a Wifi internet
  connection has already been established by boot.py. Example boot.py code which sets
  up Wifi is widely available.

Notes:
  This code has been tested on an Adafruit Airlift ESP32 WROOM-32E module but should
  work on any other ESP32 (or non-ESP32) microPython platform. Debug data is available
  on the module's 'TxD' pin (UART#0 tx @115200Bd) and the received RTCM serial data is
  output via UART#1 tx mapped to IO33, the module's 'BUSY' pin. Use the module's TxD,
  RxD, RST/EN & IO0 pins to flash & program the unit - once set up, no other IO pins
  need connecting.

  I like the Airlift module for embedded projects because, unlike most ESP dev
  boards, it does not waste space and power on a built-in USB-to-serial adapter.
  However flashing/programming/debugging does require an external adapter, suitable
  FTDI/CP2102/CH340 devices are widely available and fine if you're happy to manually
  sequence the RST and IO0 pins. But for smarter, hassle-free flashing with ESPTool
  an adapter with RTS and DTR outputs is required (which rules out FTDI units).
  However, to be able to use the same adapter with tools like Thonny or Ampy it must
  also incorporate Nodemcu-32s's DTR/RTS mod, see the USBToTTL schematics here:
  https://docs.ai-thinker.com/_media/esp32/docs/nodemcu-32s_product_specification.pdf
  Note in particular VT1,VT2,C1 & the two 12K resistors, it's a bit wierd and rather
  nasty but it works!
  Such modified adapters are hard to find (I built my own) but here's an example:
  https://kjdelectronics.com/products/capuf-esp32-programmer
  Note the helpful diagram showing the 6-wire interface to the ESP32 module.

  Once flashed with the micropython binary you can continue to use the adapter with
  a tool such as Thonny to copy your boot.py and main.py files over to the ESP32.
  And when they're in place the unit will just auto-run, on its own, at power-up.

  Normally, by default, UART#1's recommended pins would be 10,9 (tx,rx) but if using
  an Adafruit Airlift module pls set UART#1's pins to 33,9 so as to use the 'BUSY' pin
  (pin8 on the 12 way connector) for serial data output, which will be at 3.3v.
  If using other, more conventially wired dev boards stick to the 10,9 config.

  The baud rate for UART#1 (the RTCM data stream) is set at 115200 which is pretty
  much the optimal rate for this application bearing in mind the per-second quantity
  of RTCM data, the UART driver's buffer size and the loop's sleep time. Changing it
  might have unexpected consequences, take care.

  Observed power consumption averages at around 40mA with no more than 300mA peaks,
  measured at 5V on a WROOM-32E based Adafruit Airlift module.
