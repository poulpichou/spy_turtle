# 3. Hardware

Hardware is the physical layer where software interacts with electronic components.

## 3.1 Computing Hardware

### Microcontrollers

A microcontroller is a small computer designed for direct hardware control.

Examples:

* Arduino.
* ESP32.
* STM32.

Characteristics:

* Very low power consumption.
* Direct access to pins.
* Usually dedicated to one task.

Applications:

* Sensors.
* Small robots.
* Embedded systems.

### Single Board Computers (SBC)

A Single Board Computer is a complete computer integrated on one board.

Example:

* Raspberry Pi.

Characteristics:

* Runs an operating system.
* Supports networking.
* Runs multiple applications.

Applications:

* Robotics.
* Cameras.
* AI.
* Servers.

## 3.2 Hardware Extensions

### HAT - Hardware Attached on Top

A HAT is an expansion board designed to connect directly onto another board.

Examples:

* Power management boards.
* Motor controllers.
* Sensor boards.
* Display boards.
* Audio boards.

Advantages:

* Cleaner wiring.
* Standardized connections.
* Easier assembly.

```text
Raspberry Pi

      |
      |
     HAT

      |
Extra hardware
```

### Power Supplies

A power supply provides stable electrical energy.

Important parameters:

**Voltage**

* Must match component requirements.

**Current**

* Must be sufficient for all connected devices.

**Voltage Regulation**

* Converts unstable power sources into stable voltages.

```text
Battery
   |
Voltage regulator
   |
Electronic system
```

### Cooling

Electronic components generate heat.

Too much heat can cause:

* Reduced performance.
* Instability.
* Hardware damage.

Passive cooling:

* Heat sinks.
* Metal surfaces.

Active cooling:

* Fans.
* Temperature-controlled systems.

## 3.3 Hardware Components

### LEDs

Light Emitting Diodes convert electrical energy into light.

Applications:

* Status indicators.
* Lighting.
* Displays.

### Displays

Displays convert digital information into visual output.

Examples:

* OLED.
* LCD.
* E-paper.

Communication methods:

* I2C.
* SPI.
* HDMI.

### Motors

Motors convert electrical energy into mechanical movement.

Examples:

* DC motors.
* Servo motors.
* Stepper motors.

They usually require a motor driver because processors cannot directly provide enough current.

### Sensors

Sensors measure physical information.

Examples:

* Temperature.
* Distance.
* Light.
* Motion.
* Pressure.

They often communicate using:

* I2C.
* SPI.
* UART.

### Speakers and Audio Components

Speakers convert electrical signals into sound.

```text
Processor
    |
Digital audio signal
    |
Amplifier
    |
Speaker
```

---

# 4. Networks

Networks allow computers and electronic devices to exchange information.

A network connects devices using:

* Wired connections (Ethernet, fiber).
* Wireless connections (WiFi, Bluetooth, cellular).

## 4.1 Network Fundamentals

### Client and Server

A server provides a service.

A client requests information or services.

Example:

```text
Phone (Client)

      |
      | Request
      ↓

Robot (Server)

      |
      | Response
      ↓

Phone receives data
```

### Local Area Network (LAN)

A LAN connects devices inside a limited area.

```text
        Router

    /      |      \

 Phone  Laptop  Robot
```

### Internet

The Internet is a network of interconnected networks.

```text
Device
  |
Router
  |
Internet
  |
Remote Server
```

## 4.2 Network Protocols

### IP - Internet Protocol

IP provides addressing and routing.

Example:

```text
192.168.1.25
```

### TCP

TCP provides reliable communication.

Used by:

* Websites.
* SSH.
* File transfers.

### UDP

UDP provides faster communication with no delivery guarantee.

Used by:

* Video streaming.
* Games.
* Real-time applications.

### HTTP / HTTPS

HTTP is used for web communication.

HTTPS adds encryption.

Applications:

* Websites.
* Web applications.
* APIs.

### WebSocket

WebSocket enables continuous two-way communication.

Used for:

* Live dashboards.
* Robot control.
* Real-time data.

## 4.3 IP Addresses and Ports

An IP address identifies a machine.

A port identifies a service.

Example:

```text
IP: 192.168.1.50

Port 22  → SSH
Port 80  → HTTP
Port 443 → HTTPS
```

Communication uses:

```text
IP Address + Port
```

Example:

```text
192.168.1.50:22
```

## 4.4 Authentication and Security

Authentication:
"Who are you?"

Authorization:
"What are you allowed to do?"

### Password Authentication

```text
Username
+
Password
```

### Public Key Authentication

Uses:

* Private key: secret, kept by the user.
* Public key: shared with servers.

```text
Private Key
     |
Creates proof
     |
Server verifies with Public Key
```

## 4.5 SSH - Secure Shell

SSH allows secure remote access to another computer.

Uses:

* Server administration.
* Raspberry Pi control.
* Remote debugging.

```text
Laptop

   SSH connection

        ↓

Raspberry Pi
```

SSH key authentication:

```text
Laptop

Private Key

      |
 SSH Authentication

      |

Raspberry Pi

Public Key
authorized_keys
```

Advantages:

* More secure.
* No password required.
* Common in professional environments.

## 4.6 Network Security Basics

### Encryption

Transforms readable information into protected data.

### Firewall

Controls allowed network connections.

### Least Privilege

A system should only have the permissions it actually needs.

---

