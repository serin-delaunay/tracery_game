from abc import ABCMeta, abstractmethod
import json
import re
from collections import OrderedDict
from tqdm import tqdm
from itertools import count, chain

class Game(metaclass=ABCMeta):
    def __init__(self):
        pass
    @abstractmethod
    def start_states(self):
        pass
    @abstractmethod
    def options(self, state):
        pass
    @abstractmethod
    def result(self, state, input):
        pass
    @abstractmethod
    def display(self, state):
        pass
    @abstractmethod
    def encode(self, state):
        pass
    @abstractmethod
    def grammar(self):
        pass
    @abstractmethod
    def display_input(self, input):
        pass
    def make_grammar(self, filename, state_graph, displays):
        grammar = self.grammar()
        for (state_code, options) in state_graph.items():
            grammar['*'+state_code] = "[code:{}][options:{}]{}".format(state_code, '‚'.join(sorted(str(k) for k in options.keys())), displays[state_code])
        grammar['origin'] = ["{}#*{}#".format(message, self.encode(state)) for (state, message) in self.start_states()]
        grammar['error'] = "Couldn't understand input. Reply in the format \"\\[code\\] \\[input\\]\"."
        with open(filename, 'w') as f:
            json.dump(grammar, f, indent='\t', sort_keys=True)
    def make_replies(self, filename, state_graph):
        states_sorted = sorted(state_graph.keys(), key = len, reverse=True)
        replies = OrderedDict()
        for state_code in states_sorted:
            for (input, results) in state_graph[state_code].items():
                reply = ''.join("[{}:{}]".format(
                    result_type,
                    ','.join('#*{}#'.format(self.encode(result)) for result in result_list))
                for (result_type, result_list) in results.items())
                replies['\\b{}\\b.*\\b{}\\b'.format(re.escape(state_code), re.escape(input))] = "{unlisted}" + reply + "#result#"
        replies['.'] = "#error#"
        with open(filename, 'w') as f:
            json.dump(replies, f, indent='\t')
    def tracerise(self, filename_base):
        state_graph = {}
        displays = {}
        state_queue = {state for (state, message) in self.start_states()}
        for _ in tqdm(count()):
            state = state_queue.pop()
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
                for result_state in chain.from_iterable(result_states.values()):
                    result_code = self.encode(result_state)
                    if result_code not in state_graph:
                        state_queue.add(result_state)
            state_graph[state_code] = state_results
            if not state_queue:
                break
        self.make_grammar(filename_base+'_grammar.json', state_graph, displays)
        self.make_replies(filename_base+'_replies.json', state_graph)
