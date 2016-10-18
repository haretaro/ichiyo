from simulator import simulate, simulateP
from random import randint, random
import math
import matplotlib.pyplot as plt

iteration = 2000
best_parameters = []
best_benefit = 0
alpha = 0.8
tempreture = alpha

a, b = random(), random()
buy_value = max(a,b)
sell_value = min(a,b)
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

history = []
score = simulateP(state)
for i in range(iteration):
    if i% 10 == 0:
        print('iteration {} / {}, T={}'.format(i, iteration, tempreture))
    current_score = simulate(state[0], state[1], state[2], state[3], False, False)
    next_state = [state[0] + random()/10 - 0.05,
            state[1] + random()/10 - 0.05,
            state[2] + randint(-10,10),
            state[3] + randint(-10,10)]
    next_score = simulateP(next_state)
    if random() < probability(next_score, score, tempreture):
        state = next_state
        score = next_score
        print('iteration{}: new parameter {}, benefit {}'.format(i, state, score))
        history.append(score)
    tempreture *= alpha

plt.plot(history, label='benefit')
plt.title('annieling history')
plt.legend()
plt.show()

print('parameter {}'.format(state))
print('--validation set--')
simulateP(state, False, True)

print('--test set--')
simulateP(state, True, True)
