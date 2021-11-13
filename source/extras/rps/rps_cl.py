from CONNECTION import *
import re

class Data:
    def __init__(self):
        self.name = None
        self.ip = None
        self.port = None
        self.player_no = None
        self.opp_name = None

print('ROCK PAPER SCISSORS')

data = Data()
while True:
    data.name = input('Enter name: ').strip()
    if re.match('\\A[a-zA-Z0-9_]{4,16}\\Z', data.name): break
    print('[BAD INPUT] name must have 4-16 characters and only letters, numbers and underscore')

data.ip = input('Enter ip: ')
data.port = int(input('Enter port: '))

client_settings = MSettings(ip=data.ip, port=data.port) if data.ip and data.port else MSettings()


def on_receive_message(msg, data):
    args = msg.split(' ')

    if args[0] == 'name':
        return data.name

    elif args[0] ==  'init':
        server_name = args[1]
        no_of_r = args[2]
        data.player_no = args[3]
        data.opp_name = args[4]

        print(f'\nServer name: {server_name}')
        print(f'No of rounds: {no_of_r}')
        print(f'You are [Player {data.player_no}]')
        print(f'Opponent is [{data.opp_name}]')

        print(f'\nMatch starts...')
        print('Enter 0 for rock, 1 for paper, 2 for scissors')

    elif args[0] == 'move?':
        round = args[1]
        while True:
            move = input(f'\nRound {round}> ')
            if move=='0' or move=='1' or move=='2': break
            print('[BAD INPUT] Enter 0 for rock, 1 for paper, 2 for scissors')
        return move

    elif args[0] == 'result':
        result = int(args[1])
        if result==0:
            print('It was a draw')
        else:
            print(f'{"You" if result==int(data.player_no) else data.opp_name}[{result}] won')

    elif args[0] == 'ends':
        finalr = int(args[1])
        print(f'\nMatch ends')
        winner = 0

        if finalr==0:pass
        else: winner = 1 if finalr>0 else 2

        if winner==0:
            print('It was a draw')
        else:
            print(f'{"You" if winner==data.player_no else data.opp_name}[{winner}] won the match')

    elif args[0] == client_settings.disconnect_msg:
        print(f'\n Server disconnected')


client = MClient(on_receive_message, data, client_settings)
print('\nConnected to server')

print('Communicating...')
client.msg_loop()