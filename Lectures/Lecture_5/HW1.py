#Problem 1

import numpy as np

np.random.seed(42)
x1 = np.random.randint(10, 20, 12)
x2 = np.random.randint(10, 20, 10)

def either_or(list_1, list_2):
	return list(set(list_1) ^ set(list_2))

result = either_or(x1, x2)
print(result)

#Problem 2
import numpy as np

np.random.seed(42)
int_list = np.random.randint(10, 101, 20)

odd_list = [i for i in int_list if i%2 != 0]
print(odd_list)

#Problem 3
import random
import string
import numpy as np


chars = string.ascii_lowercase
random.seed(42)
my_list = [random.choice(chars) for i in range(10)]

np.random.seed(42)
ints = np.random.randint(10, 101, 20)

my_list.extend(ints)

def item_type_calculator(my_list):
	num_odd = 0
	num_even = 0
	num_str = 0
	for item in my_list:
		if type(item) == str:
			if item.isdigit():
				item = int(item)
				if item % 2 == 0:
					num_even += 1
				else:
					num_odd += 1
			else:
				num_str += 1
		else:
			if item % 2 == 0:
				num_even += 1
			else:
				num_odd += 1
	with open("result.txt", "w") as f:
		f.write("Number of even number: " + str(num_even) + "\n")
		f.write("Number of odd number: " + str(num_odd) + "\n")
		f.write("Number of strings: " + str(num_str) + "\n")

item_type_calculator(my_list)