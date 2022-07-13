class TransferValidationStrategy_2:
    def __init__(self):
        pass

    @staticmethod
    def in_range(number, a_range):
        return a_range[0] <= number <= a_range[1]

    def is_transfer_valid(self, transfer_local_address_ip, transfer_local_address_port,
                          transfer_peer_address_ip, transfer_peer_address_port,
                          valid_local_ip_addr_list, valid_peer_ip_addr_list,
                          valid_send_port_range, valid_receive_port_range):
        return self.is_valid_send_transfer(transfer_local_address_ip, transfer_local_address_port,
                                           transfer_peer_address_ip, transfer_peer_address_port,
                                           valid_local_ip_addr_list, valid_peer_ip_addr_list,
                                           valid_send_port_range,
                                           valid_receive_port_range) or self.is_valid_receive_transfer(
            transfer_local_address_ip, transfer_local_address_port,
            transfer_peer_address_ip, transfer_peer_address_port,
            valid_local_ip_addr_list, valid_peer_ip_addr_list,
            valid_send_port_range, valid_receive_port_range)

    def is_valid_send_transfer(self, transfer_local_address_ip, transfer_local_address_port,
                               transfer_peer_address_ip, transfer_peer_address_port,
                               valid_local_ip_addr_list, valid_peer_ip_addr_list, valid_send_port_range,
                               valid_receive_port_range):
        if transfer_local_address_ip in valid_local_ip_addr_list and transfer_peer_address_ip in valid_peer_ip_addr_list \
                and self.in_range(int(transfer_local_address_port), valid_send_port_range) \
                and self.in_range(int(transfer_peer_address_port), valid_receive_port_range):
            return True
        return False

    def is_valid_receive_transfer(self, transfer_local_address_ip, transfer_local_address_port,
                                  transfer_peer_address_ip, transfer_peer_address_port,
                                  valid_local_ip_addr_list, valid_peer_ip_addr_list, valid_send_port_range,
                                  valid_receive_port_range):
        if transfer_local_address_ip in valid_local_ip_addr_list and transfer_peer_address_ip in valid_peer_ip_addr_list \
                and self.in_range(int(transfer_local_address_port), valid_receive_port_range) \
                and self.in_range(int(transfer_peer_address_port), valid_send_port_range):
            return True
        return False
