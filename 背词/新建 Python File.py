with open('新建文本文档.txt','r',encoding='utf-8') as f:
    a=f.read()

a=a.replace(']','[').replace('\xa0','').replace('\ue008','').split('\n')
去除='qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNMN&'
数字='1234567890'

def is_chinese(char):
    return '\u4e00' <= char <= '\u9fff'
def in_chinese(x):
    for i in x:
        if is_chinese(i):
            return True
    return False
c={}
for i in a:
    if i=='':
        continue
    if i[0] in 数字:
        if '[' in i:
            i=i.split('[')
        elif '/' in i:
            i=i.split('/')
        else:
            i=i.split(' ')
        for x in range(len(i)):
            if not in_chinese(i[x]) and x>0:
                i[x]=''
        while '' in i:
            i.remove('')
        while len(i)>2:
            i.pop(2)
        for z in 数字+'.':
            i[0]=i[0].replace(z,'')

        i[1]=i[1].split('；')
        c[i[0].replace(' ','')]=i[1]
with open('data.txt','w',encoding='utf-8') as f:
    f.write(str(c))
