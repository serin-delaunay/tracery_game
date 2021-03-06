from xo import board, ai, token, arbiter
import base62
from game import Game

class NoughtsAndCrosses(Game):
    def __init__(self):
        self.game_over_messages = {
            'x':{
                'squashed': '#draw#',
                'loser': '#ai_win#',
                'winner': '#player_win#'
            },
            'o':{
                'squashed': '#draw#',
                'winner': '#ai_win#',
                'loser': '#player_win#'
            }
        }
    def start_states(self):
        message = "Would you like to play Noughts and Crosses?"
        start = "I'll start."
        return [('x', message+'\n')]*9 + [('x'+'.'*i + 'o', message+' '+start+'\n') for i in range(9)]
    def boardify(self, state):
        return state[0], board.Board.fromstring(state[1:])
    def options(self, state):
        player, b = self.boardify(state)
        outcome = arbiter.outcome(b, player)
        if outcome['status'] != 'in-progress':
            return []
        return [(r, c) for (r, c, p) in b if token.isempty(p)]
    def result(self, state, input):
        player, b = self.boardify(state)
        b[input[0], input[1]] = player
        next_player = token.other_token(player)
        try:
            minmax = ai.evaluate(b, next_player)
        except ValueError:
            result = [next_player + str(b)]
            return {'optimal': result, 'suboptimal': result}
        results = {'optimal': [], 'suboptimal': []}
        optimal_moves = set(tuple(minmax.positions))
        for (r,c,p) in b:
            if token.isempty(p):
                b[r,c] = next_player
                if (r,c) in optimal_moves:
                    results['optimal'].append(player + str(b))
                else:
                    results['suboptimal'].append(player + str(b))
                b[r,c] = '.'
        if not results['suboptimal']:
            results['suboptimal'] = results['optimal']
        return results
        
    def display(self, state):
        display = []
        player, b = self.boardify(state)
        outcome = arbiter.outcome(b, player)
        svg = '#init#'+''.join(
            "#{1}{0}#".format(i, p)
            for (i, (r,c,p)) in
            enumerate(self.boardify(state)[1],1)
            if not token.isempty(p))
        if outcome['status'] != 'in-progress':
            status = self.game_over_messages[player][outcome['reason']]
            return svg + status + "#display_end#"
        else:
            return svg + "#display#"
    def encode(self, state):
        player, b = self.boardify(state)
        board_str = player + str(b)
        board_ternary = board_str.translate(str.maketrans({'.':'0', 'x':'1', 'o':'2'}))
        board_num = int(board_ternary, 3)
        return base62.encode(board_num)
    def display_input(self, input):
        r, c = input
        return str(r*3 + c - 3)
    def grammar(self):
        grammar = {}
        for r in range(3):
            for c in range(3):
                i = 3*r+c+1
                grammar['x'+str(i)] = '[{0}:<path d="M {1}20 {2}20 l 60 60" stroke="black" stroke-width="13" stroke-linecap="round" /><path d="M {1}80 {2}20 l -60 60" stroke="black" stroke-width="13" stroke-linecap="round" />][{0}a:cross]'.format(i, c, r)
                grammar['o'+str(i)] = '[{0}:<circle cx="{1}50" cy="{2}50" r="30" stroke="black" stroke-width="13" fill="none" />][{0}a:nought]'.format(i, c, r)
        grammar['init'] = ''.join('[{}:]'.format(i) for i in range(1,10)) + ''.join('[{}a:blank]'.format(i) for i in range(1,10))
        grammar['display'] = "#svg##alt#Code: #code#\nOptions: #options#"
        grammar['display_end'] = "#svg##alt#"
        grammar['draw'] = [
            "It's a draw#punctuation#",
            "We both lose#punctuation#",
            "We both win#punctuation#"
        ]
        grammar['ai_win'] = [
            "#AI# win#punctuation#",
            "A winner is me#punctuation#",
            "I've won#punctuation#",
            "You lose#punctuation#",
            "You've lost#punctuation#"
        ]
        grammar['AI'] = [
            "I",
            "AI",
            "CPU",
            "Tracery",
            "Bot",
            "Computer",
            "Robot"
        ]
        grammar['player_win'] = [
            "You win#punctuation#",
            "You've won#punctuation#"
            "#AI# lose#punctuation#",
            "#AI# lost#punctuation#",
            "#AI# lose#punctuation#",
        ]
        grammar['result'] = ['#optimal#']*29 + ['#suboptimal#']
        grammar['punctuation'] = ['?', '.', '.', '.', '!', '!', '!', '!']
        grammar['svg'] = '{svg <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" width="533" height="300"><g width="300" height="300" transform="translate(116.67 0)"><rect width="300" height="300" rx="17" ry="17" fill="white"/><path d="M 100 15 l 0 270" stroke="black" stroke-width="13" stroke-linecap="round" /><path d="M 200 15 l 0 270" stroke="black" stroke-width="13" stroke-linecap="round" /><path d="M 15 100 l 270 0" stroke="black" stroke-width="13" stroke-linecap="round" /><path d="M 15 200 l 270 0" stroke="black" stroke-width="13" stroke-linecap="round" />#1##2##3##4##5##6##7##8##9#</g></svg>}'
        grammar['alt'] = '{alt row 1 #1a# #2a# #3a# row 2 #4a# #5a# #6a# row 3 #7a# #8a# #9a#}'
        return grammar

if __name__ == '__main__':
    NoughtsAndCrosses().tracerise('xo')
