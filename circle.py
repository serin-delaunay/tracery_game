from game import Game

class Circle(Game):
    def __init__(self, n):
        self.n = n
    def start_state(self):
        return 0
    def options(self, state):
        return ['+', '-']
    def result(self, state, input):
        return (state + {'+':1, '-':-1}[input])%self.n
    def display(self, state):
        return 'state: ' + str(state)
    def encode(self, state):
        return str(state)

if __name__ == '__main__':
    Circle(15).tracerise('circle')
