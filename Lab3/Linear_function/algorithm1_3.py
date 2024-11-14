import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from scipy.interpolate import splprep, splev, griddata

# Definicje funkcji celu dla problemu dwukryterialnego
def F1(x, y):
    return np.sin(x) + y**2  # Nieliniowa funkcja trygonometryczno-kwadratowa

def F2(x, y):
    return np.cos(y) + x**2  # Nieliniowa funkcja trygonometryczno-kwadratowa

# Definicje funkcji celu dla problemu trzykryterialnego
def G1(x, y, z):
    return x**2 + y**2 + z**2  # Funkcja kwadratowa

def G2(x, y, z):
    return (x - 1)**2 + (y - 1)**2 + z**2  # Funkcja kwadratowa

def G3(x, y, z):
    return x * y * z  # Nieliniowa funkcja iloczynowa

# Funkcja skalaryzowana dla problemu dwukryterialnego
def scalarized_function_F(x, lambda_weights):
    return lambda_weights[0] * F1(x[0], x[1]) + lambda_weights[1] * F2(x[0], x[1])

# Funkcja skalaryzowana dla problemu trzykryterialnego
def scalarized_function_G(x, lambda_weights):
    return (lambda_weights[0] * G1(x[0], x[1], x[2]) +
            lambda_weights[1] * G2(x[0], x[1], x[2]) +
            lambda_weights[2] * G3(x[0], x[1], x[2]))

# Generowanie kombinacji wag dla skalaryzacji
def generate_lambda_vectors(n, step=0.1):
    if n == 2:
        return [np.array([l1, 1 - l1]) for l1 in np.arange(0, 1 + step, step)]
    elif n == 3:
        return [np.array([l1, l2, 1 - l1 - l2]) for l1 in np.arange(0, 1 + step, step)
                for l2 in np.arange(0, 1 - l1 + step, step) if l1 + l2 <= 1]

# Generowanie zbioru Pareto w przestrzeni decyzyjnej i kryterialnej dla problemu dwukryterialnego
def generate_pareto_set_F(lambda_vectors):
    pareto_points_decision = []
    pareto_points_objective = []
    for lambdas in lambda_vectors:
        result = minimize(scalarized_function_F, [0.0, 0.0], args=(lambdas,), bounds=[(-1, 1), (-1, 1)])
        if result.success:
            pareto_points_decision.append(result.x)
            pareto_points_objective.append([F1(result.x[0], result.x[1]), F2(result.x[0], result.x[1])])
    return np.array(pareto_points_decision), np.array(pareto_points_objective)

# Generowanie zbioru Pareto w przestrzeni decyzyjnej i kryterialnej dla problemu trzykryterialnego
def generate_pareto_set_G(lambda_vectors):
    pareto_points_decision = []
    pareto_points_objective = []
    for lambdas in lambda_vectors:
        result = minimize(scalarized_function_G, [0.0, 0.0, 0.0], args=(lambdas,), bounds=[(-1, 1), (-1, 1), (-1, 1)])
        if result.success:
            pareto_points_decision.append(result.x)
            pareto_points_objective.append([G1(result.x[0], result.x[1], result.x[2]),
                                            G2(result.x[0], result.x[1], result.x[2]),
                                            G3(result.x[0], result.x[1], result.x[2])])
    return np.array(pareto_points_decision), np.array(pareto_points_objective)

# Wizualizacja zbioru Pareto i aproksymacja spline’ami w 2D
def plot_pareto_approximation_2d(pareto_points, title, xlabel, ylabel):
    # Sortowanie punktów po osi X, aby zapewnić poprawne dopasowanie spline'a
    pareto_points = pareto_points[np.argsort(pareto_points[:, 0])]

    # Interpolacja spline’ami lub liniowa, jeśli wystąpi błąd
    try:
        tck, _ = splprep([pareto_points[:, 0], pareto_points[:, 1]], s=0)
        new_points = splev(np.linspace(0, 1, 100), tck)
        plt.plot(new_points[0], new_points[1], '-', label="Aproksymacja spline'ami")
    except ValueError:
        plt.plot(pareto_points[:, 0], pareto_points[:, 1], 'o-', label="Interpolacja liniowa zbioru Pareto")

    # Wykres punktów Pareto
    plt.plot(pareto_points[:, 0], pareto_points[:, 1], 'o', label="Dyskretne punkty Pareto")
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend()
    plt.grid()
    plt.show()


# Wizualizacja aproksymowanego zbioru Pareto w 3D
from mpl_toolkits.mplot3d import Axes3D

def plot_pareto_approximation_3d(pareto_points, title):
    # Przygotowanie danych do wykresu 3D
    G1_vals = pareto_points[:, 0]
    G2_vals = pareto_points[:, 1]
    G3_vals = pareto_points[:, 2]

    # Wykres 3D punktów Pareto z linią łączącą punkty
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot(G1_vals, G2_vals, G3_vals, 'o-', label="Dyskretne punkty Pareto i ich aproksymacja liniowa")
    ax.set_xlabel("G1")
    ax.set_ylabel("G2")
    ax.set_zlabel("G3")
    ax.set_title(title)
    plt.legend()
    plt.show()


# Parametry skalaryzacji
lambda_vectors_2D = generate_lambda_vectors(2)
lambda_vectors_3D = generate_lambda_vectors(3)

# Obliczenia i wizualizacja dla dwukryterialnego przypadku
pareto_decision_F, pareto_objective_F = generate_pareto_set_F(lambda_vectors_2D)
plot_pareto_approximation_2d(pareto_decision_F, "Zbiór P(U, F) dla problemu dwukryterialnego", "x", "y")
plot_pareto_approximation_2d(pareto_objective_F, "Front Pareto FP(U) dla problemu dwukryterialnego", "F1", "F2")

# Obliczenia i wizualizacja dla trzykryterialnego przypadku
pareto_decision_G, pareto_objective_G = generate_pareto_set_G(lambda_vectors_3D)
plot_pareto_approximation_3d(pareto_decision_G, "Zbiór P(U, F) dla problemu trzykryterialnego")
plot_pareto_approximation_3d(pareto_objective_G, "Front Pareto FP(U) dla problemu trzykryterialnego")
