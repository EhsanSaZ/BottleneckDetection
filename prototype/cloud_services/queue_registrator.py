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

        # self.pipeline_rabbit_config_template = 'input {{ rabbitmq {{ id => "rabbitmq_pipeline" host => "rabbitmq" queue => "{queue_name}" key => "{key}" }} }} filter {{ json {{ source => "message" }} }}output {{ elasticsearch {{ hosts => ["{es_host}:{es_port}", "es02:9200", "es03:9200"] }} }}'
        # self.pipeline_rabbit_config_template = 'input {{ rabbitmq {{ id => "rabbitmq_pipeline" host => "rabbitmq" queue => "{queue_name}" key => "{key}" }} }} output {{ stdout {{ codec => "dots" }} }}'
        # self.pipeline_rabbit_config_template = 'input {{ rabbitmq {{ id => "rabbitmq_pipeline" host => "rabbitmq" queue => "{queue_name}" key => "{key}" codec =>  plain }} }} output {{ elasticsearch {{ hosts => ["{es_host}:{es_port}", "es02:9200", "es03:9200", "es04:9200"] }} }}'
        # self.pipeline_rabbit_config_template = 'input {{ rabbitmq {{ id => "rabbitmq_pipeline" host => "rabbitmq" queue => "{queue_name}" key => "{key}" codec =>  plain }} }} filter {{ grok {{ match => {{ "message" => "%{{TIMESTAMP_ISO8601:timestamp}} %{{NOTSPACE:transferID}} %{{INT:is_sender}} %{{BASE16NUM:sequence_number}} %{{NOTSPACE:request_type}} %{{GREEDYDATA:metrics}}" }} }} date {{ match => ["timestamp", "ISO8601"] target => "@timestamp" }} }}'
        # self.pipeline_rabbit_config_template = 'input {{ rabbitmq {{ id => "rabbitmq_pipeline" host => "rabbitmq" queue => "{queue_name}" key => "{key}" codec =>  plain }} }} filter {{  json {{ source => "message" }} }} output {{ elasticsearch {{ hosts => ["{es_host}:{es_port}", "es02:9200", "es03:9200", "es04:9200"] data_stream => "true" }} }}'



        # self.pipeline_rabbit_config_template = 'input {{ rabbitmq {{ id => "rabbitmq_pipeline" host => "rabbitmq" queue => "{queue_name}" key => "{key}" codec => json }} }} output {{ elasticsearch {{ hosts => ["{es_host}:{es_port}, "es02:9200", "es03:9200""] }} } }}'


        # self.pipeline_rabbit_config_template = 'input {{ rabbitmq {{ id => "rabbitmq_pipeline" host => "rabbitmq" queue => "{queue_name}" key => "{key}" codec =>  plain }} }} filter {{ grok {{ match => {{ "message" => "%{{TIMESTAMP_ISO8601:timestamp}} %{{NOTSPACE:transferID}} %{{INT:is_sender:int}} %{{NUMBER:avg_rtt_value}},%{{NUMBER:pacing_rate:float}},%{{NUMBER:cwnd_rate:float}},%{{NUMBER:avg_retransmission_timeout_value:float}},%{{NUMBER:byte_ack:float}},%{{NUMBER:seg_out:float}},%{{NUMBER:retrans:float}},%{{NUMBER:mss_value:float}},%{{NUMBER:ssthresh_value:float}},%{{NUMBER:segs_in:float}},%{{NUMBER:avg_send_value:float}},%{{NUMBER:unacked_value:float}},%{{NUMBER:rcv_space:float}},%{{NUMBER:send_buffer_value:float}},%{{NUMBER:avg_dsack_dups_value:float}},%{{NUMBER:avg_reord_seen:float}},%{{NUMBER:rchar:float}},%{{NUMBER:wchar:float}},%{{NUMBER:syscr:float}},%{{NUMBER:syscw:float}},%{{NUMBER:read_bytes_io:float}},%{{NUMBER:write_bytes_io:float}},%{{NUMBER:cancelled_write_bytes:float}},%{{NUMBER:pid:float}},%{{NUMBER:ppid:float}},%{{NUMBER:pgrp:float}},%{{NUMBER:session:float}},%{{NUMBER:tty_nr:float}},%{{NUMBER:tpgid:float}},%{{NUMBER:flags:float}},%{{NUMBER:minflt:float}},%{{NUMBER:cminflt:float}},%{{NUMBER:majflt:float}},%{{NUMBER:cmajflt:float}},%{{NUMBER:utime:float}},%{{NUMBER:stime:float}},%{{NUMBER:cutime:float}},%{{NUMBER:cstime:float}},%{{NUMBER:priority:float}},%{{NUMBER:nice:float}},%{{NUMBER:num_threads:float}},%{{NUMBER:itrealvalue:float}},%{{NUMBER:starttime:float}},%{{NUMBER:vsize:float}},%{{NUMBER:rss:float}},%{{NUMBER:rsslim:float}},%{{NUMBER:startcode:float}},%{{NUMBER:endcode:float}},%{{NUMBER:startstack:float}},%{{NUMBER:kstkesp:float}},%{{NUMBER:kstkeip:float}},%{{NUMBER:signal:float}},%{{NUMBER:blocked:float}},%{{NUMBER:sigignore:float}},%{{NUMBER:sigcatch:float}},%{{NUMBER:wchan:float}},%{{NUMBER:nswap:float}},%{{NUMBER:cnswap:float}},%{{NUMBER:exit_signal:float}},%{{NUMBER:processor:float}},%{{NUMBER:rt_priority:float}},%{{NUMBER:policy:float}},%{{NUMBER:delayacct_blkio_ticks:float}},%{{NUMBER:guest_time:float}},%{{NUMBER:cguest_time:float}},%{{NUMBER:start_data:float}},%{{NUMBER:end_data:float}},%{{NUMBER:start_brk:float}},%{{NUMBER:arg_start:float}},%{{NUMBER:arg_end:float}},%{{NUMBER:env_start:float}},%{{NUMBER:env_end:float}},%{{NUMBER:exit_code:float}},%{{NUMBER:cpu_usage_percentage:float}},%{{NUMBER:mem_usage_percentage:float}},%{{NUMBER:tcp_rcv_buffer_min:float}},%{{NUMBER:tcp_rcv_buffer_default:float}},%{{NUMBER:tcp_rcv_buffer_max:float}},%{{NUMBER:tcp_snd_buffer_min:float}},%{{NUMBER:tcp_snd_buffer_default:float}},%{{NUMBER:tcp_snd_buffer_max:float}},%{{NUMBER:req_waittime:float}},%{{NUMBER:req_active:float}},%{{NUMBER:read_bytes:float}},%{{NUMBER:write_bytes:float}},%{{NUMBER:ost_setattr:float}},%{{NUMBER:ost_read:float}},%{{NUMBER:ost_write:float}},%{{NUMBER:ost_get_info:float}},%{{NUMBER:ost_connect:float}},%{{NUMBER:ost_punch:float}},%{{NUMBER:ost_statfs:float}},%{{NUMBER:ost_sync:float}},%{{NUMBER:ost_quotactl:float}},%{{NUMBER:ldlm_cancel:float}},%{{NUMBER:obd_ping:float}},%{{NUMBER:pending_read_pages:float}},%{{NUMBER:read_RPCs_in_flight:float}},%{{NUMBER:avg_waittime_md:float}},%{{NUMBER:inflight_md:float}},%{{NUMBER:unregistering_md:float}},%{{NUMBER:timeouts_md:float}},%{{NUMBER:req_waittime_md:float}},%{{NUMBER:req_active_md:float}},%{{NUMBER:mds_getattr_md:float}},%{{NUMBER:mds_getattr_lock_md:float}},%{{NUMBER:mds_close_md:float}},%{{NUMBER:mds_readpage_md:float}},%{{NUMBER:mds_connect_md:float}},%{{NUMBER:mds_get_root_md:float}},%{{NUMBER:mds_statfs_md:float}},%{{NUMBER:mds_sync_md:float}},%{{NUMBER:mds_quotactl_md:float}},%{{NUMBER:mds_getxattr_md:float}},%{{NUMBER:mds_hsm_state_set_md:float}},%{{NUMBER:ldlm_cancel_md:float}},%{{NUMBER:obd_ping_md:float}},%{{NUMBER:seq_query_md:float}},%{{NUMBER:fld_query_md:float}},%{{NUMBER:close_md:float}},%{{NUMBER:create_md:float}},%{{NUMBER:enqueue_md:float}},%{{NUMBER:getattr_md:float}},%{{NUMBER:intent_lock_md:float}},%{{NUMBER:link_md:float}},%{{NUMBER:rename_md:float}},%{{NUMBER:setattr_md:float}},%{{NUMBER:fsync_md:float}},%{{NUMBER:read_page_md:float}},%{{NUMBER:unlink_md:float}},%{{NUMBER:setxattr_md:float}},%{{NUMBER:getxattr_md:float}},%{{NUMBER:intent_getattr_async_md:float}},%{{NUMBER:revalidate_lock_md:float}},%{{NUMBER:system_cpu_percent:float}},%{{NUMBER:system_memory_percent:float}},%{{NUMBER:remote_ost_read_bytes:float}},%{{NUMBER:remote_ost_write_bytes:float}},%{{NUMBER:dtn_read_bytes:float}},%{{NUMBER:dtn_write_bytes:float}},%{{NUMBER:lustre_nic_send_bytes:float}},%{{NUMBER:lustre_nic_receive_bytes:float}},%{{NUMBER:label_value:float}}" }} }} date {{ match => ["timestamp", "ISO8601"] target => "@timestamp" }} }} output {{ elasticsearch {{ hosts => ["{es_host}:{es_port}", "es02:9200", "es03:9200", "es04:9200"] }} }}'

        self.pipeline_rabbit_config_template = 'input {{ rabbitmq {{ id => "rabbitmq_pipeline" host => "rabbitmq" queue => "{queue_name}" key => "{key}" codec =>  plain }} }} filter {{ grok {{ match => {{ "message" => "%{{TIMESTAMP_ISO8601:timestamp}} %{{NOTSPACE:transferID}} %{{INT:is_sender:int}} %{{NUMBER:avg_rtt_value:float}},%{{NUMBER:segs_in:float}},%{{NUMBER:seg_out:float}},%{{NUMBER:retrans:float}},%{{NUMBER:system_cpu_percent:float}},%{{NUMBER:system_memory_percent:float}},%{{NUMBER:tcp_rcv_buffer_max:float}},%{{NUMBER:tcp_snd_buffer_max:float}},%{{NUMBER:read_bytes:float}},%{{NUMBER:write_bytes:float}},%{{NUMBER:remote_ost_read_bytes:float}},%{{NUMBER:remote_ost_write_bytes:float}},%{{NUMBER:nic_send_bytes:float}},%{{NUMBER:nic_receive_bytes:float}}" }} }} date {{ match => ["timestamp", "ISO8601"] target => "@timestamp" }} }} output {{ elasticsearch {{ hosts => ["{es_host}:{es_port}", "es02:9200", "es03:9200", "es04:9200"] }} }}'



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
                        pl["pipeline.workers"] = 32
                        new_pl = False
                        break
                if new_pl:
                    pl = {"pipeline.id": pipeline_id, "path.config": pipeline_docker_config_path, "pipeline.workers": 32}
                    data.append(pl)
            else:
                data = []
                pl = {"pipeline.id": pipeline_id, "path.config": pipeline_docker_config_path, "pipeline.workers": 32}
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
