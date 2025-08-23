# UART

UART stands for Universal Asynchronous Receiver Transmitter, this can be used for many things on an embedded system including communicating with other processors, sensor communications and of course what we're interested in - debug access. One of the features of using a UART over something like SPI or I2C is that since it is asynchronous, there is no clock to synchronize the signals being sent between the two. In place of using a clock the transmit line utilizes start and stop bits to outline a data packet. This means that both the transmit and receive line must know the rate at which to read bits off of the wire as they come across, this is referred to as the baud rate. This is essentially the speed of the data being transferred which is typically measured in bits per second. 

So if we were to look at a UART packet, we would have the following

| Location | Name | Description | 
| -------- | ---- | ----------- | 
| 0:1 | Start bit | Used to signify the start of a packet | 
| 1:9 | Data bits (this can also be configured to be any value really, but is commonly 8) | The data to be send / read, note that data is typically sent with the least significant bit first | 
| 9:10 | Parity bit | This bit determines if data has been changed as it went over the wire | 
| 10:12 | Stop bits | This signifies that the packet has ended | 

This is all great information, but in practice what does it mean for us reverse engineers? Well depending on the logic level that the UART is using, we can probe the circuit board with a multimeter and look for fluctuations in the voltage, this might lead us to a debug console that is spewing log messages, or it may just be another bus being used for sensor communications.

# Looking For Serial

When looking at an embedded system for the first time one of the first things you want to look for is a serial port, these can lead to additional  debug information and in some cases even terminal access. Debug ports are often exposed via a UART and typically consist of a transmit (Tx) and receive (Rx) line. 

Of course some systems only give access to Tx and other have no access at all, but it's still a good first step to try to hunt these down when assessing an embedded system. Methods of discovery for serial terminals can vary based on the system but there are a few things that can lead to quick wins:

1. Debug headers or vias
2. Silk screen labeling
3. Unused pads / jumpers on the PCB

So what do headers look like? What are vias? Below are some example images of what they typically look like and after looking at these you'll notice something very similar on our board

![EXAMPLE_1](https://wrongbaud.github.io/assets/img/EXAMPLE_1.jpeg)

![EXAMPLE_1](https://wrongbaud.github.io/assets/img/EXAMPLE_2.png)

The Tx line is typically held high in most reference designs by whoever is driving it, AKA transmitting. We have 2 possible candidates for Tx. Pins 1-3. There is a good chance that one of these is our 3.3V VCC line, we can determine that by noticing the pin's behavior when the platform is powered down. If it is a fast drop to 0V we can assume that it is a GPIO line of some sort, if it slowly drops down to 0V, it is likely the VCC line because that slow drop is caused by capacitors that are often present on power rails! After looking at these pins on shutdown we can assume that pin 1 is VCC, as it slowly drops from 3.3V to 0V over the course of ~5 seconds. This leaves two candidates for Tx/Rx, pins 3 and 4.


Also note that we talked about how it's often up to the transmitter to drive the line high, which would mean that the Rx line (which we would Transmit to) is likely pin 3 because it's 0V and not connected to ground!