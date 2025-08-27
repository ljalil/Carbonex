import math

K = {5:0.42, 15:1.59, 20:4.762, 40:8.927, 60:10.695, 80:9.949, 90:6.250, 120:7.770, 150:5.203}

def f_pH(t, pH):
    if t==20:
        return 2.0676-0.2309*pH if 3.5<pH<4.6 else (5.1885-1.2353*pH+0.0708*pH*pH)
    if t==15:
        return 2.0676-0.2309*pH if 3.5<pH<4.6 else (4.986-1.191*pH+0.0708*pH*pH)
    if t==5:
        return 2.0676-0.2309*pH if 3.5<pH<4.6 else (4.342-1.051*pH+0.0708*pH*pH)
    if t==40:
        return 2.0676-0.2309*pH if 3.5<pH<4.6 else (5.1885-1.2353*pH+0.0708*pH*pH)
    if t==60:
        return 1.836-0.1818*pH if 3.5<pH<4.6 else (15.444-6.1291*pH+0.8204*pH**2-0.0371*pH**3)
    if t==80:
        return 2.6727-0.3636*pH if 3.5<pH<4.6 else (331.68*math.exp(-1.2618*pH))
    if t==90:
        if 3.5<pH<4.57: return 3.1355-0.4673*pH
        if 4.57<pH<5.62: return 21254*math.exp(-2.1811*pH)
        return 0.4014-0.0538*pH
    if t==120:
        if 3.5<pH<4.3: return 1.5375-0.125*pH
        if 4.3<pH<5:   return 5.9757-1.157*pH
        return 0.546125-0.071225*pH
    if t==150:
        if 3.5<pH<3.8: return 1.0
        if 3.8<pH<5:   return 17.634-7.0945*pH+0.715*pH*pH
        return 0.037

def norsok_m506_CR_anchor(t, fCO2_bar, S_Pa, pH):
    kt = K[t]
    fpH = f_pH(t, pH)
    if t==5:
        return kt*(fCO2_bar**0.36)*fpH
    term = (S_Pa/19.0)**0.146 + 0.0324*math.log10(fCO2_bar)
    expo = 0.36 if t==15 else 0.62
    return kt*(fCO2_bar**expo)*term*fpH

print(norsok_m506_CR_anchor(150, 50, 10, 3.9))
