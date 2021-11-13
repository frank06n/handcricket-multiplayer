from messages import MSG, MC, MoveResult, InningsEndType
from utils import MServer, MSG_DISCON
from random import randint

class MyServer:
    def __init__(self):
        self.addr = 'localhost', 5050
        SETTINGS = MServer.create_settings(onreply=self.on_reply_from_client)

        self.server = MServer(self.addr, SETTINGS)
        print('Server online')

        if input('Use ngrok? (1 for yes): ')=='1':
            self.addr = MServer.use_ngrok(self.addr)
        
        self.print_server_details()
        self.server_client_comm()

    def print_server_details(self):
        IP, PORT = self.addr
        print('Server ip:', IP)
        print('Server port:', PORT)

    def server_client_comm(self):
        self.players = ['', None, None]

        print('\nWaiting for players...')
        self.players[1] = self.server.accept()
        print('Player 1 connected!')
        self.players[2] = self.server.accept()
        print('Player 2 connected!')

        print('\nHow many overs?')
        self.total_balls = int(input('> '))*6
        print('How many wickets per team?')
        self.total_wickets = int(input('> '))

        input('Press enter to start the match')
        while True:
            self.start_match()
            do_rematch = self.ask_for_rematch()
            if not do_rematch: break

        print('\nGame ended!')
        self.__qm(1, msg_args=(MSG_DISCON,), msg_code=MC.DISCON_P1)
        self.__qm(2, msg_args=(MSG_DISCON,), msg_code=MC.DISCON_P2)
        self.wait()
        print('Server offline')
        input('\nPress enter to close')

    def __o(self, pno):
        return 2 if pno==1 else 1

    def __qm(self, pno, msg_args, msg_code=-1):
        self.players[pno].queue_msg(MSG.combine(msg_args), msg_code)
    
    def wait(self):
        self.WAIT = True
        while self.WAIT: pass

    def stop_wait(self):
        self.WAIT = False

    def on_reply_from_client(self, msg_code, reply):
        if msg_code==MC.TOSS_CHOICE:
            self.toss_choice = int(reply)
            self.stop_wait()

        elif msg_code==MC.PLAY_CHOICE:
            self.play_choice = int(reply)
            self.stop_wait()

        elif msg_code==MC.BAT_MOVE:
            self.bat_move = int(reply)
            if self.ball_move: self.stop_wait()

        elif msg_code==MC.BALL_MOVE:
            self.ball_move = int(reply)
            if self.bat_move: self.stop_wait()

        elif msg_code==MC.REMATCH_R1:
            self.rematch_player1_response = int(reply)
            if self.rematch_player2_response!=None: self.stop_wait()

        elif msg_code==MC.REMATCH_R2:
            self.rematch_player2_response = int(reply)
            if self.rematch_player1_response!=None: self.stop_wait()

        elif msg_code==MC.DISCON_P1:
            self.players[1] = None
            print('Player 1 disconnected!')
            if not self.players[2]: self.stop_wait()

        elif msg_code==MC.DISCON_P2:
            self.players[2] = None
            print('Player 2 disconnected!')
            if not self.players[1]: self.stop_wait()


    def perform_toss(self):
        toss_player = randint(1,2)
        print(f'\nPlayer {toss_player} gets to choose heads or tails')

        args = (MSG.CHOOSE_TOSS, toss_player)
        self.__qm(toss_player, args, msg_code=MC.TOSS_CHOICE)
        self.__qm(self.__o(toss_player), args)
        self.wait()

        toss_result = randint(1,2)
        toss_win_player = toss_player if (self.toss_choice == toss_result) else self.__o(toss_player)
        print(f'Player {toss_player} chooses {"heads" if self.toss_choice==0 else "tails"}')
        print(f'Player {toss_win_player} wins toss')

        args = (MSG.CHOOSE_PLAY, self.toss_choice, toss_win_player)
        self.__qm(toss_win_player, args, msg_code=MC.PLAY_CHOICE)
        self.__qm(self.__o(toss_win_player), args)
        self.wait()

        bat_player = toss_win_player if self.play_choice==0 else self.__o(toss_win_player)
        print(f'Player {toss_win_player} chooses to {"bat" if self.play_choice==0 else "ball"}')

        del self.play_choice, self.toss_choice
        return bat_player

    def start_match(self):
        print('\nMatch begins!')
        self.__qm(1, msg_args=(MSG.MATCH_BEGINS, 1))
        self.__qm(2, msg_args=(MSG.MATCH_BEGINS, 2))

        self.bat_player = self.perform_toss()
        print(f'\nPlayer {self.bat_player} bats:')

        args = (MSG.INNINGS1_BEGIN, self.bat_player)
        self.__qm(1, args)
        self.__qm(2, args)

        self.balls_played = self.runs = self.wickets = 0
        self.target = -1

        print('')
        while True:
            self.play_ball()
            if not self.check_continue_innings():
                if not self.check_continue_match():
                    break
        
        del self.bat_player, self.bat_move, self.ball_move
        print('Match ends!')

    def play_ball(self):
        self.balls_played += 1
        self.bat_move = self.ball_move = 0
        display_score = False

        result = ''
        over_ends = 0 # False
        
        print(f'Waiting ({self.balls_played//6}.{self.balls_played%6})', end='    ')
        args = (MSG.CHOOSE_MOVE, self.balls_played)
        self.__qm(self.bat_player, args, msg_code=MC.BAT_MOVE)
        self.__qm(self.__o(self.bat_player), args, msg_code=MC.BALL_MOVE)
        self.wait()

        print(f'bat[{self.bat_move: 2d}] <->  ball[{self.ball_move: 2d}]')
        if self.bat_move == self.ball_move:
            self.runs += self.bat_move**2
            print('and its a multi...')
            display_score = True
            result = MoveResult.MULTI
        elif abs(self.bat_move-self.ball_move)==1:
            self.wickets += 1
            print('and its a wicket...')
            display_score = True
            result = MoveResult.WICKET
        else:
            self.runs += self.bat_move
            result = MoveResult.RUNS

        if self.balls_played%6==0:
            print(f'over {self.balls_played//6} ends...')
            display_score = True
            over_ends = 1 # True

        if display_score:
            print(f'Player {self.bat_player} has a score of {self.runs}/{self.wickets}\n')

        args = (MSG.MOVE_RESULT, self.balls_played, self.bat_move, self.ball_move,
             result, over_ends, self.runs, self.wickets)
        self.__qm(1, args)
        self.__qm(2, args)

    def check_continue_innings(self):
        if self.target!=-1 and self.runs>=self.target:
            print(f'Player {self.bat_player} reached target!')
            self.innings_end_type = InningsEndType.TARGET
            return False

        if self.wickets == self.total_wickets:
            print(f'Player {self.bat_player} is all out')
            self.innings_end_type = InningsEndType.WICKETS
            return False
        
        if self.balls_played == self.total_balls:
            print(f'All balls played')
            self.innings_end_type = InningsEndType.BALLS
            return False

        return True

    def check_continue_match(self):
        if self.target==-1:
            self.target = self.runs+1
            self.balls_played = self.runs = self.wickets = 0
            self.bat_player = self.__o(self.bat_player)

            print(f'Target for Player {self.bat_player} is {self.target}')
            print(f'\nPlayer {self.bat_player} bats:\n')

            args = (MSG.INNINGS2_BEGIN, self.bat_player, self.innings_end_type, self.target)
            self.__qm(1, args)
            self.__qm(2, args)
            return True
        else:
            winner, wonby = 0, ''
            tie = 0 # false

            if self.runs >= self.target:
                winner = self.bat_player
                w = self.total_wickets-self.wickets
                wonby = f'{w} wicket{"" if w==1 else "s"}'
            elif self.runs < self.target-1:
                winner = self.__o(self.bat_player)
                r = self.target-1-self.runs
                wonby = f'{r} run{"" if r==1 else "s"}'
            else:
                tie = 1 # true
            
            if tie:
                print('The match is a tie')
            elif winner:
                print(f'Player {winner} won by {wonby}')

            args = (MSG.MATCH_ENDS, self.innings_end_type, winner, wonby)
            self.__qm(1, args)
            self.__qm(2, args)

            return False
            

    def ask_for_rematch(self):
        print('\nWaiting for rematch response:')
        self.rematch_player1_response, self.rematch_player2_response = None, None
        self.__qm(1, (MSG.DO_REMATCH,), msg_code=MC.REMATCH_R1)
        self.__qm(2, (MSG.DO_REMATCH,), msg_code=MC.REMATCH_R2)
        self.wait()

        response = (1, self.rematch_player1_response, self.rematch_player2_response)
        del self.rematch_player1_response, self.rematch_player2_response

        p1r = 'wants' if response[1] else 'doesn\'t want'
        p2r = 'wants' if response[2] else 'doesn\'t want'
        print(f'Player 1 {p1r} a rematch')
        print(f'Player 2 {p2r} a rematch')

        result = 1 if all(response) else 0

        self.__qm(1, msg_args=(MSG.REMATCH_RESP, response[2], result))
        self.__qm(2, msg_args=(MSG.REMATCH_RESP, response[1], result))

        print(f'A rematch {"will" if result else "wont"} happen...')
        return bool(response)


if __name__ == '__main__':
    MyServer()