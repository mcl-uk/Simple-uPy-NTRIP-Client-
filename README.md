# Simple uPy NTRIP Client
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
   output via UART#1 tx mapped to IO33, the Airlift's 'BUSY' pin. Use its TxD, RxD,
   /RST & IO0 pins to flash & program the unit - but once set up you just need GND, 5v
   and the 'BUSY' pin for your RTCM data stream output.

   I like the Airlift module for embedded projects because, unlike most ESP dev
   boards, it does not waste space and power with a built-in USB-to-serial adapter.
 
   https://www.adafruit.com/product/4201

   The down side is that flashing/programming/debugging does require an external adapter,
   suitable FTDI/CP2102/CH340 units are widely available and fine if you're happy to
   manually sequence the RST and IO0 pins. But for smarter, hassle-free flashing with
   ESPTool an adapter with RTS & DTR outputs (RTS connects to ESP32_RST/EN & DTR to
   ESP32_IO0) may be worth the investment.  _BUT_ to be able to use the _same_ adapter
   for subsequent software dev work with tools like Thonny or Ampy it should also
   incorporate Nodemcu-32s's DTR/RTS mod, see the USBToTTL schematics here:

   https://docs.ai-thinker.com/_media/esp32/docs/nodemcu-32s_product_specification.pdf
   
   Note in particular VT1,VT2,C1 & the two 12K resistors. The modification circumvents
   the situation where both DTR and RTS are asserted low by default during virtual
   comm port driver initialisation on a host PC thus causing the ESP32 to be held in
   reset. Meanwhile, critically, the presence of C1 allows ESPTool to put the device
   into bootloader mode despite the prevention of static simultaneous low states on
   DTR & RTS. Such modified adapters are hard to find (I built my own) but here's an
   example:

   https://kjdelectronics.com/products/capuf-esp32-programmer

   Note the helpful diagram showing the 6-wire interface to the ESP32.

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

 Change log:
 
   14-08-24 v0.1 Initial working version
   
   15-08-24 v0.2 Added watchdog for RTCM data stream & added optional confidence LED 

