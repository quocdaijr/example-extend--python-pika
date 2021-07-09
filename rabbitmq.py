import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime

import pika
import pika.exceptions
from pika.exchange_type import ExchangeType
from retry import retry


class RabbitMQ(ABC):
    MAX_PRIORITY = 10
    DELIVERY_MODE = 2

    def __init__(self, host='127.0.0.1', port=5672, username='zyz', password='zYz123@', vhost='/', exchange='',
                 queue='', **kwargs):
        if not host or not port or not username or not password or not vhost or not exchange or not queue:
            raise Exception("Params is invalid.")
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.vhost = vhost
        self.exchange = exchange
        self.queue = queue
        self.exchange_type = kwargs['exchange_type'] if 'exchange_type' in kwargs else ExchangeType.direct

        credentials = pika.PlainCredentials(username, password)
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host, port, vhost, credentials, heartbeat=0))
        # Init the channel to exchange data to RabbitMQ server
        self.channel = self.connection.channel()
        if not self.connection.is_open or not self.channel.is_open:
            raise Exception("Connection fail. Please check rabbitmq-server is running.")
        self.channel.exchange_declare(exchange=self.exchange, exchange_type=self.exchange_type, passive=False,
                                      durable=True, auto_delete=False)
        self.channel.queue_declare(queue=self.queue, passive=False, durable=True, auto_delete=False)
        # ,arguments={"x-max-priority": self.MAX_PRIORITY})

    @abstractmethod
    @retry(exceptions=Exception, tries=-1, delay=3)
    def execute(self, ch, method, properties, body, *args, **kwargs):
        pass

    def handle(self, ch, method, properties, body, *args, **kwargs):
        self.execute(ch, method, properties, body, *args, **kwargs)
        self.done(ch=ch, method=method)

    def done(self, ch, method):
        logging.info(" [*] " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": Done")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def pub(self, data=None, prior=1):
        message = json.dumps(data)
        self.channel.basic_publish(exchange=self.exchange, routing_key=self.queue + ".#", body=message,
                                   properties=pika.BasicProperties(priority=prior, delivery_mode=self.DELIVERY_MODE))
        logging.info("[S] Send %r:%r" % (self.queue, message))
        self.channel.close()
        self.connection.close()

    def sub(self):
        logging.info(" [*] Queue: " + self.queue + " - " + datetime.now().strftime('%H:%M:%S %d-%m-%Y'))
        logging.info(' [*] Waiting for logs. To exit press CTRL+C')
        self.channel.queue_bind(queue=self.queue, exchange=self.exchange, routing_key=self.queue + ".#")
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(self.queue, getattr(self, "handle"))

        try:
            self.channel.start_consuming()
        except KeyboardInterrupt as e:
            logging.warning("Stopping consuming with e: " + str(e))
            self.channel.stop_consuming()

        self.channel.close()
        self.connection.close()
