import sys
import random
import joblib

import numpy as np
import pandas as pd


def sigmoid(x, x0, k):
    return 1 / (1 + np.exp(-k * (x - x0)))


def piecewise_function(transition_time, time):
    transition_time_2 = 86400

    if time < transition_time / 2:
        weight_mofu = 5 * (10**-6) * time

    elif transition_time / 2 <= time < transition_time_2:
        weight_mofu = 10**-5 * time

    else:
        weight_mofu = 0.4

    return min(weight_mofu, 0.4)


def compute_hybrid(tofu_score, mofu_score, time):
    transition_time = 1328
    transition_time_2 = 86400
    decay_rate = 10**-7

    mofu_weight = piecewise_function(transition_time, time)
    tofu_weight = 1 - mofu_weight
    final_score = tofu_weight * tofu_score + mofu_weight * mofu_score

    return final_score, tofu_weight, mofu_weight
