import mpmath as mp
N = mp.mpf('137524771864208156028430259349934309717')
p1 = mp.mpf('37084900000000000001')
k = mp.mpf('0.3')
mp.dps = 100
log_N = mp.log(N)
log_p1 = mp.log(p1)
m1 = (k / (2 * mp.pi)) * (log_N - 2 * log_p1)
print(m1)