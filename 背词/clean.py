with open('temp.txt','r',encoding='utf-8') as f:
    a=eval(f.read())


for i in a:
    a[i]=[0]
    
with open('temp.txt','w',encoding='utf-8') as f:
    f.write(str(a))
