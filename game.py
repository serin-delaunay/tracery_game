from abc import ABCMeta, abstractmethod
import json
import re
from collections import OrderedDict

class Game(metaclass=ABCMeta):
    def __init__(self):
        pass
    @abstractmethod
    def start_state(self):
        """
        Consistently returns a single state which is used
        as the root of the game's state graph.
        """
        pass
    @abstractmethod
    def options(self, state):
        """
        Given a valid state, returns an iterable containing
        valid player inputs for that state.
        """
        pass
    @abstractmethod
    def result(self, state, input):
        """
        Given a valid state and valid input, returns an iterable container
        of states resulting from that state+input combination.
        """
        pass
    @abstractmethod
    def display(self, state):
        """
        Given a valid state, returns a string containing tracery code
        that renders the game state.
        """
        pass
    @abstractmethod
    def encode(self, state):
        """
        Given a valid state, returns a string uniquely encoding that state.
        """
        pass
    @abstractmethod
    def grammar(self):
        """
        Returns a dictionary containing a partial tracery grammar,
        which will be completed by the addition of rendered states.
        """
        pass
    @abstractmethod
    def display_input(self, input):
        """
        Given a valid input, returns a string representing
        that input for the player's use.
        """
        pass
    def make_grammar(self, filename, state_graph, displays):
        grammar = self.grammar()
        for (state_code, options) in state_graph.items():
            grammar['*'+state_code] = "[code:{}][options:{}]{}".format(state_code, '‚'.join(k for k in options.keys()), displays[state_code])
        grammar['origin'] = "#*{}#".format(self.encode(self.start_state()))
        grammar['error'] = "Couldn't understand input. Reply in the format \"\\[code\\] \\[input\\]\"."
        with open(filename, 'w') as f:
            json.dump(grammar, f, indent='\t')
    def make_replies(self, filename, state_graph):
        states_sorted = sorted(state_graph.keys(), key = len, reverse=True)
        replies = OrderedDict()
        for state_code in states_sorted:
            for (input, results) in state_graph[state_code].items():
                replies['\\b{}\\b.*\\b{}\\b'.format(re.escape(state_code), re.escape(input))] = "{{unlisted}}[result:{}]#result#".format(','.join('#*{}#'.format(self.encode(result)) for result in results))
        replies['.'] = "#error#"
        with open(filename, 'w') as f:
            json.dump(replies, f, indent='\t')
    def tracerise(self, filename_base):
        state_graph = {}
        displays = {}
        state_queue = {self.start_state()}
        while state_queue:
            state = state_queue.pop()
            print(state)
            state_code = self.encode(state)
            state_results = {}
            if state_code not in state_graph:
                state_display = self.display(state)
                displays[state_code] = state_display
            for option in self.options(state):
                result_states = self.result(state, option)
                input = self.display_input(option)
                assert input not in state_results, 'input collision'
                state_results[input] = result_states
                for result_state in result_states:
                    result_code = self.encode(result_state)
                    if result_code not in state_graph:
                        state_queue.add(result_state)
            state_graph[state_code] = state_results
        self.make_grammar(filename_base+'_grammar.json', state_graph, displays)
        self.make_replies(filename_base+'_replies.json', state_graph)
