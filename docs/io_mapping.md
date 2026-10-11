# Virtual I/O

Authoritative ordered mapping: plc/io_mapping/signals.json.
Frame: little-endian 4-byte MHF1 magic, uint32 sequence, 64 IEEE-754 float32 values, 264 bytes.
PLC UDP bind 127.0.0.1:15020. One client only. Incoming finite values are copied to IEC REAL
globals in retrieve; outputs are copied after ST executes. Freshness and communication age
are assigned by C, not trusted from the packet. Duplicate sequence returns cached reply.
Client retries three times; its sequence starts from wall-clock milliseconds modulo uint32.
After >500 ms without a fresh frame, a different client UDP source port can establish a new
sequence. PLC timeout alarm remains latched until recovery/reset. At sequence wrap within one
client session, restart the runtime. Only one client may be used at a time; arbitration and
authentication are not implemented. This localhost prototype is not a production fieldbus.

Boolean conventions: 0 false, 1 true. Mode 1 manual, 2 auto, 3 single, 4 pause, 5 fault.
The machine model owns positions, product sensor, mark/home, film end, collision/jam and
package acknowledgements. HMI owns button pulses and requested recipe/mode.
ST owns enables, axis targets, jaw phase, cutter pulse, counters and latched alarms.
Physical I/O can implement the same semantic mapping in a different transport adapter.

Guard/E-stop fields are **simulation functional inputs**. Future safety-rated stop circuits,
drive STO, heater isolation and blade guarding must be independent of this PC/UDP link.
Modbus TCP is supported by Beremiz in general, but Rev A uses the separately verified adapter;
Modbus runtime integration is not claimed.
