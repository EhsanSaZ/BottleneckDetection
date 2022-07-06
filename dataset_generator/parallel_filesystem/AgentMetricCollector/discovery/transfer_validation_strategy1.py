class TransferValidation_strategy_1:
    def __init__(self):
        pass

    @staticmethod
    def in_range(number, a_range):
        return a_range[0] <= number <= a_range[1]

    def is_transfer_valid(self, transfer_local_address_ip, transfer_local_address_port,
                          transfer_peer_address_ip, transfer_peer_address_port,
                          valid_src_ip_addr, valid_src_port_range,
                          valid_dst_ip_addr, valid_dst_port_range):
        if transfer_local_address_ip == valid_src_ip_addr and \
                self.in_range(int(transfer_local_address_port), valid_src_port_range) and \
                transfer_peer_address_ip == valid_dst_ip_addr and \
                self.in_range(int(transfer_peer_address_port), valid_dst_port_range):
            return True
        else:
            return False
