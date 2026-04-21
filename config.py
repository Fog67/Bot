a = input().split(' ')
b = int(input())
kop = 0
for i in range(len(a)):
    if int(a[i]) > (b-1)*100 and int(a[i]) <= b*100:
        kop+=1


print(kop)


