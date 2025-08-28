import numpy as np

T = 60
T = T + 273.15

P_total = 100 # bar
P_CO2 = 1 # bar
phi_CO2 = 0.78

CR = 5.8 - 1710 / T + 0.67 * np.log10(P_CO2)
CR = 10 ** CR


print(f'Worst case scenario: {CR:.4f} mm/y')

F_system = 0.67* (0.0031-1.4/T)*P_total
F_system = 10**F_system
print(f'Effect of total pressure: {CR*F_system:.4f} mm/y')

F_scale = 2400 / T - 0.6 * np.log10(phi_CO2* P_CO2) - 6.7
F_scale = 10 ** F_scale
F_scale = F_scale if F_scale < 1 else 1
print(f'Effect of high temperature: {CR*F_scale:.4f} mm/y')