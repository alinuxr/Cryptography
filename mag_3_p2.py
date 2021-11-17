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

LEN = 256

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

def generating_e_d():
	p = getPrime(LEN, randfunc=get_random_bytes)
	q = getPrime(LEN, randfunc=get_random_bytes)
	euler = (p-1)*(q-1)
	n = p*q
	#print(euler)
	while True:
		e = random.getrandbits(16)
		if(math.gcd(e, euler) == 1):
			break
	d = mult_inv(e,euler)
	while(d<0):
		d = d + euler

	file_1 = open("file_d.txt", "w")
	file_1.write(str(d))
	file_1.close()

	return e,d,n

#RSA-преобразование
def RSA(message, key, N):
	outputText = pow(message, key, N)
	return outputText

def asn1_pack(n,e,c,length,enc_file):
	encoder = asn1.Encoder()
	encoder.start()
	encoder.enter(asn1.Numbers.Sequence)
	encoder.enter(asn1.Numbers.Set)
	encoder.enter(asn1.Numbers.Sequence)
	encoder.write(b'\x00\x01' ,asn1.Numbers.OctetString)#идентификатор RSA
	encoder.write(b'test' ,asn1.Numbers.UTF8String)
	encoder.enter(asn1.Numbers.Sequence)
	encoder.write(n,asn1.Numbers.Integer)
	encoder.write(e,asn1.Numbers.Integer)
	encoder.leave()#закрываем фигурную скобку, поднимаясь на уровень выше
	encoder.enter(asn1.Numbers.Sequence)
	encoder.leave()
	encoder.enter(asn1.Numbers.Sequence)
	encoder.write(c,asn1.Numbers.Integer)
	encoder.leave()
	encoder.leave()
	encoder.leave()
	encoder.enter(asn1.Numbers.Sequence)
	encoder.write(b'\x10\x82' ,asn1.Numbers.OctetString)#идентификатор AES в CBC-mode
	encoder.write(length,asn1.Numbers.Integer)
	encoder.leave()
	encoder.leave()
	encoder.write(enc_file)
	file = open("asn1_pack.txt", "wb")
	file.write(encoder.output())
	file.close()

def asn1_unpack():
	file = open("asn1_pack.txt", "rb")
	file_byte = file.read()
	decoder = asn1.Decoder()
	decoder.start(file_byte)
	decoder.enter()
	decoder.enter()
	decoder.enter()
	decoder.read()
	decoder.read()
	decoder.enter()
	tag,n = decoder.read()
	decoder.read()
	decoder.leave()
	decoder.enter()
	decoder.leave()
	decoder.enter()
	tag,c = decoder.read()
	decoder.leave()
	decoder.leave()
	decoder.leave()
	decoder.enter()
	decoder.read()
	decoder.read()
	decoder.leave()
	decoder.leave()
	tag,enc = decoder.read()
	file.close()
	return n,c,enc

def G(r,k_0):
	#длина r равна k_0 бит
	if(str(type(r)) != "<class 'bytes'>"):
		r_bytes = r.to_bytes(int(k_0/8), 'big')
	else:
		r_bytes = r
	h = hashlib.sha384()
	h.update(r_bytes)
	hash = h.digest()
	return hash

def H(X):
	h = hashlib.shake_128()
	h.update(X)
	hash = h.digest(16)
	return hash

def byte_xor(ba1, ba2):
	return bytes([_a ^ _b for _a, _b in zip(ba1, ba2)])

def AES_generation():
	#random 32-byte key
	key = random.getrandbits(256)
	#print("Symmetric key (32-bytes): " + str(key) + "\n")

	#random 16-byte sync-pos
	sync_package = random.getrandbits(128)
	file_sync = open("file_sync.txt", "w")
	file_sync.write(str(sync_package))
	file_sync.close()

	key = key.to_bytes(32, byteorder='big')
	sync_package = sync_package.to_bytes(16, byteorder='big')

	return key

