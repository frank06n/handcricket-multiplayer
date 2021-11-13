import socket
import threading
import time


class MSettings:
    def __init__(self, ip='localhost', port=5050):
        self.ip = ip
        self.port = port

        self.header = 8
        self.format = 'utf-8'
        self.disconnect_msg = '+DISCONNECT'
        self.null_msg = '+NULL'




class MServer:
    def __init__(self, settings, onreply, use_ngrok=False):
        self.settings = settings
        self.onreply = onreply
        self.addr = self.settings.ip, self.settings.port

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(self.addr)
        self.server.listen()

        if use_ngrok:
            from pyngrok import ngrok

            ssh_tunnel = ngrok.connect(self.addr[1], "tcp")
            url = ssh_tunnel.public_url
            i_0 = url.find('//')+2
            i_1 = url.find('io:')+2
            ip = url[i_0:i_1]
            port = int(url[i_1+1:])
            self.addr = (ip, port)


    def accept(self):
        conn, addr = self.server.accept()
        return MClientHandler(conn, self.settings, self.onreply)




class MMsgHandler:
    def __init__(self, conn, settings):
        self.conn = conn
        self.format = settings.format
        self.header = settings.header

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




class MClientHandler:
    def __init__(self, conn, settings, onreply):
        self.settings = settings
        self.onreply = onreply
        self.msg_handle = MMsgHandler(conn, settings)
        self.msg_queue = []

        threading.Thread(target=self.msg_loop).start()

    def queue_msg(self, msg, msg_code=None):
        self.msg_queue.append((msg, msg_code))

    def msg_loop(self):
        while True:
            if self.msg_queue:
                msg, msg_code = self.msg_queue[0]
                del(self.msg_queue[0])

                self.msg_handle.send_message(msg)
                
                reply = self.msg_handle.recv_message()
                if not reply:
                    reply = self.msg_handle.recv_message()

                self.onreply(msg_code, reply)

                if reply == self.settings.disconnect_msg:
                    break

        self.msg_handle.close()




class MClient:
    def __init__(self, onreceive, data, settings):
        self.onreceive = onreceive
        self.settings = settings
        self.data = data
        self.addr = self.settings.ip, self.settings.port

        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect(self.addr)

        self.msg_handle = MMsgHandler(conn, settings)

    def msg_loop(self):
        while True:
            msg = self.msg_handle.recv_message()
            if msg:
                reply = self.onreceive(msg, self.data)

                if msg == self.settings.disconnect_msg:
                    self.msg_handle.send_message(self.settings.disconnect_msg)
                    break
                elif reply:
                    self.msg_handle.send_message(reply)
                else:
                    self.msg_handle.send_message(self.settings.null_msg)
        
        self.msg_handle.close()