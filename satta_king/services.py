import numpy as np
from collections import Counter
from sklearn.ensemble import RandomForestClassifier

def get_tens(number):
    return number // 10

def get_ones(number):
    return number % 10

def number_frequency(data):
    freq = {}
    for n in data:
        freq[n] = freq.get(n, 0) + 1
    return freq

def tens_frequency(data):
    freq = {}
    for n in data:
        t = get_tens(n)
        freq[t] = freq.get(t, 0) + 1
    return freq

def ones_frequency(data):
    freq = {}
    for n in data:
        o = get_ones(n)
        freq[o] = freq.get(o, 0) + 1
    return freq

# --- HEURISTIC PREDICTOR ---
def recent_pattern_score(number, history):
    if not history: return 0
    score = 0
    last = history[-1]
    difference = abs(number - last)

    if difference <= 5: score += 10
    elif difference <= 15: score += 6
    else: score += 2

    if get_ones(number) == get_ones(last): score += 5
    if get_tens(number) == get_tens(last): score += 5
    return score

def frequency_score(number, history):
    score = 0
    num_freq = number_frequency(history)
    tens_freq = tens_frequency(history)
    ones_freq = ones_frequency(history)

    if number in num_freq: score += num_freq[number] * 5
    t = get_tens(number)
    if t in tens_freq: score += tens_freq[t] * 2
    o = get_ones(number)
    if o in ones_freq: score += ones_freq[o] * 2
    return score

def trend_score(number, history):
    if not history: return 0
    score = 0
    avg = np.mean(history)
    distance = abs(number - avg)
    if distance <= 10: score += 8
    elif distance <= 25: score += 5
    else: score += 1
    return score

def calculate_score(number, history):
    score = 0
    score += recent_pattern_score(number, history)
    score += frequency_score(number, history)
    score += trend_score(number, history)
    return score

def predict_heuristic(history, count=10):
    all_scores = []
    # Using 0-99 like original script (00 is considered 0 or 100? In original it is 0-99 or MIN_NUMBER to MAX_NUMBER). In original numbers2.py, it's 0-99.
    for number in range(0, 100):
        score = calculate_score(number, history)
        all_scores.append((number, score))
    all_scores.sort(key=lambda x: x[1], reverse=True)
    return [x[0] for x in all_scores[:count]]

def calculate_digit_score(digit, history):
    score = 0
    last = history[-1]
    
    difference = abs(digit - last)
    if difference == 0: score += 10
    elif difference <= 2: score += 6
    else: score += 2

    freq = {}
    for n in history:
        freq[n] = freq.get(n, 0) + 1
    if digit in freq: score += freq[digit] * 5

    avg = np.mean(history)
    distance = abs(digit - avg)
    if distance <= 2: score += 8
    elif distance <= 4: score += 5
    else: score += 1
    return score

def predict_heuristic_digits(history, count=5):
    all_scores = []
    for digit in range(0, 10):
        score = calculate_digit_score(digit, history)
        all_scores.append((digit, score))
    all_scores.sort(key=lambda x: x[1], reverse=True)
    return [x[0] for x in all_scores[:count]]


# --- MACHINE LEARNING PREDICTOR ---
def pad_predictions(preds, history_fallback, count, is_digit=False):
    preds = list(preds)
    if len(preds) < count:
        freq = Counter(history_fallback)
        for item, _ in freq.most_common():
            if item not in preds:
                preds.append(item)
            if len(preds) == count:
                break
    if len(preds) < count:
        domain = range(0, 10) if is_digit else range(1, 101)
        for item in domain:
            if item not in preds:
                preds.append(item)
            if len(preds) == count:
                break
    return preds[:count]

def create_features_and_labels(history, lag_size=10):
    X = []
    y_num = []
    for i in range(lag_size, len(history)):
        window = history[i-lag_size:i]
        features = []
        for val in window:
            features.extend([val, val // 10, val % 10])
        features.append(np.mean(window))
        features.append(np.std(window))
        X.append(features)
        y_num.append(history[i])
    return np.array(X), np.array(y_num)

def predict_ml(history, count=10, is_digit=False):
    lag_size = 10
    if len(history) <= lag_size + 2:
        return pad_predictions([], history, count, is_digit=is_digit)

    X_train, y_num = create_features_and_labels(history, lag_size)
    
    current_window = history[-lag_size:]
    current_features = []
    for val in current_window:
        current_features.extend([val, val // 10, val % 10])
    current_features.append(np.mean(current_window))
    current_features.append(np.std(current_window))
    X_test = np.array([current_features])

    rf_num = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_num.fit(X_train, y_num)
    
    num_probs = rf_num.predict_proba(X_test)[0]
    num_classes = rf_num.classes_
    
    top_nums_indices = np.argsort(num_probs)[::-1]
    predicted_numbers = [int(num_classes[i]) for i in top_nums_indices[:count]]
    
    predicted_numbers = pad_predictions(predicted_numbers, history, count, is_digit=is_digit)
    return predicted_numbers
