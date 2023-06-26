# LaserPowerControl
Diode laser power and temperature stabilization

![image](https://github.com/1mmo/LaserPowerControl/assets/79962819/5bf8bc49-70b2-4b4f-836a-44d68f7f65dd)


# Introduction 📝
Technological progress gives people incredible abilities. What seemed impossible for people of past centuries is now commonplace for every person. Lasers are one of those everyday things. Complex engineering and technical systems that require the creation and maintenance of appropriate means of control and management are now subject to every person. 

Laser radiation technologies are actively developing and, due to a wide range of physical and operating characteristics, are used in many different areas: information technology, industry, environmental monitoring, and medicine. This scale of application is associated primarily with the unique features of laser radiation, which, in turn, gives a high level of monochromaticity, coherence and directivity. Such indicators are unattainable by any other energy sources. “With the help of lasers, it is possible to provide extremely high concentrations of energy both in space, close to the conditions at the epicenter of a nuclear explosion and in the center of stars, and in time, providing such a high power (peak) and intensity of the light beam that when such beams interact with materials Fundamentally new physical effects arise” (A.S. Boreisho, S.V. Ivakin “Lasers: device and action”).


# Problems of uncontrolled laser radiation ⚠️
The laser stores energy and emits it in the form of a light beam. If the emitted energy leaves the laser, and its use becomes a separate task, then the remaining part of the energy inside the laser poses the problem for engineers to get rid of this energy by dissipating into the environment. With low-power lasers, everything is simple:
it is enough to keep them in a relatively cool room. When using more powerful lasers, the support of special heat removal or cooling systems is required.
Compactness is a positive feature of a semiconductor laser, but at the same time its problem. Because of the small size, the laser heats up quickly and the intensity degrades over time.

Laser power is one of the important parameters. When conducting medical operations, it is necessary to accurately maintain the required power, avoid fluctuations and increases, otherwise it may harm the patient.

# Algorithm development 💻
It is necessary to develop an algorithm capable of maintaining the required power levels and temperatures for a semiconductor laser based system. The task is to develop engineering skills in process automation, control of technical devices, use of an object-oriented programming style.

### <b>Experiment scheme</b>

![image](https://github.com/1mmo/LaserPowerControl/assets/79962819/8ca486aa-b171-4f7c-9301-82b61891a324)


### <b>Automation object</b>
The automation object is the NI PCI-6251 board. The PCI Multifunction Device - PCI6251 offers analog and digital I/O, bit counters/timers, and analog and digital triggers.

![image](https://github.com/1mmo/LaserPowerControl/assets/79962819/b7ef30ad-d2c0-4c08-9bcc-78865b93f5b9)


### <b>Laser diode</b>
AlGaInP semiconductor laser is used as a laser

![image](https://github.com/1mmo/LaserPowerControl/assets/79962819/e2094063-23d2-4271-b76f-c52857a97c2c)

### <b>Power unit</b>
As a power supply for the laser is used - THORLABS LDC

![image](https://github.com/1mmo/LaserPowerControl/assets/79962819/7be3dae2-3471-4956-bdd9-b14f0719d9e3)


### <b>Thermoelectric cooling</b>
Thermal control is based on the Peltier element, which consists of one or more pairs of semiconductors in the form of parallelepipeds and has a small size. One n-type semiconductor and one p-type semiconductor are used, which are paired with metal jumpers. If pairs of parallelepipeds are connected together in series, then an electric current flows through each pair. And depending on the direction of the current, the upper contacts are cooled, and the lower ones are heated, or vice versa. As a result, heat is transferred from one side of the Peltier element to the other, due to the electric current. As a result, a temperature difference is created. If the heating side is connected to a radiator or a fan, then the cold part will be cooled more strongly. And in a similar way, you can achieve a difference in temperature of about 70 ° C.

![image](https://github.com/1mmo/LaserPowerControl/assets/79962819/7aeeb644-535a-4ccd-9acb-46be73b8549c)

# Control algorithm 🕹
An algorithm based on a PID controller will be used to control laser radiation. A proportional-integral-derivative (PID) controller is a device in a closed-loop control loop. It is used in automatic control systems to generate a control signal in order to obtain the required accuracy and quality of the transient process.

![image](https://github.com/1mmo/LaserPowerControl/assets/79962819/801c9461-a11b-46ee-ab7c-29a31449c512)
The main problem of the PID controller is to choose the necessary coefficients for the proportional, integral, differential parts. The selection process is carried out manually, studying the influence of a particular coefficient on the system. The task of the PID regulator in power control is to calculate the difference between the current and the required power during operation and, by outputting the voltage determined by the regulator, minimize the error. The task of the PID controller in temperature control is to minimize the difference between the current temperature and the set temperature by calculating the required Peltier turn-on time, that is, the cooling time.

# Structure and description of the program. 📎
At the heart of the project is the DAQmx library, which provides support for customers using NATIONAL INSTRUMENTS data acquisition and signal conditioning devices. The nidaqmx package is open source, hosted on github, and is a complex object-oriented wrapper. Nidaqmx supports Windows and Linux operating systems.
Program architecture:
- The realtimeplot.py module is designed to display the dynamics of power and temperature changes coming from the sensors to the ADC.
- Controller.py module - includes four classes:
  - PID_regulator (for PID tuning);
  - PCI - configuration of analog input and output in the NI PCI-6251 device (board management);
  - PowerControlling is a class that inherits from the PCI class. Designed for direct power control;
  - TemperatureControlling is a class that inherits from the PCI class. Designed for direct temperature control.
- The smoothing.py module is responsible for averaging the indicators coming from the ADC.
- The main.py program is the code that includes the launch of all modules.

# RESULTS 📝
The developed control system for a laser diode contains circuits for controlling its power and temperature, taking into account the features. Generated power values of at least 0.1% of the set value have been achieved at a temperature of 0.1 °C with care. The control algorithm written in the Python environment makes it possible to use it in all modern hardware. The algorithm shows high-quality results and can be used in industry, medicine, and the scientific field. Requirements for hardware and software environment are not related to the problem of HIV infection. The ability to run on Windows, Linux with Python environments and the library installed, allows you to quickly set up the circuit configuration and take advantage of semiconductor laser control and cooling to a great extent. The game program is enough for the user and the parameters of the required power and temperature are entered.

- The use of diode lasers has shown that this technology is one of the most relevant solutions in many different areas of human activity. Semiconductor lasers are different from most other types of lasers and are the most efficient.
- Any laser system must have: control and data acquisition systems, power control, temperature control, power supply. Such systems must be precisely configured and controlled so as not to harm people and the environment.
- The development of the Python programming language and, as a result, the object-oriented programming style encourages engineers to study this area, find applications for new technologies in tasks, improve the efficiency of software and the possibility of its improvement. It is not uncommon to observe a situation in a company when employees do not touch some system because it was written on old technologies that most programmers did not study, then the company faces difficulties in finding the right specialist.
- The results of the developed algorithm show that such a system is a reliable assistant in the control and maintenance of laser radiation.