def OAEP(k, k_0, k_1, aes_key):
	#сообщением для RSA-OAEP будет симметричный ключ
	m = aes_key
	#дополняем k_1 нулями
	for i in range(0,int(k_1/8)):
		m = m + b'\00'

	#рандомим r длины k_0
	r = random.getrandbits(k_0)
	X = byte_xor(m,G(r,k_0))

	#переводим r в байты
	r_bytes = r.to_bytes(int(k_0/8), 'big')
	Y = byte_xor(r_bytes,H(X))

	#итоговое сообщение, которое пойдет в RSA
	m_ = X + Y
	#итоговый шифртекст
	c_ = RSA(int.from_bytes(m_, 'big') ,e, n)
	return c_

def AES_encrypt(file_bytes, key):
	ff_sync = open("file_sync.txt", "rb")
	sync_bytes = ff_sync.read()
	ff_sync.close()
	sync_package = int(sync_bytes)
	sync_package = sync_package.to_bytes(16, byteorder='big')

	aes = AES.new(key, AES.MODE_CBC, sync_package)
	encd = aes.encrypt(pad(file_bytes, AES.block_size))

	return encd

def get_param():
	ff_d = open("file_d.txt", "rb")
	d_bytes = ff_d.read()
	ff_d.close()
	d = int(d_bytes)

	ff_sync = open("file_sync.txt", "rb")
	sync_bytes = ff_sync.read()
	ff_sync.close()
	sync_package = int(sync_bytes)
	sync_package = sync_package.to_bytes(16, byteorder='big')
	return sync_package, d

option = -1
while (option != '3'):
#if (option != '3'):
	print("\n\n\n1)Encrypt\n2)Decrypt\n3)Exit")
	option = input()

	if (option == '1'):
		#f = open("1.txt", "rb")
		print("Enter filename")
		filename = input()
		f = open(filename, "rb")
		file_bytes = f.read()
		f.close()

		while(1):
			e,d,n = generating_e_d()
			k = LEN*2
			k_1 = 128
			k_0 = 128
			aes_key = AES_generation()
			#полученный шифртекст
			c_ = OAEP(k, k_0, k_1, aes_key)

			#проверка
			M_ = RSA(c_,d, n)
			M_ = M_.to_bytes(64,'big')

			X_ = M_[:48]
			Y_ = M_[48:]

			R = byte_xor(Y_,H(X_))
			msg = byte_xor(X_,G(R,k_0))

			if(str(aes_key) == str(msg[:32])):
				break

		key = msg[:32]

		print("e = " + str(e) + "\n")
		print("d = " + str(d) + "\n")
		print("n = " + str(n) + "\n")
		print("\nk = " + str(k) + "\n")
		print("k_0 = " + str(k_0) + "\n")
		print("k_1 = " + str(k_1) + "\n")
		print("\nSymmetrc key:\n", key)

		encd = AES_encrypt(file_bytes, key)

		#упаковка asn1
		asn1_pack(n,e,c_,len(encd),encd)

		print("Encrypted successfully! Result is in asn1_pack.txt")

	if (option == '2'):
		k_0 = 128

		#распаковка asn1 - извлекаем параметры n, c, и сам файл в зашифрованном виде

		unpack_n, unpack_c, unpack_encd = asn1_unpack()

		sync_package, d = get_param()

		#расшифровываем unpack_c (симм.ключ) закрытым показателем d
		M_ = RSA(unpack_c,d,unpack_n)

		M_ = M_.to_bytes(64,'big')

		X_ = M_[:48]
		Y_ = M_[48:]
		R = byte_xor(Y_,H(X_))
		msg = byte_xor(X_,G(R,k_0))

		decrypted_key = msg[:32]

		print("Decrypted symmetric key:\n",str(decrypted_key))

		#aes с использованием decrypted_key (расшифровываем unpack_encd)
		#decrypted_key = decrypted_key.to_bytes(32, byteorder='big')
		aes_2 = AES.new(decrypted_key, AES.MODE_CBC, sync_package)
		decd = unpad(aes_2.decrypt(unpack_encd), AES.block_size)

		file2 = open("decrypted.txt", "wb")
		file2.write(decd)
		file2.close()

		print("Decrypted successfully! Result is in decrypted")


