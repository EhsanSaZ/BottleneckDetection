class Config:
    # rabbit publisher
    rabbit_host = "localhost"
    rabbit_port = 5672
    # rabbit_log_queue_name = "transfer_monitoring_logs"
    # heartbeat_queue_name = "HEARTBEAT_QUEUE"
    # rabbitmq_heartbeat_interval = 60

    elastic_host = "es01"
    elastic_port = 9200
    local_pipeline_config_path = "/home/esaeedizade/elk_conf/esdatadir/logst/proto_bufs/allpl/"
    docker_pipeline_config_path = "/usr/share/pipelinesConfig/allpl/"
    pipelines_yml_path = "/home/esaeedizade/elk_conf/esdatadir/logst/pipeline/pipelines.yml"
    #
    # # rabbit publisher
    # rabbit_host = "c220g1-030616.wisc.cloudlab.us"
    # rabbit_port = 5672
    # # rabbit_log_queue_name = "transfer_monitoring_logs"
    # # heartbeat_queue_name = "HEARTBEAT_QUEUE"
    # # rabbitmq_heartbeat_interval = 60
    #
    # elastic_host = "es01"
    # elastic_port = 9200
    # local_pipeline_config_path = "/users/Ehsan/elk_conf/esdatadir/logst/allpl/"
    # docker_pipeline_config_path = "/usr/share/pipelinesConfig/allpl/"
    # pipelines_yml_path = "/users/Ehsan/elk_conf/esdatadir/logst/pipeline/pipelines.yml"