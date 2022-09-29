from datetime import datetime, timezone
import json
import threading
import time, os
import traceback
import zmq
from pika.exceptions import StreamLostError
import uuid

# import global_vars
from multiprocessing import Process
import pika


class cloudStress():
    def __init__(self, cluster_name, rabbit_host, rabbit_port=5672, rabbitmq_heartbeat_interval=60, **kwargs):
        # super().__init__()
        self.rabbit_host = rabbit_host
        self.rabbit_port = rabbit_port
        self.rabbitmq_HEARTBEAT_INTERVAL = rabbitmq_heartbeat_interval

        self.rabbitmq_connection = None
        self.rabbitmq_channel = None

        # self.rabbit_log_queue_name = rabbit_log_queue_name
        self.host_name = os.uname()[1]
        self.cluster_name = cluster_name
        self._rabbit_log_queue_name = "{}_at_{}".format(self.host_name, self.cluster_name)
        self.retry_number = 7
        self.message_rate = 2000

    def check_rabbit_connection(self):
        if not self.rabbitmq_channel or self.rabbitmq_channel.is_closed:
            if self.rabbitmq_connection and self.rabbitmq_connection.is_open:
                self.rabbitmq_connection.close()
            self.rabbitmq_connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=self.rabbit_host, port=self.rabbit_port,
                                          heartbeat=self.rabbitmq_HEARTBEAT_INTERVAL))
            self.rabbitmq_channel = self.rabbitmq_connection.channel()
            self.rabbitmq_channel.queue_declare(queue=self._rabbit_log_queue_name)
            self.result = self.rabbitmq_channel.queue_declare(queue='', exclusive=True)
            self.callback_queue = self.result.method.queue
        # print(f"Monitoring agent is ready to publish data to rabbitmq.")

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body
        else:
            print("got this {} but last req is {}".format(props.correlation_id, self.corr_id))
            self.response = None

    def advertise_rabbit_log_queue_name(self):
        self.check_rabbit_connection()
        sleep_time = 1
        retry = 1
        self.corr_id = str(uuid.uuid4())
        while retry <= self.retry_number:
            self.check_rabbit_connection()
            self.response = None
            self.rabbitmq_channel.basic_consume(queue=self.callback_queue, on_message_callback=self.on_response,
                                                auto_ack=True)
            body = json.dumps({"request_type": "register_new_queue",
                               "body": {"rabbit_log_queue_name": self._rabbit_log_queue_name}
                               })
            self.rabbitmq_channel.basic_publish(exchange='', routing_key='rpc_queue',
                                                properties=pika.BasicProperties(reply_to=self.callback_queue,
                                                                                correlation_id=self.corr_id), body=body)
            self.rabbitmq_connection.process_data_events(time_limit=sleep_time)
            if self.response is not None:
                response_json = json.loads(self.response)
                if response_json["status"] == 200:
                    print("ready to publish data")
                else:
                    print("Error in registering queue, {}", format(response_json))
                    return False
                break
            else:
                # T ODO handle retry if no response is back
                sleep_time = sleep_time * 2
                retry += 1
                print("NO RESPONSE for request {} Retry after {} seconds".format(self.corr_id, sleep_time))
                time.sleep(sleep_time)
        if retry > self.retry_number:
            print("failed to register the queue to the server")
            return False
        return True

    def run(self):
        self.advertise_rabbit_log_queue_name()

        dicts = {"requestType": "send_log_data", "data": {"transferID": "a3ab570bb74a8d35479be377905dbe21", "metrics": {"timestamp": "17:11:56 09-19-2022", "networkMetrics": {"avgRttValue": 0.089, "pacingRate": 2603.1, "cwndRate": 10.0, "avgRetransmissionTimeoutValue": 204.0, "byteAck": 0.0, "segOut": 0.0, "retrans": 0.0, "mssValue": 1448.0, "ssthreshValue": 631.0, "segsIn": 0.0, "avgSendValue": 1301.6, "unackedValue": 0.0, "rcvSpace": 29200.0, "sendBufferValue": 0.0, "avgDsackDupsValue": 0.0, "avgReordSeen": 0.0}, "systemMetrics": {"rchar": "3195150", "wchar": "0", "syscr": "63", "syscw": "0", "readBytesIo": "0", "writeBytesIo": "0", "cancelledWriteBytes": "0", "pid": 10458, "ppid": 1, "pgrp": 10447, "session": 10447, "ttyNr": 0, "tpgid": -1, "flags": 1077944320, "minflt": "2236", "cminflt": "0", "majflt": "0", "cmajflt": "0", "utime": "0", "stime": "1", "cutime": "0", "cstime": "0", "priority": "20", "nice": "0", "numThreads": "1", "itrealvalue": "0", "starttime": "42968174", "vsize": "95404032", "rss": "1827", "rsslim": "18446744073709551615", "startcode": "4194304", "endcode": "4273660", "startstack": "140724610651520", "kstkesp": "140724610648184", "kstkeip": "140257518696755", "signal": "0", "blocked": "0", "sigignore": "4101", "sigcatch": "2", "wchan": 1.8446744072522971e+19, "nswap": "0", "cnswap": "0", "exitSignal": 17, "processor": 7, "rtPriority": 0, "policy": 0, "delayacctBlkioTicks": "0", "guestTime": "0", "cguestTime": "0", "startData": "6372720", "endData": "6380888", "startBrk": "29483008", "argStart": "140724610653465", "argEnd": "140724610653554", "envStart": "140724610653554", "envEnd": "140724610654175", "exitCode": 0, "cpuUsagePercentage": 0.0, "memUsagePercentage": 0.0055464655}, "bufferValueMetrics": {"tcpRcvBufferMin": "4096", "tcpRcvBufferDefault": "87380", "tcpRcvBufferMax": "6291456", "tcpSndBufferMin": "4096", "tcpSndBufferDefault": "16384", "tcpSndBufferMax": "4194304"}, "clientOstMetrics": {"reqWaittime": 0.0, "reqActive": 0.0, "readBytes": 0.0, "writeBytes": 0.0, "ostSetattr": 0.0, "ostRead": 0.0, "ostWrite": 0.0, "ostGetInfo": 0.0, "ostConnect": 0.0, "ostPunch": 0.0, "ostStatfs": 0.0, "ostSync": 0.0, "ostQuotactl": 0.0, "ldlmCancel": 0.0, "obdPing": 0.0, "pendingReadPages": 0.0, "readRPCsInFlight": 0.0}, "clientMdtMetrics": {"avgWaittimeMd": 2158.0, "inflightMd": 0.0, "unregisteringMd": 0.0, "timeoutsMd": 0.0, "reqWaittimeMd": 2511.0, "reqActiveMd": 5.0, "mdsGetattrMd": 0.0, "mdsGetattrLockMd": 542.0, "mdsCloseMd": 930.0, "mdsReadpageMd": 0.0, "mdsConnectMd": 0.0, "mdsGetRootMd": 0.0, "mdsStatfsMd": 0.0, "mdsSyncMd": 0.0, "mdsQuotactlMd": 0.0, "mdsGetxattrMd": 0.0, "mdsHsmStateSetMd": 0.0, "ldlmCancelMd": 0.0, "obdPingMd": 0.0, "seqQueryMd": 0.0, "fldQueryMd": 0.0, "closeMd": 2.0, "createMd": 0.0, "enqueueMd": 0.0, "getattrMd": 0.0, "intentLockMd": 9.0, "linkMd": 0.0, "renameMd": 0.0, "setattrMd": 0.0, "fsyncMd": 0.0, "readPageMd": 0.0, "unlinkMd": 0.0, "setxattrMd": 0.0, "getxattrMd": 0.0, "intentGetattrAsyncMd": 0.0, "revalidateLockMd": 0.0}, "resourceUsageMetrics": {"systemCpuPercent": 0.6, "systemMemoryPercent": 3.7}, "lustreOstMetrics": {"remoteOstReadBytes": 0.0, "remoteOstWriteBytes": 0.0}, "labelValue": 123}, "sequenceNumber": "3", "isSender": 1}}
        msg2 = b'\n\rsend_log_data\x12\xdc\x07\x12 bff4ac64bced562676049e3ce98c7018\x1a\xb3\x07\n\x1323:16:50 09-22-2022\x12Q\rT\xe3\xe5>\x15\x00\xe3\x98F\x1d\x00\x00\xbeC%\x00\x00IC-^\x9drC5\xc0\xc2+H=\x00\x00\x00\x00E\x00\x00\xb5DM\x00\x00\xa0AU\x00 \x97D]3/\x19Fe\x00\x004Cm\x00 \xe4Fu\xa0\xa8\x18J}\x00\x00\x00\x00\x85\x01\x00\x00\x00\x00\x1a\x92\x02\x08\x8e\x82\x83~\x10\x00\x18\xb8\x02 \x00(\x80\x80\x80\x9c\x010\x008\x00@\xda:H\x01P\xcf:X\xcf:`\x00h\xff\xff\xff\xff\xff\xff\xff\xff\xff\x01p\x80\xc2\x80\x82\x04x\xc2\x11\x80\x01\x00\x88\x01\x00\x90\x01\x00\x98\x01\x02\xa0\x01!\xa8\x01\x00\xb0\x01\x00\xb8\x01\x14\xc0\x01\x00\xc8\x01\x01\xd0\x01\x00\xd8\x01\x9e\xa0\xf2!\xe0\x01\x80\x80\xbf-\xe8\x01\xa2\x0e\xf0\x01\xff\xff\xff\xff\xff\xff\xff\xff\xff\x01\xf8\x01\x80\x80\x80\x02\x80\x02\xfc\xeb\x84\x02\x88\x02\xf0\xce\xec\xb1\xf8\xff\x1f\x90\x02\xe8\xb4\xec\xb1\xf8\xff\x1f\x98\x02\xb3\xd2\xcf\xeb\x8c\xfe\x1f\xa0\x02\x00\xa8\x02\x00\xb0\x02\x85 \xb8\x02\x02\xc1\x02\xc7(\xf7\xff\xff\xff\xefC\xc8\x02\x00\xd0\x02\x00\xd8\x02\x11\xe0\x02\x03\xe8\x02\x00\xf0\x02\x00\xf8\x02\x01\x80\x03\x00\x88\x03\x00\x90\x03\xf0\xfa\x84\x03\x98\x03\xd8\xba\x85\x03\xa0\x03\x80\x80\xe0\x07\xa8\x03\x99\xda\xec\xb1\xf8\xff\x1f\xb0\x03\xf2\xda\xec\xb1\xf8\xff\x1f\xb8\x03\xf2\xda\xec\xb1\xf8\xff\x1f\xc0\x03\xdf\xdf\xec\xb1\xf8\xff\x1f\xc8\x03\x00\xd5\x03\x00\x00\x08B\xdd\x03\xa9\xa5\xb5;"\x18\x08\x80 \x10\xd4\xaa\x05\x18\x80\x80\x80\x03 \x80 (\x80\x80\x010\x80\x80\x80\x02*\x9b\x01\t\x00\x00\x00\x00I&3A\x11\x00\x00\x00\x00\x00\xa0l@\x19\x00\x00\x00\x00\x00@\xb3A!\x00\x00\x00\x00\x00\x00\x00\x00)\x00\x00\x00\x00\x00\x00\x00\x001\x00\x00\x00\x00I&3A9\x00\x00\x00\x00\x00\x00\x00\x00A\x00\x00\x00\x00\x00\x00\x00\x00I\x00\x00\x00\x00\x00\x00\x00\x00Q\x00\x00\x00\x00\x00\x00\x00\x00Y\x00\x00\x00\x00\x00\x00\x00\x00a\x00\x00\x00\x00\x00\x00\x00\x00i\x00\x00\x00\x00\x00\x00\x00\x00q\x00\x00\x00\x00\x00\x00\x00\x00y\x00\x00\x00\x00\x00\x00\x00\x00\x81\x01\x00\x00\x00\x00\x00\x00\x10@\x89\x01\x00\x00\x00\x00\x00\x00\x00\x002\xd9\x02\t\x00\x00\x00\x00\x00X\x9d@\x11\x00\x00\x00\x00\x00\x00\x00\x00\x19\x00\x00\x00\x00\x00\x00\x00\x00!\x00\x00\x00\x00\x00\x00\x00\x00)\x00\x00\x00\x00\x00\xcc\xa1@1\x00\x00\x00\x00\x00\x00\x14@9\x00\x00\x00\x00\x00\x00\x00\x00A\x00\x00\x00\x00\x00\xa0\x7f@I\x00\x00\x00\x00\x00P\x8b@Q\x00\x00\x00\x00\x00\x00\x00\x00Y\x00\x00\x00\x00\x00\x00\x00\x00a\x00\x00\x00\x00\x00\x00\x00\x00i\x00\x00\x00\x00\x00\x00\x00\x00q\x00\x00\x00\x00\x00\x00\x00\x00y\x00\x00\x00\x00\x00\x00\x00\x00\x81\x01\x00\x00\x00\x00\x00\x00\x00\x00\x89\x01\x00\x00\x00\x00\x00\x00\x00\x00\x91\x01\x00\x00\x00\x00\x00\x00\x00\x00\x99\x01\x00\x00\x00\x00\x00\x00\x00\x00\xa1\x01\x00\x00\x00\x00\x00\x00\x00\x00\xa9\x01\x00\x00\x00\x00\x00\x00\x00\x00\xb1\x01\x00\x00\x00\x00\x00\x00\x00@\xb9\x01\x00\x00\x00\x00\x00\x00\x00\x00\xc1\x01\x00\x00\x00\x00\x00\x00\x00\x00\xc9\x01\x00\x00\x00\x00\x00\x00\x00\x00\xd1\x01\x00\x00\x00\x00\x00\x00"@\xd9\x01\x00\x00\x00\x00\x00\x00\x00\x00\xe1\x01\x00\x00\x00\x00\x00\x00\x00\x00\xe9\x01\x00\x00\x00\x00\x00\x00\x00\x00\xf1\x01\x00\x00\x00\x00\x00\x00\x00\x00\xf9\x01\x00\x00\x00\x00\x00\x00\x00\x00\x81\x02\x00\x00\x00\x00\x00\x00\x00\x00\x89\x02\x00\x00\x00\x00\x00\x00\x00\x00\x91\x02\x00\x00\x00\x00\x00\x00\x00\x00\x99\x02\x00\x00\x00\x00\x00\x00\x00\x00\xa1\x02\x00\x00\x00\x00\x00\x00\x00\x00:\n\r33\xb3?\x15\x9a\x99\xd9?B\x12\t\x00\x00\x00\x00\x00@\xb5A\x11\x00\x00\x00\x00\x00\x00\x00\x00H{ \x01(\x01*\x1d2022-09-23T04:16:50.624+00:00'

        mtrc = '{"transferID": "a3ab570bb74a8d35479be377905dbe21", "metrics": {"timestamp": "17:11:56 09-19-2022", "networkMetrics": {"avgRttValue": 0.089, "pacingRate": 2603.1, "cwndRate": 10.0, "avgRetransmissionTimeoutValue": 204.0, "byteAck": 0.0, "segOut": 0.0, "retrans": 0.0, "mssValue": 1448.0, "ssthreshValue": 631.0, "segsIn": 0.0, "avgSendValue": 1301.6, "unackedValue": 0.0, "rcvSpace": 29200.0, "sendBufferValue": 0.0, "avgDsackDupsValue": 0.0, "avgReordSeen": 0.0}, "systemMetrics": {"rchar": "3195150", "wchar": "0", "syscr": "63", "syscw": "0", "readBytesIo": "0", "writeBytesIo": "0", "cancelledWriteBytes": "0", "pid": 10458, "ppid": 1, "pgrp": 10447, "session": 10447, "ttyNr": 0, "tpgid": -1, "flags": 1077944320, "minflt": "2236", "cminflt": "0", "majflt": "0", "cmajflt": "0", "utime": "0", "stime": "1", "cutime": "0", "cstime": "0", "priority": "20", "nice": "0", "numThreads": "1", "itrealvalue": "0", "starttime": "42968174", "vsize": "95404032", "rss": "1827", "rsslim": "18446744073709551615", "startcode": "4194304", "endcode": "4273660", "startstack": "140724610651520", "kstkesp": "140724610648184", "kstkeip": "140257518696755", "signal": "0", "blocked": "0", "sigignore": "4101", "sigcatch": "2", "wchan": 1.8446744072522971e+19, "nswap": "0", "cnswap": "0", "exitSignal": 17, "processor": 7, "rtPriority": 0, "policy": 0, "delayacctBlkioTicks": "0", "guestTime": "0", "cguestTime": "0", "startData": "6372720", "endData": "6380888", "startBrk": "29483008", "argStart": "140724610653465", "argEnd": "140724610653554", "envStart": "140724610653554", "envEnd": "140724610654175", "exitCode": 0, "cpuUsagePercentage": 0.0, "memUsagePercentage": 0.0055464655}, "bufferValueMetrics": {"tcpRcvBufferMin": "4096", "tcpRcvBufferDefault": "87380", "tcpRcvBufferMax": "6291456", "tcpSndBufferMin": "4096", "tcpSndBufferDefault": "16384", "tcpSndBufferMax": "4194304"}, "clientOstMetrics": {"reqWaittime": 0.0, "reqActive": 0.0, "readBytes": 0.0, "writeBytes": 0.0, "ostSetattr": 0.0, "ostRead": 0.0, "ostWrite": 0.0, "ostGetInfo": 0.0, "ostConnect": 0.0, "ostPunch": 0.0, "ostStatfs": 0.0, "ostSync": 0.0, "ostQuotactl": 0.0, "ldlmCancel": 0.0, "obdPing": 0.0, "pendingReadPages": 0.0, "readRPCsInFlight": 0.0}, "clientMdtMetrics": {"avgWaittimeMd": 2158.0, "inflightMd": 0.0, "unregisteringMd": 0.0, "timeoutsMd": 0.0, "reqWaittimeMd": 2511.0, "reqActiveMd": 5.0, "mdsGetattrMd": 0.0, "mdsGetattrLockMd": 542.0, "mdsCloseMd": 930.0, "mdsReadpageMd": 0.0, "mdsConnectMd": 0.0, "mdsGetRootMd": 0.0, "mdsStatfsMd": 0.0, "mdsSyncMd": 0.0, "mdsQuotactlMd": 0.0, "mdsGetxattrMd": 0.0, "mdsHsmStateSetMd": 0.0, "ldlmCancelMd": 0.0, "obdPingMd": 0.0, "seqQueryMd": 0.0, "fldQueryMd": 0.0, "closeMd": 2.0, "createMd": 0.0, "enqueueMd": 0.0, "getattrMd": 0.0, "intentLockMd": 9.0, "linkMd": 0.0, "renameMd": 0.0, "setattrMd": 0.0, "fsyncMd": 0.0, "readPageMd": 0.0, "unlinkMd": 0.0, "setxattrMd": 0.0, "getxattrMd": 0.0, "intentGetattrAsyncMd": 0.0, "revalidateLockMd": 0.0}, "resourceUsageMetrics": {"systemCpuPercent": 0.6, "systemMemoryPercent": 3.7}, "lustreOstMetrics": {"remoteOstReadBytes": 0.0, "remoteOstWriteBytes": 0.0}, "labelValue": 123}'


        msg3 = "{time} {tid} {sender} {seq} {req_type} {metrics}"
        msg4 = "0.467,15478.4,312.0,201.0,691.0332870483398,500445.0,0.0,1448.0,88.0,2765.0,7739.2,210.0,29200.0,2252400,0,0,1512096014,0,1502,0,0,0,0,11762,1,11751,11751,0,-1,1077944320,2243,0,0,0,3,65,0,0,20,0,1,0,105045709,95404032,1828,18446744073709551615,4194304,4273660,140728983474352,140728983471016,140465142552883,0,0,4101,2,18446744072522970309,0,0,17,23,0,0,0,0,0,6372720,6380888,26898432,140728983481624,140728983481714,140728983481714,140728983482335,0,24.0,0.00554950143133421,4096,87380,6291456,4096,16384,4194304,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,1876.0,0.0,0.0,0.0,1923.0,5.0,0.0,335.0,721.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,2.0,0.0,0.0,0.0,9.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,1.4,3.2,0.0,184549376.0,123"

        self.check_rabbit_connection()
        while True:
            try:
                time_1 = time.time()
                dicts["@timestamp"] = datetime.now(tz=timezone.utc).isoformat(sep='T', timespec='milliseconds')
                # dicts["@timestamp"] = "2022-09-22T23:03:14.111Z" 2022-09-22T22:50:33.771Z
                # msg = json.dumps(dicts).encode('utf-8')
                msg = msg3.format(time=datetime.now(tz=timezone.utc).isoformat(sep='T', timespec='milliseconds'),
                                  tid="a3ab570bb74a8d35479be377905dbe21",
                                  sender="1",
                                  seq="3",
                                  req_type="send_log_data",
                                  metrics=mtrc)
                for i in range(self.message_rate):
                    self.rabbitmq_channel.basic_publish(exchange='', routing_key=self._rabbit_log_queue_name, body=msg)
                processing_time = time.time() - time_1
                print(processing_time)
                time.sleep(abs(1 - (processing_time % 1)))
            except StreamLostError as e:
                self.rabbitmq_channel = None
                self.rabbitmq_connection = None
                traceback.print_exc()
            except Exception as e:
                self.rabbitmq_channel = None
                self.rabbitmq_connection = None
                if self.xsub_backend_socket:
                    self.poller.unregister(self.xsub_backend_socket)
                    self.xsub_backend_socket.setsockopt(zmq.LINGER, 0)
                    self.xsub_backend_socket.close()
                    self.xsub_backend_socket = None
                traceback.print_exc()


obj = cloudStress("cluster_1", "c220g1-030601.wisc.cloudlab.us", 5672, 60)
obj.run()
