import subprocess
import sys
import time
import math
from sympy import mod_inverse

class TimeAttack:

    def _pow_quick(self, a, b, m):
        a = int(a)
        b = int(b)
        if a % m == 0:
            return 0
        if a > m:
            a = a % m
        tmp = 1
        while b > 1:
            if b & 1 == 0:
                b >>= 1
                a = (a * a) % m
            if b & 1 == 1:
                b -= 1
                tmp *= a
                tmp = tmp % m
        return tmp % m


    def __init__(self, exe_path, e, n):
        self.exe_path = exe_path

        self.process = None
        self.stdin = None
        self.stdout = None

        self.interactions = 0
        self.e = int(e, 16)
        self.N = int(n, 16)
        self.R = int(2 ** ((math.log(self.N, 2) // 2) + 1))
        self.q = 0
        if self._pow_quick(self.R, -1, self.N) == mod_inverse(self.R, self.N):
            print('OK')

    def _euclidean_trancated(self, a, b):
        x0, x1, y0, y1 = 1, 0, 0, 1
        i = 0
        while b:
            q = a // b
            a, b = b, a % b
            if(b > (a >> 1)):
                b = a - b
                x0, x1 = x1, x1 - (x0 - x1*q)#если остатки усекаются, то коэф линейного разложения должны быть
                y0, y1 = y1, y1 - (y0 - y1*q)#пересчитаны таким образом, что бы не нарушалась структура алгоритма
            else:
                x0, x1 = x1, x0 - x1*q
                y0, y1 = y1, y0 - y1*q
            i += 1
        return (x0, y0, a)

    def run(self):
        self.process = subprocess.Popen(args=self.exe_path, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        self.stdout = self.process.stdout
        self.stdin = self.process.stdin

    def interact(self, c):
        self.interactions += 1

        line = "{0:X}\r\n".format(c).encode()
        self.stdin.write(line)
        self.stdin.flush()

        #while True:
        time = int(self.stdout.readline())
        message = int(self.stdout.readline().strip(), 16)
            #self.stdout.flush()
            #if time != 0 and message != 0:
                #print(time, message)
                #break
        return message, time

    def close(self):
        print('The job is done!')
        if self.process:
            self.process.kill()

    #  g - два старших бита, которые подбираются перебором
    #  l - сколько бит оценивать
    #  s - сколько запросов делать
    def attack(self, preset, s, l, delta_limit):
        g = preset
        #print(f'len of g is {len(bin(g)) - 2}')
        #  будем начинать с бита под номером 503, если считать справа, или 9го бита слева
        #cur_offset = 503
        sum = 0
        for cur_offset in range(503, 2, -1):
            #print(f'testing bit №{512 - cur_offset}')
            #  сдвигаем единицу на текущее количество бит и делаем ИЛИ текущее c g, таким образом следующий бит поставим в 1
            self.q = g | (0b1 << cur_offset)
            #print(bin(g))
            #print(bin(self.q))
            time1 = time2 = 0
            #  считаем время, учитывая соседей
            for j in range(l):
                ugi = ((g + j) * mod_inverse(self.R, self.N)) % self.N
                ugi_tmp = ((self.q + j) * mod_inverse(self.R, self.N)) % self.N
                msg, t1 = self.interact(ugi)
                msg, t2 = self.interact(ugi_tmp)
                time1 += t1
                time2 += t2

            delta = time1 - time2 if time1 > time2 else time2 - time1
            sum += delta
            if delta > delta_limit:
                self.q = g
                #print(f'{512 - cur_offset})delta = {delta}, set bit to 0\n')
            else:
                g = self.q

        for i in range(0, 9):
            if self.N % (self.q | i) == 0:
                print(f'divisor is {self.q | i}')
                p = self.N // self.q
                d, _, _ = self._euclidean_trancated(self.e, (self.q - 1) * (p - 1))
                print(f'd = {d}')
                return True

            #cur_offset -= 1
        print(f'delta middle = {sum/503}')
        return False



N = '97239b859ed7b1f4be8b35b0da954e21cd88aa3377c5461bb656f4c58d7a79e7a7937229c41b2734370a345e8d07992f1d185e8fcbf5680738105998d9eda7e71c72cfb9edf7726c9ea23846caf212bdfe34c6d1042826c2142aa3ef7ffd207e32634592909acacc8e054cec047045184da06c019974161e79d162bcd2ec460b'
e = '010001'
g = int('ce', 16)
a = TimeAttack('cryptor_v2.exe', e, N)
a.run()
print(f'preset bits: {bin(g)}')
l = 1
limit = 34000
print(f'delta = {limit}')
    #  сдвигаем g на 504 влево, таким образом получим число длинной 512 бит, где первые 8 нам известны, остальные - нули
time_st = time.perf_counter()
a.attack(g << 504, 1, l, limit)
print(f'total time: {time.perf_counter() - time_st}')
a.close()
