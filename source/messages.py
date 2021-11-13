class MSG:
    SEP = '|'
    MATCH_BEGINS   = 'mb'  #args: player_no
    CHOOSE_TOSS    = 'ct'  #args: toss_player
    CHOOSE_PLAY    = 'cp'  #args: toss_choice, toss_win_player
    INNINGS1_BEGIN = 'i1b' #args: bat_player
    CHOOSE_MOVE    = 'cm'  #args: ball_no
    MOVE_RESULT    = 'mr'  #args: ball_no, bat_move, ball_move, result, over_ends, runs, wickets
    INNINGS2_BEGIN = 'i2b' #args: bat_player, i_end_type, target
    MATCH_ENDS     = 'me'  #args: i_end_type, winner, wonby
    DO_REMATCH     = 'dr'  
    REMATCH_RESP   = 'rr'  #args: opp_response, result

    @staticmethod
    def combine(args):
        msg = ''
        for i, arg in enumerate(args):
            msg += str(arg)
            if i+1 < len(args): msg += MSG.SEP
        return msg

    @staticmethod
    def decombine(msg):
        return msg.split(MSG.SEP)

class MC:
    TOSS_CHOICE = 0
    PLAY_CHOICE = 1
    BAT_MOVE    = 2
    BALL_MOVE   = 3
    REMATCH_R1  = 4
    REMATCH_R2  = 5
    DISCON_P1   = 6
    DISCON_P2   = 7

class MoveResult:
    RUNS   = 'r'
    WICKET = 'w'
    MULTI  = 'm'

class InningsEndType:
    WICKETS = 'w'
    BALLS   = 'b'
    TARGET  = 't' #only for innings 2; more priority than BALLS