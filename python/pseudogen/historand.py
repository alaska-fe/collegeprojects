import matplotlib.pyplot as plt
from pseudogen import random_gen
numbers = [random_gen(1, 100) for _ in range(1000)]

plt.hist(numbers, bins=range(1, 101), edgecolor='black', align='left')

plt.savefig('histogram.png')
print("График успешно сохранен в файл histogram.png")
