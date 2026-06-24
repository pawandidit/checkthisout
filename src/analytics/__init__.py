import math
from scipy.stats import norm

def compute_greeks(S, K, T, r, sigma, option_type="call"):
    if T <= 0 or sigma <= 0:
        return {"delta": 0, "gamma": 0, "theta": 0, "vega": 0, "rho": 0}

    d1 = (math.log(S/K) + (r + 0.5*sigma**2)*T) / (sigma*math.sqrt(T))
    d2 = d1 - sigma*math.sqrt(T)

    if option_type=="call":
        delta = norm.cdf(d1)
        theta = (-S*norm.pdf(d1)*sigma/(2*math.sqrt(T)) - r*K*math.exp(-r*T)*norm.cdf(d2))
        rho = K*T*math.exp(-r*T)*norm.cdf(d2)
    else:
        delta = -norm.cdf(-d1)
        theta = (-S*norm.pdf(d1)*sigma/(2*math.sqrt(T)) + r*K*math.exp(-r*T)*norm.cdf(-d2))
        rho = -K*T*math.exp(-r*T)*norm.cdf(-d2)

    gamma = norm.pdf(d1)/(S*sigma*math.sqrt(T))
    vega = S*norm.pdf(d1)*math.sqrt(T)

    return {"delta": delta, "gamma": gamma, "theta": theta, "vega": vega, "rho": rho}
