import random


testList = [1, 2, 3]
testQuant = 2

for i in range(100):
    subset = [temp for temp in random.sample(testList, testQuant)]
    print(subset)
