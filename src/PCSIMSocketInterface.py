import socket
from Utilities import Utilities
from enum import Enum

socket_message_req = bytearray(b'\x01')
socket_message_err = bytearray(b'\x02')


class PCSIMSocketInterface:
    class PCSIMSocketInterfaceRequestStatus(Enum):
        SUCCESSFUL = 0,
        ERROR_SCREENSHOT = 1,
        ERROR_UNKNOWN = 2

    def __init__(self):
        self.sock_tx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock_rx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock_rx.bind(Utilities.get_host_socket_rx_conf())

    def request_screenshot(self) -> PCSIMSocketInterfaceRequestStatus:
        request_successful = self.PCSIMSocketInterfaceRequestStatus.SUCCESSFUL

        message = socket_message_req
        self.sock_tx.sendto(message, Utilities.get_host_socket_tx_conf())

        received_data = self.sock_rx.recv(1)
        if received_data == socket_message_req:
            request_successful = self.PCSIMSocketInterfaceRequestStatus.SUCCESSFUL

        elif received_data == socket_message_err:
            request_successful = self.PCSIMSocketInterfaceRequestStatus.ERROR_SCREENSHOT

        else:
            request_successful = self.PCSIMSocketInterfaceRequestStatus.ERROR_UNKNOWN

        return request_successful
