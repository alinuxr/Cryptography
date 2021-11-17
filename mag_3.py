import random
import os
import math
import hashlib
import asn1
import numpy as np
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Util.Padding import unpad
from Crypto.Util.number import getPrime
from Crypto.Random import get_random_bytes
from sympy import symbols, Poly, Matrix, gcd
from sympy.abc import x,y
from labmath import polyrootsmod



LEN = 32

def bytes_needed(n):
	if(n == 0):
		return 1
	return int(math.log(n, 256)) + 1

#возвращаемый аргумент x является мультипликативно обратным к a, b - модуль
def mult_inv(a, b):
	x, xx, y, yy = 1, 0, 0, 1
	while b:
		q = a // b
		a, b = b, a % b
		x, xx = xx, x - xx*q
		y, yy = yy, y - yy*q
	#return (x, y, a)
	return x

def small_generating_e_d():
	while True:
		p = getPrime(LEN, randfunc=get_random_bytes)
		q = getPrime(LEN, randfunc=get_random_bytes)
		euler = (p-1)*(q-1)
		n = p*q
		e = 3#random.getrandbits(16)
		if(math.gcd(e, euler) == 1):
			break
	d = mult_inv(e,euler)
	while(d<0):
		d = d + euler
	print("n =  " + str(n) + "\n")
	print("e =  " + str(e) + "\n")
	print("d =  " + str(d) + "\n")

	return e,d,n

#RSA-преобразование
def RSA(message, key, N):
	outputText = pow(message, key, N)
	return outputText

def coefficients(P):
    Pc = []
    for i in range(P.degree(), -1, -1):
        Pc.append(P.nth(i))
    return tuple(Pc)

def sylvester(P, Q):
    rows = []
    m = P.degree()
    n = Q.degree()
    size = m + n
    CP = coefficients(P)
    CQ = coefficients(Q)
    for i in range(size):
        tail = []
        row = []
        if i in range(0, n):
            row = list(CP)
            row.extend((n-1-i)*[0])
            row[:0] = [0]*i
            rows.append(row)
        if i in range(n, size):
            row = list(CQ)
            row.extend((size-1-i)*[0])
            row[:0] = [0]*(size-len(row))
            rows.append(row)
    return Matrix(rows)

def resultant(P, Q):
    return sylvester(P,Q).det()

def cipher_short_mess(m,e,n):
	u = int(math.log(n,2) / e*e)
	r_1 = random.randint(0, (pow(2, u) - 1))
	m_1 = pow(2,u)*m + r_1
	m_1 = m_1%n

	r_2 = random.randint(0, (pow(2, u) - 1))
	m_2 = pow(2,u)*m + r_2
	m_2 = m_2%n

	c_1 = RSA(m_1,e,n)
	c_2 = RSA(m_2,e,n)

	return c_1,c_2,r_1

def find_res_root(c_1, c_2, e, n):
	g_1 = Poly(x**e - c_1, x)
	g_2 = Poly((x+y)**e - c_2, x)

	#преобразовываем результант к полиному
	res = Poly(resultant(g_1,g_2),y)
	#print("resultant:\n",res)
	#находим коэффициенты (для вычисления корня)
	coef = coefficients(res)

	#берем коэффициенты по модулю n
	new_coef = []
	for i in coef:
		new_coef.append(i%n)

	#reverse for polyrootsmod
	new_coef.reverse()
	#finding root
	root = polyrootsmod(new_coef,n)
	root = int(root[0])

	return root

def find_opentexts(c_1, c_2, a, b, e, n):
	f = x**e - c_1
	g = (a*x + b)**e - c_2

	#находим коэффициенты (для вычисления корня)
	coef = list(coefficients(Poly(f)))
	#reverse for polyrootsmod
	coef.reverse()

	#finding root
	root = polyrootsmod(coef,n)

	m_1 = int(root[0])
	m_2 = (a*m_1 + b)%n

	return m_1, m_2

option = '1'
#while (option != '5'):
if (option != '5'):
	#option = input()

	if (option == '1'):

		file_bytes = input("\nEnter message: ")
		file_bytes = file_bytes.encode()
		#file_bytes = 'Ok'.encode()

		#converting bytes to int
		m = int.from_bytes(file_bytes, "big")

		print("\nm = " , m)
		print("\nm^e=" , pow(m,3),"\n")

		#генерируем показатели e и d и зашифровываем симм.ключ открытым показателем e
		e,d,n = small_generating_e_d()

		u = (int(math.log(n,2) / e*e))

		#дополняем сообщение, зашифровываем на открытом ключе
		c_1, c_2, r_1 = cipher_short_mess(m,e,n)

		#нарушитель перехватил c_1 и c_2

		b = find_res_root(c_1, c_2, e, n)
		#print("b:",b)

		m_1, m_2 = find_opentexts(c_1, c_2, 1, b, e, n)

		f = ((2**u)*x - (m_1 - r_1))
		#находим коэффициенты (для вычисления корня)
		coef = list(coefficients(Poly(f)))
		#reverse for polyrootsmod
		coef.reverse()
		#finding root
		root = polyrootsmod(coef,n)

		M = int(root[0])
		M = M.to_bytes(bytes_needed(M), 'big')
		print("\nCalculated message value:",M.decode())




