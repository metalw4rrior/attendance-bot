#! /usr/bin/env python
# -*- coding: utf-8 -*-
import random
 
Big = 'QWERTYUIOPASDFGHJKLZXCVBNM'
Low = 'qwertyuiopasdfghjklzxcvbnm'
Num = '1234567890'
Spe = '!@#$%^&amp;*()'
 
BI = True  # Пароль должен содержать символы в верхнем регистре (True - да | False - нет)
LO = True  # Пароль должен содержать символы в нижнем регистре (True - да | False - нет)
NU = True  # Пароль должен содержать цифры (True - да | False - нет)
PS = True  # Пароль должен содержать спец символы (True - да | False - нет)
 
Password_len = input('Длина пароля: ')
 
if Password_len:
   if Password_len.isdigit() == True:
       Password_len = int(Password_len)
   else:
      print('Выход... Значение должно быть цифровое...')
      exit(0)
else:
   print('Выход... Не указана Длина пароля...')
   exit(0)
 
Password_cou = input('Количество паролей: ')
print('\n')
 
if Password_cou:
   if Password_cou.isdigit() == True:
       Password_cou = int(Password_cou)
   else:
      print('Выход... Значение должно быть цифровое...')
      exit(0)
else:
   print('Выход... Не указано нужное количество паролей...')
   exit(0)
 
Pass_Symbol = []
if BI == True:
   Pass_Symbol.extend(list(Big))
 
if LO == True:
   Pass_Symbol.extend(list(Low))
 
if NU == True:
   Pass_Symbol.extend(list(Num))
 
if PS == True:
   Pass_Symbol.extend(list(Spe))
 
random.shuffle(Pass_Symbol)
psw = []
 
for yx in range(Password_cou):
   psw.append(''.join([random.choice(Pass_Symbol) for x in range(Password_len)]))
 
file_Pass = open('Password.txt', 'w')
file_Pass.write('\n'.join(psw))
file_Pass.close()
 
print('\n'.join(psw))
print('\n')
