# 5. Programming

Programming creates instructions that control hardware and process information.

## 5.1 Programming Fundamentals

### Program

A program is a sequence of instructions executed by a processor.

```text
Read sensor
     ↓
Process information
     ↓
Make decision
     ↓
Control hardware
     ↓
Repeat
```

### Variables

Store information.

Example:

```python
temperature = 25
```

### Functions

Reusable blocks of instructions.

Example:

```python
def move_forward():
    start_motor()
```

### Loops

Repeat actions.

Example:

```python
while True:
    read_sensor()
    update_display()
```

### Libraries

Pre-written code providing additional functionality.

Example:

```python
import camera_library
```

## 5.2 How Python Runs on Hardware

Python is a high-level programming language.

The code passes through several layers before controlling hardware.

```text
Python Code
     |
Python Interpreter
     |
Bytecode
     |
Python Virtual Machine
     |
Operating System
     |
Hardware Drivers
     |
Electronic Component
```

### Python Interpreter

Reads Python instructions and executes them.

The most common implementation is CPython.

### Bytecode

Intermediate representation generated from Python code.

Not directly understood by the CPU.

### Python Virtual Machine

Executes Python bytecode.

### Operating System

Manages:

* Memory.
* Processes.
* Files.
* Hardware access.

### Hardware Drivers

Translate software requests into hardware commands.

Example:

```text
Python
 |
GPIO Library
 |
Driver
 |
Electrical Pin
 |
LED ON
```

## 5.3 High-Level vs Low-Level Programming

```text
High Level
-----------
Python
C++
C
Assembly
Machine Code
-----------
Low Level
```

High-level languages:

* Easier to write.
* Faster development.
* More portable.

Low-level languages:

* More control.
* Higher performance.
* More complexity.

---

# Final Overview

A complete hardware/software system follows this chain:

```text
User
 |
Application
 |
Programming Language
 |
Operating System
 |
Driver
 |
Communication Protocol
 |
Electronic Component
 |
Physical Action
```

Example:

```text
Phone App
    |
   WiFi
    |
Python Program
    |
GPIO / I2C / SPI
    |
Motor Driver
    |
Motor
    |
Robot moves
```
