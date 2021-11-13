import socket
from _thread import start_new_thread


MSG_DISCON = ';discon' # disconnect message
MSG_NULL   = ';null'   # null message


class MServer:
    def __init__(self, addr, settings):
        self.settings = settings

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(addr)
        self.server.listen()

    @staticmethod
    def create_settings(format='utf-8', header=10, onreply=None):
        return format, header, onreply

    @staticmethod
    def get_addr_from_url(url):
        i_0 = url.find('//')+2
        i_1 = url.find('io:')+2
        return url[i_0:i_1], int(url[i_1+1:])

    @staticmethod
    def use_ngrok(addr):
        from pyngrok import ngrok

        ssh_tunnel = ngrok.connect(addr[1], "tcp")
        return MServer.get_addr_from_url(ssh_tunnel.public_url)
        
    def accept(self):
        conn, addr = self.server.accept()
        return MS2CSocket(conn, self.settings)


class MMsgHandler:
    def __init__(self, conn, format, header):
        self.conn = conn
        self.format = format
        self.header = header

    def send_message(self, msg):
        msg = msg.encode(self.format)

        msg_header = str(len(msg)).encode(self.format)
        msg_header += b' ' * (self.header - len(msg_header))

        self.conn.send(msg_header)
        self.conn.send(msg)

    def recv_message(self):
        msg_header = self.conn.recv(self.header).decode(self.format)

        if msg_header:
            msg = self.conn.recv(int(msg_header)).decode(self.format)
            return msg

    def close(self):
        self.conn.close()


class MS2CSocket:
    def __init__(self, conn, settings):
        format, header, self.onreply = settings
        self.msg_handle = MMsgHandler(conn, format, header)
        self.msg_queue = []

        start_new_thread(self.__async_msg_loop, ())

    def queue_msg(self, msg, msg_code=-1):
        self.msg_queue.append((msg, msg_code))

    def __pop_queue(self):
        msg, msg_code = self.msg_queue[0]
        del(self.msg_queue[0])
        return msg, msg_code

    def __get_valid_reply(self):
        reply = self.msg_handle.recv_message()
        if not reply:
            reply = self.msg_handle.recv_message()
        return reply

    def __async_msg_loop(self):
        while True:
            if self.msg_queue:
                msg, msg_code = self.__pop_queue()
                self.msg_handle.send_message(msg)
                reply = self.__get_valid_reply()
                self.onreply(msg_code, reply)
                if reply == MSG_DISCON: break

        self.msg_handle.close()



class MC2SSocket:
    def __init__(self, addr, onreceive, format='utf-8', header=10):
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect(addr)

        self.onreceive = onreceive
        self.msg_handle = MMsgHandler(conn, format, header)

    def start_msg_loop(self):
        while True:
            if not self.__msg_loop(): break
        self.msg_handle.close()

    def __msg_loop(self):
        msg = self.msg_handle.recv_message()
        if msg:
            reply = self.onreceive(msg)
            if msg == MSG_DISCON:
                self.msg_handle.send_message(MSG_DISCON)
                return False
            self.msg_handle.send_message(reply if reply else MSG_NULL)
        return True