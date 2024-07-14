import threading
import socket


class BaseStationClient(threading.Thread):
    def __init__(self):
        super(BaseStationClient, self).__init__()
        
        # socket‚Ìì¬
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

        return

    def run(self,):
        
        # player_server‚É©g‚Ìó‘Ô‚ğ‘—M‚·‚é
        
        # player_server‚Ì•ÔM‚ğó‚¯æ‚é
        
        
        return
