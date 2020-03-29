# -*- coding: utf-8 -*-     

import string
from random import choice

'''
[:alnum:]   代表英文大小写字节及数字，亦即 0-9, A-Z, a-z 
[:alpha:]   代表任何英文大小写字节，亦即 A-Z, a-z 
[:blank:]   代表空白键与 [Tab] 按键两者 
[:cntrl:]   代表键盘上面的控制按键，亦即包括 CR, LF, Tab, Del.. 等等 
[:digit:]   代表数字而已，亦即 0-9 
[:graph:]   除了空白字节 (空白键与 [Tab] 按键) 外的其他所有按键 
[:lower:]   代表小写字节，亦即 a-z 
[:print:]   代表任何可以被列印出来的字节 
[:punct:]   代表标点符号 (punctuation symbol)，亦即：" ' ? ! ; : # $... 
[:upper:]   代表大写字节，亦即 A-Z 
[:space:]   任何会产生空白的字节，包括空白键, [Tab], CR 等等 
[:xdigit:]  代表 16 进位的数字类型，因此包括： 0-9, A-F, a-f 的数字与字节 
 
Python自带常量(本例中改用这个，不用手工定义了) 
string.digits          #十进制数字：0123456789 
string.octdigits       #八进制数字：01234567 
string.hexdigits       #十六进制数字：0123456789abcdefABCDEF 
string.ascii_lowercase #小写字母(ASCII)：abcdefghijklmnopqrstuvwxyz 
string.ascii_uppercase #大写字母(ASCII)：ABCDEFGHIJKLMNOPQRSTUVWXYZ 
string.ascii_letters   #字母：(ASCII)abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ 
string.punctuation     #标点符号：!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~ 
 
以下的不用，有locale问题 
string.lowercase       #abcdefghijklmnopqrstuvwxyz 
string.uppercase       #ABCDEFGHIJKLMNOPQRSTUVWXYZ 
string.letters         #ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz 
 
以下的不能用 
string.whitespace      #On most systems this includes the characters space, tab, linefeed, return, formfeed, and vertical tab. 
string.printable       #digits, letters, punctuation, and whitespace 
'''  
  
# 请在此设置您要生成的密码需求
password_length = 18  # 密码长度
password_count = 10  # 密码个数
# password_seed = string.digits + string.ascii_letters + string.punctuation #密码种子
# password_seed = string.digits
password_seed = string.digits + string.ascii_letters 
  

# generate password
def generate_password():
    password = []  
    while len(password) < password_length:
        password.append(choice(password_seed))  
    return ''.join(password)  


def print_string_constants():
    print(string.digits)
    print(string.octdigits)
    print(string.hexdigits)
    print(string.ascii_lowercase)
    print(string.ascii_uppercase)
    print(string.ascii_letters)
    print(string.punctuation)
    print("\n\n")

      
if __name__ == '__main__':
    print('generate password begin: ' + "\n")
    for i in range(0, password_count):  
        print(generate_password())
    print('generate password end: ' + "\n")
