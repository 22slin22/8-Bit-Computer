# 8-Bit-Computer

## The Project
This is all the code I used for my highschool project "Building an 8-Bit Computer".
The code was mainly used for two purposes: Microcoding the computer, e.i. filling the EEPROMS used in the decoder of the computer and
programming it, e.i. filling the EEPROM that is part of the computer's memory. To make programming easier, I programmed an assembler.

## The Structure
**Memory** contains the assembly code for programs run on the 8-Bit computer.

**Instructions.txt** contains a list of all instructions the computer is able to execute or will be able to (the ones commented out with a #)

**ROM.py** handles writing the EEPROMS.

**instructions.py** looks at every instruction in **instructions-micro-steps.txt** and fills the decoder EEPROMS with the instructins specified.

**memory.py** is an assembler that takes one assembly file (usually *Memory/file*), assembles it and writes the machine code into the EEPROM that is part of momory.

## Usage

This code probably has little value without an own 8-Bit Computer that is structured similar to mine.

## Want to know more

If you want to learn more about the 8-Bit Computer itself, I can send you the thesis I wrote about it aswell as providing you with the schematics. Feel free to contact me about anything.
