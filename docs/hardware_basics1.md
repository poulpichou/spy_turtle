# Hardware & Programming Basics

A practical introduction to electronics, communication protocols, computer hardware, networks and programming concepts.

The goal of this document is to understand the basic concepts behind modern embedded systems, robotics, IoT devices and computers.

---

# 1. Electronics Fundamentals

Electronics is based on controlling electrical signals to process information or create physical actions.

## 1.1 Voltage, Current and Power

**Voltage (V)** is the electrical potential difference that pushes electrons through a circuit.
**Current (A)** is the amount of electrical flow through a component.
**Power (W)** represents the energy consumed by a device.

Formula:

```text
Power = Voltage × Current

P(W) = V(V) × I(A)
```

Example:

```text
5V × 2A = 10W
```

A power source must provide:

* The correct voltage.
* Enough current for all connected components.

## 1.2 Digital and Analog Signals

Electronic systems communicate using electrical signals.

### Analog Signals

An analog signal is continuous and can take any value inside a range.

Examples:

* Microphone signals.
* Temperature sensors.
* Traditional audio signals.

Example:

```text
0V → 1.2V → 2.7V → 3.3V
```

### Digital Signals

A digital signal uses discrete values.

Most electronic systems use:

```text
LOW  = 0V
HIGH = 3.3V or 5V
```

Digital signals are easier for computers to process because they are less sensitive to noise.

## 1.3 GPIO - General Purpose Input/Output

GPIO pins are programmable electrical connections available on many computers and microcontrollers.

A GPIO can work as an input or an output.

### Input

The processor reads information from the outside world.

Examples:

* Buttons.
* Sensors.
* Switches.

```text
Sensor → GPIO → Processor
```

### Output

The processor controls an external device.

Examples:

* LEDs.
* Relays.
* Motor control signals.

```text
Processor → GPIO → Device
```

GPIO pins usually operate at 3.3V or 5V logic levels.

Connecting an incorrect voltage can permanently damage hardware.

---

# 2. Communication

Electronic components need communication protocols to exchange information.

A communication protocol defines:

* How data is formatted.
* How devices synchronize.
* How information is transmitted.

## 2.1 Communication Concepts

### Serial Communication

Serial communication sends data one bit at a time through a communication channel.

```text
10110010

↓

1 → 0 → 1 → 1 → 0 → 0 → 1 → 0
```

Advantages:

* Requires few wires.
* Simple hardware.
* Works well over distances.

Examples:

* UART.
* SPI.
* I2C.

### Parallel Communication

Parallel communication sends multiple bits simultaneously using several wires.

```text
Bit 1 ─────────
Bit 2 ─────────
Bit 3 ─────────
Bit 4 ─────────
```

Advantages:

* Can be very fast.

Disadvantages:

* Requires many wires.
* Synchronization becomes difficult.

### Synchronous Communication

A synchronous protocol uses a shared clock signal.

One device generates timing pulses so all devices know when to read data.

```text
Clock:
_|-|_|-|_|-|_

Data:
__--___--__--
```

Examples:

* SPI.
* I2C.
* I2S.

### Asynchronous Communication

An asynchronous protocol does not use a shared clock.

Both devices agree beforehand on communication parameters, especially speed.

Example:

* UART.

### Bus

A bus is a shared communication pathway connecting several electronic devices.

A bus can transport:

* Data.
* Clock signals.
* Addresses.
* Control information.

```text
              CPU
               |
       ----------------
       |       |      |
     OLED   Sensor  Memory
```

## 2.2 Communication Protocols

### I2C - Inter-Integrated Circuit

I2C is a synchronous serial communication protocol designed for connecting multiple low-speed devices.

It uses only two wires:

```text
SDA = Data
SCL = Clock
```

Characteristics:

* Multi-master.
* Multi-slave.
* Devices have unique addresses.
* Multiple devices can share the same bus.

Applications:

* OLED displays.
* LCD displays.
* Sensors.
* Real-time clocks.

```text
          CPU
           |
        SDA/SCL
           |
   ----------------
   |       |      |
 OLED  Sensor  Clock
```

### SPI - Serial Peripheral Interface

SPI is a fast synchronous serial protocol using a master/slave architecture.

```text
MOSI → Master Out Slave In
MISO → Master In Slave Out
SCLK → Clock
CS   → Chip Select
```

Advantages:

* Very fast.
* Simple protocol.
* Good for short distances.

Applications:

* SD cards.
* LCD screens.
* Flash memory.
* EEPROM.
* ADC converters.
* DAC converters.

### UART - Universal Asynchronous Receiver Transmitter

UART is an asynchronous serial communication protocol.

```text
Device A          Device B

TX  ------------> RX
RX  <------------ TX
GND ------------ GND
```

Communication speed is defined by the baud rate.

Applications:

* GPS modules.
* Bluetooth modules.
* Debug consoles.
* Communication between processors.

### I2S - Inter-IC Sound

I2S is a communication protocol dedicated to digital audio.

Important:

**I2S has nothing to do with I2C.**

It transports digital audio data between components such as processors, amplifiers and DACs.

Applications:

* Digital microphones.
* Audio amplifiers.
* Speakers.
* DAC audio boards.

```text
Processor
    |
   I2S
    |
Audio amplifier
    |
 Speaker
```

### PCM - Pulse Code Modulation

PCM is the method used to represent analog audio as digital data.

```text
Analog sound
      ↓
Sampling
      ↓
Digital values
      ↓
Storage or transmission
```

Example:

```text
Analog:
~~~~~~~ sound wave ~~~~~~~

Digital samples:
120
145
167
190
155
```

PCM is commonly used in digital audio systems and I2S communication.

---

