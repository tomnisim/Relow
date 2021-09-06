import socket
import pickle

from kivy.app import App
import threading
from kivymd.toast import toast
from kivy.lang import Builder
from twisted.internet import reactor, protocol

from Backend_controller import Backend_controller
from Req_Answers import Req_Answers
from kivy.storage.jsonstore import JsonStore
# from Backend_controller import Backend_controller
from windows.mainWindow import TestApp


class Struct(object):
    def __init__(self, **entries):
        self.__dict__.update(entries)

class OurClient(protocol.Protocol):
    """Once connected, send a message, then print the result."""

    def connectionMade(self):
        self.transport.write(b"hello, world!")

    def dataReceived(self, data):
        to_send = req_answers.get_request()
        print(to_send, 'step 11111\n')
        message = pickle.dumps(to_send)
        print(message, 'step 2\n')

        self.transport.write.send(message)
        print("ans", "step 3")
        print(type("ans"))
        decoded_ans = Struct(**(pickle.loads("ans")))
        if decoded_ans.message == 'EXIT':
            ex()
            req_answers.add_answer(decoded_ans)
            return
        req_answers.add_answer(decoded_ans)

    def connectionLost(self, reason):
        print("connection lost")


class OurFactory(protocol.ClientFactory):
    protocol = OurClient

    def clientConnectionFailed(self, connector, reason):
        print("Connection failed - goodbye!")
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        print("Connection lost - goodbye!")
        reactor.stop()



def net():
    f = OurFactory()
    reactor.connectTCP("localhost", 4000, f)
    reactor.run()


def network(**kwargs):
    # --------------- connect to Server ---------------------------------
    print(kwargs['arg1'])
    print("start thread work")
    ClientSocket = socket.socket()
    host = '127.0.0.1'
    port = 4000
    print('Waiting for connection..')
    try:
        ClientSocket.connect((host, port))
    except socket.error as e:
        print(str(e))

    # response = ClientSocket.recv(1024)
    # response1 = pickle.loads(response)
    # print(response1)


    # --------------- init the fields ---------------------------------



    # main Window as a Thread
    # mainWindow = MainWindow()

    while True:
        to_send = req_answers.get_request()
        print(to_send, 'step 11111\n')
        message = pickle.dumps(to_send)
        print(message, 'step 2\n')

        ClientSocket.send(message)
        # if to_send['op'] == 2:
        #     ClientSocket.close()2169-+





        #     App.get_running_app().stop()
        #     break
        ans = ClientSocket.recv(4400)
        print(ans, "step 3")
        print(type(ans))
        decoded_ans = Struct(**(pickle.loads(ans)))
        if decoded_ans.message == 'EXIT':

            ex()
            req_answers.add_answer(decoded_ans)
            return
        req_answers.add_answer(decoded_ans)


def ex():
    App.get_running_app().stop()

if __name__ == '__main__':
    Builder.load_file('windows/mainWindow.kv')
    Builder.load_file('windows/managerWindow.kv')
    Builder.load_file('windows/connectWindow.kv')
    Builder.load_file('windows/accountWindow.kv')
    Builder.load_file('windows/searchWindow.kv')
    Builder.load_file('windows/addofferWindow.kv')
    Builder.load_file('windows/offers_list.kv')
    store = JsonStore('hello.json')
    a = OurClient()
    req_answers = Req_Answers()
    t1 = threading.Thread(target=lambda:network(arg1=a))
    t1.start()
    controller = Backend_controller(req_answers, store, a)
    TestApp( controller).run()



