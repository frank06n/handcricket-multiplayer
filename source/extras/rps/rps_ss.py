from CONNECTION import *



database = {}

def on_reply_message(msg_code, reply):
    if msg_code == None:
        return
    else:
        database[msg_code] = reply



print('ROCK PAPER SCISSORS')
SERVER_NAME = input('Enter server name: ')
NO_OF_R = int(input('Enter no of rounds: '))

default_settings = MSettings()
server = MServer(default_settings, on_reply_message, use_ngrok=True)

print('\nServer online')
print(f'Server ip: {server.addr[0]}')
print(f'Server port: {server.addr[1]}')

print('\nWaiting for player 1')
player1 = server.accept()
print('Player 1 connected')

print(('Waiting for Player 2'))
player2 = server.accept()
print('Player 2 connected')

database['p1name'] = None
database['p2name'] = None

player1.queue_msg('name', msg_code='p1name')
player2.queue_msg('name', msg_code='p2name')

while not (database['p1name'] and database['p2name']): pass

p1name = database['p1name']
p2name = database['p2name']

player1.queue_msg(f'init {SERVER_NAME} {NO_OF_R} 1 {p2name}')
player2.queue_msg(f'init {SERVER_NAME} {NO_OF_R} 2 {p1name}')

print(f'\nPlayers are {p1name}[1], {p2name}[2]')
print('Match starts...')

points = [0,0]

for i in range(0, int(NO_OF_R)):
    round = i+1
    print(f'\nRound {round}> waiting for players..')

    database['p1move'] = None
    database['p2move'] = None

    player1.queue_msg(f'move? {round}', msg_code='p1move')
    player2.queue_msg(f'move? {round}', msg_code='p2move')
    
    while not (database['p1move'] and database['p2move']): pass

    '''0->rock, 1->paper, 2->scissors'''
    p1move = int(database['p1move'])
    p2move = int(database['p2move'])

    result = 0
    #region Calculating result
    diff = p1move-p2move

    # 0-> draw, 1-> player 1 wins, 2-> player 2 wins
    if abs(diff)==1:
        result=1 if diff>0 else 2
    elif abs(diff)==2:
        result=1 if diff<0 else 2
    #endregion

    if result==0:
        print('It was a draw')
        points[0] += 1
        points[1] += 1
    else:
        print(f'{p1name if result==1 else p2name}[{result}] wins')
        points[result-1] += 1

    player1.queue_msg(f'result {result}')
    player2.queue_msg(f'result {result}')


print('\nMatch ends...')
finalr = points[0]-points[1]

player1.queue_msg(f'ends {finalr}')
player2.queue_msg(f'ends {finalr}')


if finalr==0:
    print('The match is a draw')
elif finalr>0:
    print(f'{p1name}[1] won the match')
else:
    print(f'{p2name}[2] won the match')


player1.queue_msg(server.settings.disconnect_msg)
player2.queue_msg(server.settings.disconnect_msg)

print('\nPlayers disconnected')