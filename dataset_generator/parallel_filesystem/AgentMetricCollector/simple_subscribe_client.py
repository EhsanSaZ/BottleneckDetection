import zmq

# Socket to talk to server
context = zmq.Context()
socket = context.socket(zmq.SUB)

print ("Collecting updates from weather server...")
socket.connect ("tcp://10.10.2.1:%s" % "5556")
socket.connect ("tcp://10.10.2.2:%s" % "5557")

#topicfilter = "10001"
socket.setsockopt_string(zmq.SUBSCRIBE, '')

# Process 5 updates
total_value = 0
while (True):
    #string = socket.recv_multipart()
    #print (string)
    string = socket.recv_json()
    print(string)
    #dict = json.load(str(string))
    #print (dict)
    #topic, messagedata = string.split()
    #total_value += int(messagedata)
    #print (topic, messagedata)

    #print ("Average messagedata value for topic '%s' was %dF" % (topicfilter, total_value / update_nbr))

