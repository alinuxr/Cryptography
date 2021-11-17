

import math
from random import randint
from fractions import gcd
import time
from datetime import datetime


# Sieve of Eratosthenes
def primes(n):

    b = [True] * (n + 1)
    ps = []

    for p in range(2, n + 1):

        if b[p]:
            ps.append(p)

            for i in range(p, n + 1, p):
                b[i] = False

    return ps


# Finds modular inverse
# Returns inverse, unused helper and gcd
def modular_inv(a, b):

    if b == 0:
        return 1, 0, a

    q, r = divmod(a, b)
    x, y, g = modular_inv(b, r)

    return y, x - q * y, g


# Addition in Elliptic curve modulo m space
def elliptic_add(p, q, a, b, m):

    # If one point is infinity, return other one
    if p[2] == 0: return q
    if q[2] == 0: return p
    if p[0] == q[0]:
        if (p[1] + q[1]) % m == 0:
            return 0, 1, 0  # Infinity

        num = (3 * p[0] * p[0] + a) % m
        denom = (2 * p[1]) % m

    else:
        num = (q[1] - p[1]) % m
        denom = (q[0] - p[0]) % m

    inv, _, g = modular_inv(denom, m)
    # Unable to find inverse, arithmetic breaks
    if g > 1:
        return 0, 0, denom  # Failure

    z = (num * inv * num * inv - p[0] - q[0]) % m

    return z, (num * inv * (p[0] - z) - p[1]) % m, 1


# Multiplication (repeated addition and doubling)
def elliptic_mul(k, p, a, b, m):

    r = (0, 1, 0)  # Infinity

    while k > 0:
        # p is failure, return it
        if p[2] > 1:
            return p

        if k % 2 == 1:
            r = elliptic_add(p, r, a, b, m)

        k = k // 2
        p = elliptic_add(p, p, a, b, m)

    return r


# Lenstra's algorithm for factoring
# Limit specifies the amount of work permitted
def lenstra(n, limit, primes):

    g = n

    while g == n:
        # Randomized x and y
        q = randint(0, n - 1), randint(0, n - 1), 1
        # Randomized curve coefficient a, computed b
        a = randint(0, n - 1)
        b = (q[1] * q[1] - q[0] * q[0] * q[0] - a * q[0]) % n
        g = math.gcd(4 * a * a * a + 27 * b * b, n)  # singularity check

    # If we got lucky, return lucky factor
    if g > 1:
        return g
    # increase k step by step until lcm(1, ..., limit)

    #for p in primes(limit):
    for p in primes:
        pp = p

        while pp < limit:
            q = elliptic_mul(p, q, a, b, n)

            # Elliptic arithmetic breaks
            if q[2] > 1:
                return math.gcd(q[2], n)

            pp = p * pp

    return None
start_time = datetime.now()
e = 0x10001
d = 0x82cc419cabf996d11
#n = "8cc5ee393a0ab4e8b"
n = 29538001#5311160273
    #29538001 #162300410644419792523
limit=1000
primes = primes(limit)
print('for n=', n)
print('result = ', lenstra(n,limit,primes))
print(datetime.now() - start_time)
