# Mad Scientist

## PIR input test

`test_pir.py` displays the raw digital output of an HC-SR501-compatible PIR
every 0.2 seconds, with a timestamp. It does not filter or debounce the signal.

### Wiring

With the Raspberry Pi powered off, connect:

- PIR OUT to **BCM GPIO 6**, physical header pin **31**.
- PIR GND to a Pi ground, for example physical pin **6**.
- PIR VCC to the module's specified supply. Standard HC-SR501 modules normally
  use the Pi's **5 V** supply, for example physical pin **2**.

Check your particular module's pin labels and supply requirements. The OUT
signal must be **3.3 V logic** for the Pi GPIO; never connect 5 V to GPIO 6.

### Running

Use a Raspberry Pi environment with the `RPi.GPIO` module available:

```bash
python3 test_pir.py
```

- Allow approximately **30-60 seconds** after sensor power-up for stabilization.
  The script prints immediately so startup fluctuations are visible.
- `PIR=1` means the sensor output is HIGH (motion signaled).
- `PIR=0` means the sensor output is LOW (idle output).
- With the jumper in **L** (non-retriggering) mode, output can drop LOW and
  enter a blocking interval even if someone is still moving. It is not a
  continuous presence or distance measurement.
- Press **Ctrl+C** to stop. The script releases only GPIO 6, leaving unrelated
  GPIO channels alone.

Hardware-free tests, run from this directory:

```bash
python3 -m unittest discover -s tests -p test_pir_input.py
```