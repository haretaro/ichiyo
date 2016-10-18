#ランダムに試行して最適なパラメータを求める
iteration = 1500
best_parameters = []
best_benefit = 0
from simulator import simulate
from random import randint, random
for i in range(iteration):
    if i% 100 == 0:
        print('iteration {} / {}'.format(i, iteration))
    a, b = random(), random()
    buy_value = max(a,b)
    sell_value = min(a,b)
    loss_cut = randint(1,1000)
    profit_taking = randint(1,1000)
    benefit = simulate(buy_value, sell_value, loss_cut, profit_taking, False, False)
    if benefit > best_benefit:
        best_benefit = benefit
        best_parameters = [buy_value, sell_value, loss_cut, profit_taking]
        print('iteration{}: new best parameter {}'.format(i, benefit))


print('best benefit {}'.format(best_benefit))
print('parameters {}'.format(best_parameters))
simulate(best_parameters[0], best_parameters[1], best_parameters[2], best_parameters[3], False)
simulate(best_parameters[0], best_parameters[1], best_parameters[2], best_parameters[3])
