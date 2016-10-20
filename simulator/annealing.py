from simulator import simulate, simulateP
from random import randint, random, uniform
import math
import matplotlib.pyplot as plt

iteration = 10000
best_parameters = []
best_benefit = 0
alpha = 0.9
tempreture = alpha
regularization = None
mobility_of_rate = 0.1
mobility_of_money = 100
scale_par_100iteration = 0.9

buy_value = uniform(0.5,1)
sell_value = uniform(0,0.5)
loss_cut = randint(0,1000)
profit_taking = randint(0,1000)
state = [buy_value, sell_value, loss_cut, profit_taking]
def probability(next_score, score, tempreture):
    if next_score >= score:
        return 1
    else:
        p = math.e ** ((next_score - score)/tempreture)
        if p > 1:
            raise Exception('p is too large: {}'.format(p))
        return p

def neighbour(state):
    s0 = state[0] + uniform(-mobility_of_rate, mobility_of_rate)
    s1 = state[1] + uniform(-mobility_of_rate, mobility_of_rate)
    s2 = state[2] + randint(-mobility_of_money, mobility_of_money)
    s3 = state[3] + randint(-mobility_of_money, mobility_of_money)
    if s0 > 1:
        s0 = 1
    if s1 > 1:
        s1 = 1
    if s0 < s1:
        s0, s1 = s1, s0
    next_state = [s0, s1, s2, s3]
    next_state = [s if s > 0 else 0 for s in next_state]
    return next_state

history = []
score = simulateP(state)

try:
    for i in range(iteration):
        if i% 100 == 0:
            print('iteration {} / {}, T={}, current score{}'.format(i, iteration, tempreture, score))
            mobility_of_rate *= scale_par_100iteration
            mobility_of_money = int( mobility_of_money * scale_par_100iteration)
        current_score = simulate(state[0], state[1], state[2], state[3], False, False, regularization)
        next_state = neighbour(state)
        next_score = simulateP(next_state, regularization=regularization)
        if random() < probability(next_score, score, tempreture):
            state = next_state
            score = next_score
            print('iteration{}: new parameter {}, benefit {}'.format(i, state, score))
            history.append(score)
        tempreture *= alpha
except KeyboardInterrupt:
    print('stopped')
    print('iteration{}: iterationparameter {}, benefit {}'.format(i, state, score))

plt.plot(history, label='benefit')
plt.title('annieling history')
plt.legend()
plt.show()

print('\n----validation set--')
simulateP(state, False, True)

print('\n----test set--')
simulateP(state, True, True)

print('parameter {}'.format(state))
