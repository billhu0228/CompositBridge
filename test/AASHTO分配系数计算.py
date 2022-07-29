import pickle

from src.CompositeBridge import CompositeBridge

modelName = "M1"
with open("../bin/%s/bridge.pickle" % modelName, 'rb') as f:
    Bridge: CompositeBridge = pickle.load(f)

h = Bridge.get_parameters()
S = h["S"]
L = h["L"]
Kg = h['Kg']
ts = h['ts']

g_in = 0.06 + (S / 4300) ** 0.4 * (S / L) ** 0.3 * (Kg / (L * ts ** 3)) ** 0.1
print("单车道弯矩系数=%.3f" % (g_in))
