import matplotlib.pyplot as plt
import random


def rn():
    return random.random() * 2
base = 0

ppl1 = []
ppl2 = []
ppl3 = []
ppl4 = []
ppl5 = []
x = []
for i in range(1,10):

    base += rn()
    ppl1.append(base)
    
base = 0
for i in range(1,10):

    base += rn()
    ppl2.append(base)
    
base = 0
for i in range(1,10):

    base += rn()
    ppl3.append(base)
    
base = 0
for i in range(1,10):

    base += rn()
    ppl4.append(base)
    
base = 0
for i in range(1,10):

    base += rn()
    ppl5.append(base)

for i in range(1,10):
    x.append(i)

for i in range (0, len(ppl1)):
    plt.plot(x[i], ppl1[i], linestyle="None", marker="o", markersize=10, color="red")
    plt.plot(x[i], ppl2[i], linestyle="None", marker="o", markersize=8, color="blue")
    plt.plot(x[i], ppl3[i], linestyle="None", marker="o", markersize=8, color="green")
    plt.plot(x[i], ppl4[i], linestyle="None", marker="o", markersize=8, color="brown")
    plt.plot(x[i], ppl5[i], linestyle="None", marker="o", markersize=8, color="purple")
    
plt.plot(x, ppl1, linestyle="-", color="red", linewidth = 3 , label = 'ppl1')
plt.plot(x, ppl2, linestyle="solid", color="blue", linewidth = 3 , label = 'ppl2')
plt.plot(x, ppl3, linestyle="solid", color="green", linewidth = 3 , label = 'ppl3')
plt.plot(x, ppl4, linestyle="solid", color="brown", linewidth = 3 , label = 'ppl4')
plt.plot(x, ppl5, linestyle="solid", color="purple", linewidth = 3 , label = 'ppl5')
plt.legend(loc='best')

plt.savefig("/Users/Lucify/Documents/git_repo/weight_overflow/files/weightgram/abcd.png")