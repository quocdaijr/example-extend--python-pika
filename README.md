## An example extend from Pika package

###Struct

- `rabbitmq.py`: File contains class extend from Python Pika with some basic methods (pub, sub).
- `jobs.py`: File contains Job classes.
- `example.py`: an example

###Usage

Create virtual env

Edit config RabbitMQ host and port (in Job class)

Run example receive: `python example.py receive` to receive msg queue (Not interrupt (Ctrl+C) process)

Run example send: `python example.py send` to send example msg queue and see result in terminal run command receive (above)

###Note: 
You must have RabbitMQ server before run

###Contributes

You can help me improve this code. Thank you!
