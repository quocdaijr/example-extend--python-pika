import sys
import os
import json

from rabbitmq import RabbitMQ
from retry import retry


class ExampleJob(RabbitMQ):

    def __init__(self):
        super().__init__(
            host='127.0.0.1',
            port=5672,
            username='username',
            password='password',
            vhost='/',
            exchange='example_exchange',
            queue='example_queue_name'
        )

    @retry(exceptions=Exception, tries=-1, delay=3)
    def execute(self, ch, method, properties, body, *args, **kwargs):
        try:
            print("You see this because you just sub queue")
            input_params = json.loads(body)
            print(input_params)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(e, exc_type, os.path.split(exc_tb.tb_frame.f_code.co_filename)[1], exc_tb.tb_lineno)
            # create error exception to retry
            raise Exception(e)
