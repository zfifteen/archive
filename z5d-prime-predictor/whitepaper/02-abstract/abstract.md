# Abstract

This draft abstract records the current implemented predictor and separates it from broader exploratory framing. The repository currently ships a cross-language nth-prime predictor that combines a calibrated closed-form seed with short forward refinement to a probable prime. Exactness is locked only on the shipped benchmark grid `n = 10^0 ... 10^18` through committed lookup values shared across the C, Python, and Java implementations. Outside that grid, the code returns an empirical probable-prime result rather than a proof that the returned value is the exact nth prime.

The wider Z5D language around five-dimensional geodesics, Riemann-inspired structure, and geofac alignment remains exploratory research context. Those ideas motivate experiments in this repository, but they are not the active algorithm implemented in the current predictor. This white-paper draft should therefore be read as a current-state technical note plus a research agenda, not as a formal validation claim.

**Keywords:** nth-prime prediction, calibrated closed-form seed, probable-prime refinement, cross-language parity, exploratory research notes
