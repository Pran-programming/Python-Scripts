# Write your program for Task 8j here
from random import randint
largest = 0

number = []

for i in range(10):
  num = randint(1,100)
  number.append(num)

for a in range(len(number)):
  print(number[a])

for b in range(len(number)):
  if number[b] > largest:
    largest = number[b]
print("The largest number is",largest)

for b in range(len(number)):
  if number[b] == largest:
    print("The index position of the largest number is", b)