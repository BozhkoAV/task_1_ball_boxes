import matplotlib.pyplot as plt

with open("task_1_ball_boxes.txt") as inf:
    inf.readline()  # Source data:
    s = inf.readline().strip().split(', ')

    n_boxes = int(s[0].replace("n_boxes: ", ""))  # Количество корзин
    m = int(s[1].replace("m: ", ""))  # Количество цветов шаров
    d = int(s[2].replace("d: ", ""))  # Столько шаров берётся за раз, потом их возвращают
    p_change_box = float(s[3].replace("p_change_box: ", ""))  # Вероятность смены корзины
    nExp = int(s[4].replace("nExp = ", ""))  # Количество экспериментов

    boxes = dict()
    for i in range(n_boxes):
        s = inf.readline().strip().split(". ")

        boxes[s[0]] = dict()  # s[0] = Box i

        total = s[1].split(": ")
        boxes[s[0]][total[0]] = int(total[1])  # 'Total': ball_quantity

        colors = s[2].split(", ")
        for color in colors:
            boxes[s[0]][color.split(": ")[0]] = int(color.split(": ")[1])  # 'Color': ball_quantity

    inf.readline()  # Experiments:

    experiments = dict()
    for i in range(nExp):
        experiments[i + 1] = inf.readline().strip().split(': ')[1].split(', ')

# Вычислим априорную вероятность P(H_k) для первого опыта для каждой гипотезы
p_H_allHypos = dict()
p_H_i = 1 / n_boxes

for i in range(n_boxes):
    p_H_allHypos['Hypo' + str(i + 1)] = list()
    p_H_allHypos['Hypo' + str(i + 1)].append(p_H_i)

# Ряд распределения апостериорных вероятностей гипотез
p_HA_allHypos = dict()
for i in range(n_boxes):
    p_HA_allHypos['Hypo' + str(i + 1)] = list()

for exp in experiments.values():
    # Считаем условную вероятность события при верности гипотезы [P(A│H_k)] для каждой гипотезы
    p_AH_allHypos = dict()

    for i in p_H_allHypos:
        p_AH_i = 1.0

        colors = dict()
        for (ball_color, quantity) in boxes["Box " + i.replace('Hypo', '')].items():
            colors[ball_color] = quantity

        for ball in exp:
            p_AH_i *= colors[ball] / colors['Total']
            colors[ball] -= 1
            colors['Total'] -= 1

        p_AH_allHypos[i] = p_AH_i

    # Считаем полную вероятность события A
    p_A = 0.0
    for (i, p_H_i) in p_H_allHypos.items():
        p_A += p_H_i[-1] * p_AH_allHypos[i]

    # Вычислим апостериорную вероятность P(H_k|A) для каждой гипотезы по формуле Байеса
    for (k, p_H_k) in p_H_allHypos.items():
        if p_A != 0.0:
            p_HA_allHypos[k].append(p_H_k[-1] * p_AH_allHypos[k] / p_A)
        else:
            p_HA_allHypos[k].append(p_HA_allHypos[k][-1])

    # Вычислим априорные вероятности P(H_k) для следующего опыта на
    for k in p_H_allHypos:
        p_H_k = 0.0
        for i in p_HA_allHypos:
            if i == k:
                p_H_k += (1.0 - p_change_box) * p_HA_allHypos[i][-1]
            else:
                p_H_k += p_change_box * (1.0 / (n_boxes-1)) * p_HA_allHypos[i][-1]
        p_H_allHypos[k].append(p_H_k * p_H_allHypos[k][-1])

# 1a
size = 14
for (i, hypo) in p_HA_allHypos.items():
    plt.plot([i+1 for i in range(0, size)], hypo[0:size], label=i)
plt.legend()
plt.show()

# 1b
size = 100
maxHypo = ""
print('Наиболее вероятные гипотезы после каждого извлечения:')
for i in range(0, size):
    m = 0.0
    for hypo in p_HA_allHypos:
        if p_HA_allHypos[hypo][i] > m:
            m = p_HA_allHypos[hypo][i]
            maxHypo = hypo
    print(str(i + 1) + ": " + maxHypo, end="; ")
    if (i + 1) % 5 == 0:
        print()
print()

size = 14
plt.plot([i+1 for i in range(0, size)], p_HA_allHypos[maxHypo][0:size], label=maxHypo)
plt.legend()
plt.show()

# 1c
size = 12
hypoList = list()
for i in range(0, size):
    count = 0
    for hypo in p_HA_allHypos:
        if p_HA_allHypos[hypo][i] > 1e-2:
            count += 1
    hypoList.append(count)

plt.plot([i+1 for i in range(0, size)], hypoList)
plt.show()

# 2a
colors = dict()
for color in boxes['Box 1']:
    if color != 'Total':
        colors[color] = 0

for exp in experiments.values():
    for ball in exp:
        colors[ball] += 1

exp_profiles = dict()
for color in colors:
    exp_profiles[color] = colors[color] / (d * nExp)
print('Экспериментальный профиль корзины:')
print(exp_profiles, end="\n\n")

theoretical_profiles = dict()
for (i, box) in boxes.items():
    theoretical_profiles[i] = dict()
    total = 0
    for (color, quantity) in box.items():
        if color == 'Total':
            total = quantity
        else:
            theoretical_profiles[i][color] = quantity / total

print('Теоретические профили корзин:')
for (i, box) in theoretical_profiles.items():
    for color in box:
        box[color] = float("{0:.6f}".format(box[color]))
    print(i, box)
print()

# 2b
exp_theoretical_profiles = dict(theoretical_profiles)
print('Сравнение теоретического профиля каждой корзины с экспериментальным:')
for (i, box) in exp_theoretical_profiles.items():
    for color in box:
        box[color] = float("{0:.6f}".format(box[color] - exp_profiles[color]))
    print(i, box)

# 2c
experimental_profiles = dict()
for color in exp_profiles:
    experimental_profiles[color] = [0.0]

current_balls = dict()
for color in exp_profiles:
    current_balls[color] = 0.0

for exp in experiments.values():
    for ball in exp:
        current_balls[ball] += 1.0

    for color in current_balls:
        experimental_profiles[color].append(experimental_profiles[color][-1] + current_balls[color])
        current_balls[color] = 0.0

for (color, ball_quantity) in experimental_profiles.items():
    for i in range(1, len(ball_quantity)):
        ball_quantity[i] /= d * i

size = 200
for (color, quantity) in experimental_profiles.items():
    plt.plot([i for i in range(1, size+1)], quantity[1:size+1], color=color, label=color)

plt.legend()
plt.gca().set_facecolor('xkcd:light blue')
plt.grid()
plt.show()
