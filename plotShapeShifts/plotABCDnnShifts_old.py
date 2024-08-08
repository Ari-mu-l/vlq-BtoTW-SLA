import numpy as np
import matplotlib.pyplot as plt
#import config
#from json import loads

def shift_peak(input_, mean_, sigma_, const_, shift_):
     if shift_ == "UP":
          return const_ * np.exp( -( ( input_ - mean_ ) / sigma_ )**2 )
     elif shift_ == "DN":
          return -const_ * np.exp( -( ( input_ - mean_ ) / sigma_ )**2 )
     else:
          quit( "[WARN] Invalid shift used, quitting..." )

def shift_tail(input_, mean_, sigma_, const_, shift_):
     if shift_ == "UP":
          return const_ * ( 1 - np.exp( -( ( input_ - mean_ ) / sigma_ )**2 ) )
     elif shift_ == "DN":
          return -const_ * ( 1 - np.exp( -( ( input_ - mean_ ) / sigma_ )**2 ) )
     else:
          quit( "[WARN] Invalid shift used, quitting..." )

def shift_linear(input_, mean_, sigma_, const_, shift_):
     if shift_ == "UP":
          return const_ * np.ones(input_.shape)
     elif shift_ == "DN":
          return -const_ * np.ones(input_.shape)

plotPrecentage = False
plotCombined = True

mean_ABCDnn = 905.44763 #800.9696 # random37_0.85
sigma_ABCDnn = 427.18433 # 379.87177

mean_input = 1003.4107 #797.64636
sigma_input = 303.12906 #389.21887

X = np.linspace(0, 2500, 101)

Ylinear_UP = shift_linear(X, mean_ABCDnn, sigma_ABCDnn, 0.2, "UP")
Ylinear_DN = shift_linear(X, mean_ABCDnn, sigma_ABCDnn, 0.2, "DN")
Ypeak_UP = shift_peak(X, mean_ABCDnn, sigma_ABCDnn, 0.05, "UP")
Ypeak_DN = shift_peak(X, mean_ABCDnn, sigma_ABCDnn, 0.05, "DN")
#Yinput_UP = shift_peak(X, mean_input, sigma_input, 0.5, "UP")
#Yinput_DN = shift_peak(X, mean_input, sigma_input, 0.5, "DN")
Ytail_UP = shift_tail(X, mean_ABCDnn, sigma_ABCDnn, 0.2, "UP")
Ytail_DN = shift_tail(X, mean_ABCDnn, sigma_ABCDnn, 0.2, "DN")

if plotPrecentage:
     if plotCombined:
          plt.plot(X, Ylinear_UP, color="red", linestyle="solid", label="Linear Up")
          plt.plot(X, Ylinear_DN, color="blue", linestyle="solid", label="Linear Down")
          plt.plot(X, Ytail_UP+Ypeak_UP, color="red", linestyle="dashed", label="Combined Up")
          plt.plot(X, Ytail_DN+Ypeak_DN, color="blue", linestyle="dashed", label="Combined Down")
          
          plt.xlabel("x")
          plt.ylabel("$\delta y(x) / x$")
          plt.legend(loc="upper right")
          plt.show()
     
     else:
          plt.plot(X, Ylinear_UP, color="red", linestyle="solid", label="Linear Up")
          plt.plot(X, Ylinear_DN, color="blue", linestyle="solid", label="Linear Down")
          plt.plot(X, Ytail_UP, color="red", linestyle="dashed", label="Tail Up")
          plt.plot(X, Ytail_DN, color="blue", linestyle="dashed", label="Tail Down")
          plt.plot(X, Ypeak_UP, color="red", linestyle="dotted", label="Peak Up")
          plt.plot(X, Ypeak_DN, color="blue", linestyle="dotted", label="Peak Down")
          
          plt.xlabel("x")
          plt.ylabel("$\delta y(x) / x$")
          plt.legend(loc="upper right")
          plt.show()
else:
     if plotCombined:
          plt.plot(X, X, color="black", linestyle="solid")
          plt.plot(X, X+X*Ylinear_UP, color="red", linestyle="solid", label="Linear Up")
          plt.plot(X, X+X*Ylinear_DN, color="blue", linestyle="solid", label="Linear Down")
          plt.plot(X, X+X*Ytail_UP+Ypeak_UP, color="red", linestyle="dashed", label="Combined Up")
          plt.plot(X, X+X*Ytail_DN+Ypeak_DN, color="blue", linestyle="dashed", label="Combined Down")

          plt.xlabel("x")
          plt.ylabel("y(x)")
          plt.legend(loc="upper right")
          plt.show()
     else:
          plt.plot(X, X, color="black", linestyle="solid")
          plt.plot(X, X+X*Ylinear_UP, color="red", linestyle="solid", label="Linear Up")
          plt.plot(X, X+X*Ylinear_DN, color="blue", linestyle="solid", label="Linear Down")
          plt.plot(X, X+X*Ytail_UP, color="red", linestyle="dashed", label="Tail Up")
          plt.plot(X, X+X*Ytail_DN, color="blue", linestyle="dashed", label="Tail Down")
          plt.plot(X, X+X*Ypeak_UP, color="red", linestyle="dotted", label="Peak Up")
          plt.plot(X, X+X*Ypeak_DN, color="blue", linestyle="dotted", label="Peak Down")
          
          plt.xlabel("x")
          plt.ylabel("y(x)")
          plt.legend(loc="upper right")
          plt.show()
