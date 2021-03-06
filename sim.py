from game import Game
from sim_engine import SimEngine, SimState, Colour
from math import sin, cos, pi
import base62


class Sim(Game):
    def __init__(self):
        self.engine = SimEngine()
        self.engine.map_state_space()
        self.engine.perform_minimax()
    def start_states(self):
        initial_state = SimState.initial_state()
        details = self.engine.state_details[initial_state]
        second_state = details.successors[details.optimal_play]
        return [
            (initial_state, "Would you like to play a game of Sim?\n"),
            (second_state, "Would you like to play a game of Sim? I'll start.\n")
            ]
    def options(self, state):
        return list(self.engine.state_details[state].successors.keys())
    def result(self, state, input):
        next_state = self.engine.state_details[state].successors[input]
        next_details = self.engine.state_details[next_state]
        if next_details.in_progress:
            next_state = next_details.successors[next_details.optimal_play]
        return {'only': [next_state]}
    def display(self, state):
        set_colours = ''.join(f'[{e}:#{c.name[0]}{e}#]' for (e, c) in enumerate(state.colours) if c is not Colour.empty)
        return '#init#' + set_colours + '#display#'
        
    def encode(self, state):
        state_string = state.encode()
        state_ternary = state_string.translate(str.maketrans({'r':'0', 'b':'1', 'e':'2'}))
        state_num = int(state_ternary, 3)
        return base62.encode(state_num)
    def grammar(self):
        grammar = {}
        positions = {v: (1000*cos((v+4)*pi/3), 1000*sin((v+4)*pi/3)) for v in self.engine.vertices}
        for edge in self.engine.edges:
            grammar[f'r{self.engine.edge_ids[edge]}'] = f'<line x1="{positions[edge[0]][0]}" y1="{positions[edge[0]][1]}" x2="{positions[edge[1]][0]}" y2="{positions[edge[1]][1]}" stroke="red" stroke-width="20" />'
            grammar[f'b{self.engine.edge_ids[edge]}'] = f'<line x1="{positions[edge[0]][0]}" y1="{positions[edge[0]][1]}" x2="{positions[edge[1]][0]}" y2="{positions[edge[1]][1]}" stroke="blue" stroke-width="20" />'
            grammar[f'e{self.engine.edge_ids[edge]}'] = f'<line x1="{positions[edge[0]][0]}" y1="{positions[edge[0]][1]}" x2="{positions[edge[1]][0]}" y2="{positions[edge[1]][1]}" stroke="black" stroke-width="15" />'
        grammar['svg'] = f'''
{{svg <svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="960" height="540" id="Complete graph K6">
<rect width="100%" height="100%" fill="none"/>
<circle cx = "480" cy="270" r="270" stroke="none" fill="white"/>
<g transform="translate(480 270) scale(0.22 0.22)">
#0##1##2##3##4##5##6##7##8##9##10##11##12##13##14#
<g style="fill:green;stroke:black;stroke-width:5">
<circle cx="{positions[0][0]}" cy="{positions[0][1]}" r="35"/>
<circle cx="{positions[1][0]}" cy="{positions[1][1]}" r="35"/>
<circle cx="{positions[2][0]}" cy="{positions[2][1]}" r="35"/>
<circle cx="{positions[3][0]}" cy="{positions[3][1]}" r="35"/>
<circle cx="{positions[4][0]}" cy="{positions[4][1]}" r="35"/>
<circle cx="{positions[5][0]}" cy="{positions[5][1]}" r="35"/>
</g>
<g transform="scale(1.128 1.128)" font-family="Verdana" font-size="126" text-anchor="middle">
<text>
<tspan x="{positions[0][0]}" y="{positions[0][1]}" alignment-baseline="central">1</tspan>
<tspan x="{positions[1][0]}" y="{positions[1][1]}" alignment-baseline="central">2</tspan>
<tspan x="{positions[2][0]}" y="{positions[2][1]}" alignment-baseline="central">3</tspan>
<tspan x="{positions[3][0]}" y="{positions[3][1]}" alignment-baseline="central">4</tspan>
<tspan x="{positions[4][0]}" y="{positions[4][1]}" alignment-baseline="central">5</tspan>
<tspan x="{positions[5][0]}" y="{positions[5][1]}" alignment-baseline="central">6</tspan>
</text>
</g>
</g>
</svg>}}
'''.replace('\n','')
        grammar['alt'] = ''
        grammar['display'] = "#svg##alt#Code: #code#\nOptions: #options#"
        grammar['init'] = ''.join(f'[{e}:#e{e}#]' for e in range(len(self.engine.edges)))
        grammar['result'] = '#only#'
        return grammar
    def display_input(self, input):
        return ' '.join(str(v+1) for v in self.engine.edges[input])

if __name__ == '__main__':
    Sim().tracerise('sim')
