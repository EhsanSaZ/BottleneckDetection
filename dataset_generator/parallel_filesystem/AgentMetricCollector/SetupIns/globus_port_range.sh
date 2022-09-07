# place this in /etc/profile.d
# running server globus-gridftp-server -c gridftp.conf -aa --data-interface 10.10.2.3
# running client globus-url-copy src_path ftp://ip:port/path
export GLOBUS_TCP_PORT_RANGE=50000,51000
export GLOBUS_TCP_SOURCE_RANGE=40000,41000
