import json
import time
import traceback
import yaml
import pika
from pika.exceptions import ChannelClosed
from Config import Config


class QueueRegistrator:
    def __init__(self, rabbit_host, rabbit_port=5672):
        self.rabbit_host = rabbit_host
        self.rabbit_port = rabbit_port
        self.rabbitmq_connection = None
        self.rabbitmq_channel = None

        self.pipeline_rabbit_config_template = 'input {{ rabbitmq {{ id => "rabbitmq_pipeline" host => "rabbitmq" queue => "{queue_name}" key => "{key}" codec => json }} }} output {{ elasticsearch {{ hosts => ["{es_host}:{es_port}"] }} stdout {{ codec => rubydebug }} }}'

    def check_rabbit_connection(self):
        if not self.rabbitmq_channel or self.rabbitmq_channel.is_closed:
            if self.rabbitmq_connection and self.rabbitmq_connection.is_open:
                self.rabbitmq_connection.close()
            self.rabbitmq_connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=self.rabbit_host, port=self.rabbit_port))
            self.rabbitmq_channel = self.rabbitmq_connection.channel()
            self.rabbitmq_channel.basic_qos(prefetch_count=1)
            self.rabbitmq_channel.queue_declare(queue='rpc_queue')
            # self.rabbitmq_channel.queue_declare(queue=self.heartbeat_queue_name, arguments={'x-message-ttl': 500})
            # self.heart_beat_at = time.time()

    def process_pipelines_file(self, pipeline_id, config_file_name, pipeline_workers):
        pipeline_docker_config_path = Config.docker_pipeline_config_path + config_file_name
        with open(Config.pipelines_yml_path, 'r+') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            new_pl = True
            if data:
                for pl in data:
                    if pl["pipeline.id"] == pipeline_id:
                        pl["pipeline.id"] = pipeline_id
                        pl["path.config"] = pipeline_docker_config_path
                        pl["pipeline.workers"] = 1
                        new_pl = False
                        break
                if new_pl:
                    pl = {"pipeline.id": pipeline_id, "path.config": pipeline_docker_config_path, "pipeline.workers": 1}
                    data.append(pl)
            else:
                data = []
                pl = {"pipeline.id": pipeline_id, "path.config": pipeline_docker_config_path, "pipeline.workers": 1}
                data.append(pl)
            f.truncate(0)
            f.seek(0)
            # print(yaml.dump(data))
            yaml.dump(data, f)

    def on_request(self, ch, method, props, body):
        request_json = json.loads(body)
        print("got request", request_json)
        try:
            if request_json.get("request_type") == "register_new_queue":
                queue_name = request_json.get("body").get("rabbit_log_queue_name")
                print("REGISTERING queue {}".format(queue_name))
                pipeline_config = self.pipeline_rabbit_config_template.format(queue_name=queue_name, key=queue_name,
                                                                              es_host=Config.elastic_host,
                                                                              es_port=Config.elastic_port)
                config_file_name = "{}.conf".format(queue_name)
                pipeline_local_config_path = Config.local_pipeline_config_path + config_file_name
                with open(pipeline_local_config_path, 'w+') as f:
                    f.write(pipeline_config)
                self.process_pipelines_file(pipeline_id=queue_name, config_file_name=config_file_name, pipeline_workers=1)
                response = json.dumps({"status": 200, "msg": "{} registered successfully".format(queue_name)})
                ch.basic_publish(exchange='',
                                 routing_key=props.reply_to,
                                 properties=pika.BasicProperties(correlation_id=props.correlation_id),
                                 body=response)
                ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            msg = str(e)
            response = json.dumps({"status": 400, "msg": msg})
            ch.basic_publish(exchange='',
                             routing_key=props.reply_to,
                             properties=pika.BasicProperties(correlation_id=props.correlation_id),
                             body=response)
            ch.basic_ack(delivery_tag=method.delivery_tag)

    def start_server(self):
        while True:
            try:
                self.check_rabbit_connection()
                self.rabbitmq_channel.basic_consume(queue='rpc_queue', on_message_callback=self.on_request)
                self.rabbitmq_channel.start_consuming()
            except ChannelClosed as e:
                self.check_rabbit_connection()
                self.rabbitmq_channel.basic_consume(queue='rpc_queue', on_message_callback=self.on_request)
                self.rabbitmq_channel.start_consuming()
            except Exception as e:
                traceback.print_exc()
                print("Retry consuming rpc requests")


service = QueueRegistrator(Config.rabbit_host, Config.rabbit_port)
service.start_server()
