from utils import MC2SSocket, MSG_DISCON
from messages import MSG, MoveResult, InningsEndType

class MyClient(MC2SSocket):
    def __init__(self):
        IP = input('Enter server ip: ')
        PORT = int(input('Enter server port: '))

        print('\nLooking for the server...')
        super().__init__((IP if IP else 'localhost', PORT), onreceive=self.__on_receive_msg)
        print('Connected to server!')

        self.start_msg_loop()
        input('\nPress enter to close')

    def __batter(self, you_suff='', opp_suff=''):
        return ('You'+you_suff) if self.player_no==self.bat_player else ('Opponent'+opp_suff)

    def __on_receive_msg(self, msg):
        #print('[DEBUG] msg received:', msg)
        args = MSG.decombine(msg)

        if args[0]==MSG.MATCH_BEGINS:
            self.player_no = int(args[1])
            #print('[DEBUG] my player no:', self.player_no)

        elif args[0]==MSG.CHOOSE_TOSS:
            self.toss_player = int(args[1])
            if self.player_no==self.toss_player:
                print('\nYou get to choose heads or tails')
                toss_choice = input('Enter 0 for heads, 1 for tails: ')
                return toss_choice
            print('\nOpponent gets to choose heads or tails')

        elif args[0]==MSG.CHOOSE_PLAY:
            toss_choice, toss_win_player = int(args[1]), int(args[2])
            if self.player_no!=self.toss_player:
                print(f'Opponent chose {"heads" if toss_choice==0 else "tails"}')
            del self.toss_player

            batter = "\nYou" if self.player_no==toss_win_player else "Opponent"
            print(f'{batter} won the toss')
            if self.player_no==toss_win_player:
                print('You get to choose bat or ball')
                play_choice = input('Enter 0 for bat, 1 for ball: ')
                return play_choice

        elif args[0]==MSG.INNINGS1_BEGIN:
            self.bat_player = int(args[1])
            print('\n1st innings begin')
            print(f'{self.__batter()} will bat:')

        elif args[0]==MSG.CHOOSE_MOVE:
            ball_no = int(args[1])
            print(f'\nWaiting ({ball_no//6}.{ball_no%6})', end=' ')
            move = int(input('Enter your move: '))
            #TODO add check for move
            return str(move)

        elif args[0]==MSG.MOVE_RESULT:
            ball_no   = int(args[1])
            bat_move  = int(args[2])
            ball_move = int(args[3])
            result    =     args[4]
            over_ends = int(args[5])
            runs      = int(args[6])
            wickets   = int(args[7])
            
            display_score = over_ends or result!=MoveResult.RUNS
            print(f'bat[{bat_move: 2d}] <->  ball[{ball_move: 2d}]', end=' ')

            if result==MoveResult.MULTI:
                print('and its a multi...', end=' ')
            elif result==MoveResult.WICKET:
                print('and its a wicket...', end=' ')
            if over_ends:
                print(f'over {ball_no//6} ends...', end=' ')
            
            print('')
            if display_score:
                print(f'{self.__batter(" have", " has")} a score of {runs}/{wickets}')
            
        elif args[0]==MSG.INNINGS2_BEGIN:
            new_bat_player  = int(args[1])
            i_end_type      =     args[2]
            target          = int(args[3])

            if i_end_type==InningsEndType.WICKETS:
                print(f'\n{self.__batter(" are", " is")} all out')
            elif i_end_type==InningsEndType.BALLS:
                print('\nAll balls played')
            else:
                raise Exception('Wrong innings end type for 1st innings')

            self.bat_player = new_bat_player

            print(f'Target for {self.__batter()} is {target}')
            print(f'\n{self.__batter()} will bat:')

        if args[0]==MSG.MATCH_ENDS:
            i_end_type =     args[1]
            winner     = int(args[2])
            wonby      =     args[3]

            if i_end_type==InningsEndType.WICKETS:
                print(f'\n{self.__batter(" are", " is")} all out')
            elif i_end_type==InningsEndType.BALLS:
                print('\nAll balls played')
            elif i_end_type==InningsEndType.TARGET:
                print(f'\n{self.__batter()} reached target! ')
            else:
                raise Exception('Wrong innings end type for 1st innings')

            if winner:
                print(f'{"You" if winner==self.player_no else "Opponent"} won by {wonby}')
            else:
                print('The match is a tie')

            del self.bat_player, self.player_no
            print('Match ends!')

        if args[0]==MSG.DO_REMATCH:
            response = input('\nDo you want a rematch? (1 for yes):')=='1'
            return '1' if response else '0'

        if args[0]==MSG.REMATCH_RESP:
            opp_response = int(args[1])
            result       = int(args[2])
            print(f'Opponent {"wanted" if opp_response else "didnt want"} a rematch')
            print(f'A rematch {"will" if result else "wont"} happen...')
            if not result: print('\nGame ended!')

        if msg==MSG_DISCON:
            print('Server disconnected!')


if __name__ == '__main__':
    MyClient()