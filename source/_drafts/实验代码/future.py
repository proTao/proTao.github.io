# #-*- coding:utf-8 -*-
# from concurrent import futures
# import time
 
# def gcd(pair):
#     a, b = pair
#     low = min(a, b)
#     for i in range(low, 0, -1):
#         if a % i == 0 and b % i == 0:
#             return i
# numbers = [
#     (1963309, 2265973), (1879675, 2493670), (2030677, 3814172),
#     (1551645, 2229620), (1988912, 4736670), (2198964, 7876293)
# ]


# def multi_exec():
#     #m 并发次数
#     #n 运行次数
 
#     with futures.ProcessPoolExecutor(max_workers=4) as executor: #多进程
#     #with futures.ThreadPoolExecutor(max_workers=m) as executor: #多线程
#         executor_dict=dict((executor.submit(gcd,numbers[i]), i) for i in range(6))
 
#         for future in futures.as_completed(executor_dict):
#             i = executor_dict[future]
#             if future.exception() is not None:
#                 print('%r generated an exception: %s' % (i,future.exception()))
#             else:
#                 print('RunTimes:%d,Res:%s'% (i, future.result()))
 
# if __name__ == '__main__':
#     start = time.time()
#     # results = list(map(gcd, numbers))
#     multi_exec()
#     end = time.time()
#     print(end - start)

import concurrent.futures
import math
import time

PRIMES = [
    112272535095293,
    112582705942171,
    112272535095293,
    115280095190773,
    115797848077099,
    1099726899285419
]

def is_prime(n):
    if n % 2 == 0:
        return False

    sqrt_n = int(math.floor(math.sqrt(n)))
    for i in range(3, sqrt_n + 1, 2):
        if n % i == 0:
            return False
    return True

def main():
    with concurrent.futures.ProcessPoolExecutor() as executor:
        for number, prime in zip(PRIMES, executor.map(is_prime, PRIMES)):
            print('%d is prime: %s' % (number, prime))

if __name__ == '__main__':
    start = time.time()
    main()
    # for i in PRIMES:
        # print(i, is_prime(i))
    end = time.time()
    print(end - start)

