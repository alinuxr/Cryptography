from sage import *
import random
import time
from datetime import datetime

def generate_random_curve():
    n = next_prime(10**7)
    k = GF(n)

    while True:
        a = random.randint(2, n-1)
        b = random.randint(2, n-1)

        if (4*a**3 + 27*b**2) != 0:
            curve = EllipticCurve(k, [a, b])

            P = curve.random_element()
            q = P.order()

            d = random.randint(2, q)
            Q = d * P



            return [curve, n, P, Q, d, q]


def generate_curve(n, a, b, d, x, y):
    curve = EllipticCurve(GF(n), [a, b])
    P = curve(x, y)
    Q = d * P
    q = P.order()

    return [curve, n, P, Q, d, q]


def H(P, L):
    return mod(P[0], L)


def PollardAttack(curve, P, Q, q, L=32):
    R = list()
    a = list()
    b = list()

    #Step 3
    for j in range(0, L):
        a.append(random.randint(0, q-1))
        b.append(random.randint(0, q-1))
        R.append(a[j]*P + b[j]*Q)

    #Step 4
    a1 = random.randint(1, q-1)
    b1 = random.randint(1, q-1)
    T1 = a1*P + b1*Q

    T2 = T1
    a2 = a1
    b2 = b1

    #Step 5
    while True:
        #Step 5.1
        j = H(T1, L)
        T1 = T1 + R[j]
        a1 = (a1 + a[j]) % q
        b1 = (b1 + b[j]) % q

        #Step 5.2
        j = H(T2, L)
        T2 = T2 + R[j]
        a2 = (a2 + a[j]) % q
        b2 = (b2 + b[j]) % q

        j = H(T2, L)
        T2 = T2 + R[j]
        a2 = (a2 + a[j]) % q
        b2 = (b2 + b[j]) % q

        if T1 == T2:
            break

    if a1 == a2 and b1 == b2:
        return None
    else:
        d = ((a1 - a2) * inverse_mod(b2 - b1, q)) % q
        return d


def Z(z, i):
    if i < 0:
        return 0
    else:
        return z[i]


def factor_to_list(Value):
    l = list(Value)
    r = list()

    for elem in l:
        tmp1, tmp2 = elem
        r.append(tmp1**tmp2)

    return r




curve = generate_curve(n=10000019, a=4476793, b=7781326, d=275822, x=3937719, y=6181659)
start_time = datetime.now()
#curve = generate_random_curve()
print("Parameters:\n\t{}\n\tn = {}\n\tP = {}\n\tQ = {}\n\td = {}\n\tq = {}\n".format(
    curve[0], curve[1], curve[2], curve[3], curve[4], curve[5]))


while True:
    try:
        while True:
            d = PollardAttack(curve[0], curve[2], curve[3], curve[5])
            if d != None:
                print("\n\nPollard Method:")
                print("Found d = {}".format(d))
                print(datetime.now() - start_time)
                break
        break

    except Exception as e:
        continue