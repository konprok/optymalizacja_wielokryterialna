import time
import math

def naive_no_filter(X):
    P = []
    comparison_count = 0
    start_time = time.time()
    for i in range(len(X)):
        Y = X[i]
        dominated = False
        for j in range(len(X)):
            comparison_count += 1
            if i != j and all(X[j][k] <= Y[k] for k in range(len(Y))):
                dominated = True
                break
        if not dominated:
            P.append(Y)
    exec_time = time.time() - start_time
    return P, exec_time, comparison_count

def naive_with_filter(X):
    P = []
    comparison_count = 0
    start_time = time.time()
    i = 0
    while i < len(X):
        Y = X[i]
        dominated = False
        j = i + 1
        while j < len(X):
            comparison_count += 1
            if all(X[j][k] <= Y[k] for k in range(len(Y))):
                dominated = True
                break
            elif all(Y[k] <= X[j][k] for k in range(len(Y))):
                j += 1
            else:
                j += 1
        if not dominated:
            P.append(Y)
        i += 1
    exec_time = time.time() - start_time
    return P, exec_time, comparison_count


def distance_from_ideal(point, ideal=None):
    if ideal is None:
        ideal = [0] * len(point)
    return math.sqrt(sum((point[k] - ideal[k])**2 for k in range(len(point))))

def sort_and_filter(X):
    X_sorted = sorted(X, key=lambda point: distance_from_ideal(point))
    result, exec_time, comparison_count = naive_with_filter(X_sorted)
    return result, exec_time, comparison_count

# # Przykładowe dane testowe
# X = [
#     (5,5,3), (3,6,4), (4,4,5), (5,3,6), 
#     (3,3,2), (1,8,1), (3,4,7), (4,5,3), 
#     (3,10,5), (6,6,8), (4,1,2), (3,5,3)
# ]
# result_no_filter, time_no_filter, comparisons_no_filter = naive_no_filter(X[:])
# result_with_filter, time_with_filter, comparisons_with_filter = naive_with_filter(X[:])
# result_sorted_filter, time_sorted_filter, comparisons_sorted_filter = sort_and_filter(X[:])

# print("Bez filtrowania:")
# print("Punkty niezdominowane:", result_no_filter)
# print("Czas wykonania:", time_no_filter)
# print("Liczba porównań współrzędnych:", comparisons_no_filter)
# print("\nZ filtrowaniem:")
# print("Punkty niezdominowane:", result_with_filter)
# print("Czas wykonania:", time_with_filter)
# print("Liczba porównań współrzędnych:", comparisons_with_filter)
# print("\nPo sortowaniu odległości i filtrowaniu:")
# print("Punkty niezdominowane:", result_sorted_filter)
# print("Czas wykonania:", time_sorted_filter)
# print("Liczba porównań współrzędnych:", comparisons_sorted_filter)
