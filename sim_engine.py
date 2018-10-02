import networkx
from typing import NamedTuple, Tuple, Optional, Dict
from enum import Enum
from math import copysign
from itertools import combinations, chain, count
from dataclasses import dataclass, field
from collections import defaultdict
from tqdm import tqdm

class Colour(Enum):
    empty = 0
    red = 1
    blue = 2
    @classmethod
    def iter_nonempty(cls):
        yield cls.red
        yield cls.blue

class Player(Enum):
    red = False
    blue = True
    def change(self):
        return Player(not self.value)
    def colour(self):
        return Colour.blue if self.value else Colour.red
    def win_value(self):
        return 1000 if self.value else -1000
    def optimiser(self):
        return max if self.value else min
    def __str__(self):
        return '{} player'.format(self.name).capitalize()

class SimState(NamedTuple):
    player: Player
    colours: Tuple[
        Colour, Colour, Colour, Colour, Colour,
        Colour, Colour, Colour, Colour,
        Colour, Colour, Colour,
        Colour, Colour,
        Colour
    ]
    @classmethod
    def initial_state(cls):
        return cls(Player.red, (Colour.empty,)*15)
    def options(self):
        return (i for (i, c) in enumerate(self.colours) if c is Colour.empty)
    def apply(self, index):
        return SimState(self.player.change(), self.colours[:index] + (self.player.colour(),) + self.colours[index+1:])
    def __str__(self):
        return '{}, {}'.format(''.join(c.name[0] for c in self.colours), self.player)
    def encode(self):
        return ''.join(c.name[0] for c in (self.player,) + self.colours)

class StateInvariants(NamedTuple):
    player: Player
    degree_sequence: Tuple[
        Tuple[int,int],Tuple[int,int],Tuple[int,int],
        Tuple[int,int],Tuple[int,int],Tuple[int,int]
    ]
    

class ColourDegree(NamedTuple):
    red: int
    blue: int

@dataclass
class StateDetails:
    expanded: bool = False
    in_progress: Optional[bool] = None
    winner: Optional[Player] = None
    value: Optional[int] = None
    optimal_play: Optional[int] = None
    successors: Dict[int, SimState] = field(default_factory=dict)

class SimEngine:
    def __init__(self):
        self.vertices = tuple(range(6))
        self.edges = tuple(combinations(self.vertices, 2))
        self.edge_ids = {edge: eid for (eid, edge) in enumerate(self.edges)}
        self.triangles = {
            eid: tuple(
                tuple(self.edge_ids[self.sort_edge((v, u))]
                    for u in edge)
                for v in self.vertices
                if v not in edge
            )
            for (edge, eid) in self.edge_ids.items()
        }
        self.incidents = {
            vertex: tuple(
                self.edge_ids[e]
                for (v, e) in 
                chain.from_iterable(
                    ((v, edge) for v in edge)
                    for edge in self.edges
                )
                if v == vertex
            )
            for vertex in self.vertices
        }
        self.canonical_states = {}
        self.states_by_invariants = defaultdict(list)
        self.state_details = {}
    def add_canonical_state(self, state):
        self.canonical_states[state] = state
        self.states_by_invariants[self.invariants(state)].append(state)
        self.state_details[state] = StateDetails()
    def sort_edge(self, edge):
        return tuple(sorted(edge))
    def invariants(self, state):
        return StateInvariants(state.player, self.degree_sequence(state.colours))
    def degree_sequence(self, colours):
        return tuple(sorted(tuple(sum(
                    colours[e] is c
                    for e in self.incidents[v])
                for c in Colour.iter_nonempty())
            for v in self.vertices))
    def is_isomorphic(self, colours, other_colours):
        g1 = networkx.generators.complete_graph(6)
        g2 = networkx.generators.complete_graph(6)
        c1 = {edge: colour for (edge, colour) in zip(self.edges,colours)}
        c2 = {edge: colour for (edge, colour) in zip(self.edges,other_colours)}
        networkx.set_edge_attributes(g1, c1, 'colour')
        networkx.set_edge_attributes(g2, c2, 'colour')
        em = networkx.algorithms.isomorphism.categorical_edge_match('colour', Colour.empty)
        return networkx.is_isomorphic(g1, g2, edge_match=em)
    def canonicalise(self, state):
        try:
            return self.canonical_states[state]
        except KeyError:
            pass
        invariants = self.invariants(state)
        for canon_state in self.states_by_invariants[invariants]:
            if state.player != canon_state.player:
                continue
            if self.is_isomorphic(state.colours, canon_state.colours):
                self.canonical_states[state] = canon_state
                return canon_state
        self.add_canonical_state(state)
        return state
    def evaluate_state(self, state, details, last_move):
        for (e, f) in self.triangles[last_move]:
            if state.colours[e] == state.colours[f] == state.player.change().colour():
                details.in_progress = False
                details.winner = state.player
                details.value = state.player.win_value()
                return
        details.in_progress = True
                    
    def map_state_space(self):
        state = SimState.initial_state()
        self.canonicalise(state)
        self.state_details[state].in_progress = True
        state_queue = {state}
        for _ in tqdm(count()):
            state = state_queue.pop()
            details = self.state_details[state]
            details.expanded = True
            if details.in_progress:
                for option in state.options():
                    next_state = state.apply(option)
                    next_state = self.canonicalise(next_state)
                    details.successors[option] = next_state
                    next_details = self.state_details[next_state]
                    if next_details.in_progress is None:
                        state_queue.add(next_state)
                        self.evaluate_state(next_state, next_details, option)
            if not state_queue:
                break
    def perform_minimax(self):
        self.minimax(SimState.initial_state())
    def minimax(self, state):
        details = self.state_details[state]
        if details.value is not None:
            return details.value
        options = [(self.minimax(next_state), option) for (option, next_state) in details.successors.items()]
        value, edge = state.player.optimiser()(options)
        details.optimal_play = edge
        details.value = value - (1 if value > 0 else -1)
        return details.value
    def sample_game(self):
        state = SimState.initial_state()
        while True:
            details = self.state_details[state]
            print(str(state), details.value)
            if not details.in_progress:
                break
            print(details.optimal_play)
            state = details.successors[details.optimal_play]

if __name__ == '__main__':
    SE = SimEngine()
    SE.map_state_space()
    print(f'{len(SE.state_details)} states')
    SE.perform_minimax()
    SE.sample_game()
