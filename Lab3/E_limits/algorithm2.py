import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from scipy.interpolate import splprep, splev

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

# Metoda ε-ograniczeń dla problemu dwukryterialnego
def epsilon_constraint_F(j, epsilons):
    def objective(x):
        if j == 1:
            return F1(x[0], x[1])
        elif j == 2:
            return F2(x[0], x[1])
    
    constraints = []
    if j == 1:
        constraints.append({'type': 'ineq', 'fun': lambda x: epsilons[1] - F2(x[0], x[1])})
    elif j == 2:
        constraints.append({'type': 'ineq', 'fun': lambda x: epsilons[0] - F1(x[0], x[1])})
    
    result = minimize(objective, [0.0, 0.0], bounds=[(-1, 1), (-1, 1)], constraints=constraints)
    if result.success:
        return result.x, [F1(result.x[0], result.x[1]), F2(result.x[0], result.x[1])]
    else:
        return None, None

# Metoda ε-ograniczeń dla problemu trzykryterialnego
def epsilon_constraint_G(j, epsilons):
    def objective(x):
        if j == 1:
            return G1(x[0], x[1], x[2])
        elif j == 2:
            return G2(x[0], x[1], x[2])
        elif j == 3:
            return G3(x[0], x[1], x[2])

    constraints = []
    if j != 1:
        constraints.append({'type': 'ineq', 'fun': lambda x: epsilons[0] - G1(x[0], x[1], x[2])})
    if j != 2:
        constraints.append({'type': 'ineq', 'fun': lambda x: epsilons[1] - G2(x[0], x[1], x[2])})
    if j != 3:
        constraints.append({'type': 'ineq', 'fun': lambda x: epsilons[2] - G3(x[0], x[1], x[2])})

    result = minimize(objective, [0.0, 0.0, 0.0], bounds=[(-1, 1), (-1, 1), (-1, 1)], constraints=constraints)
    if result.success:
        return result.x, [G1(result.x[0], result.x[1], result.x[2]),
                          G2(result.x[0], result.x[1], result.x[2]),
                          G3(result.x[0], result.x[1], result.x[2])]
    else:
        return None, None

# Generowanie zbioru Pareto dla problemu dwukryterialnego z metodą ε-ograniczeń
def generate_pareto_set_F_epsilon():
    pareto_points_decision = []
    pareto_points_objective = []
    epsilon_values = np.linspace(0, 2, 20)  # Przykładowe wartości epsilon
    for eps in epsilon_values:
        for j in range(1, 3):
            point_decision, point_objective = epsilon_constraint_F(j, [eps, eps])
            if point_decision is not None:
                pareto_points_decision.append(point_decision)
                pareto_points_objective.append(point_objective)
    return np.array(pareto_points_decision), np.array(pareto_points_objective)

# Generowanie zbioru Pareto dla problemu trzykryterialnego z metodą ε-ograniczeń
def generate_pareto_set_G_epsilon():
    pareto_points_decision = []
    pareto_points_objective = []
    epsilon_values = np.linspace(0, 3, 20)  # Przykładowe wartości epsilon
    for eps in epsilon_values:
        for j in range(1, 4):
            point_decision, point_objective = epsilon_constraint_G(j, [eps, eps, eps])
            if point_decision is not None:
                pareto_points_decision.append(point_decision)
                pareto_points_objective.append(point_objective)
    return np.array(pareto_points_decision), np.array(pareto_points_objective)

# Wizualizacja zbioru Pareto w przestrzeni decyzyjnej 2D
def plot_decision_space_2d(pareto_points, title):
    plt.figure()
    plt.plot(pareto_points[:, 0], pareto_points[:, 1], 'o', label="Punkty Pareto w przestrzeni decyzyjnej")
    plt.xlabel("x1")
    plt.ylabel("x2")
    plt.title(title)
    plt.legend()
    plt.grid()
    plt.show()

# Wizualizacja zbioru Pareto w przestrzeni kryterialnej 2D z aproksymacją spline’ami
def plot_pareto_approximation_2d(pareto_points, title):
    # Sprawdzenie liczby punktów
    if pareto_points.shape[0] < 2:
        print("Zbyt mała liczba punktów do interpolacji.")
        return

    # Usunięcie powtarzających się punktów
    pareto_points = np.unique(pareto_points, axis=0)
    
    # Sortowanie punktów Pareto według osi X
    pareto_points = pareto_points[np.argsort(pareto_points[:, 0])]

    try:
        # Próba interpolacji spline’ami
        tck, _ = splprep([pareto_points[:, 0], pareto_points[:, 1]], s=2)
        new_points = splev(np.linspace(0, 1, 100), tck)

        # Wykres z aproksymacją spline’ami
        plt.figure()
        plt.plot(pareto_points[:, 0], pareto_points[:, 1], 'o', label="Dyskretne punkty Pareto")
        plt.plot(new_points[0], new_points[1], '-', label="Aproksymacja spline'ami")
    except ValueError as e:
        print(f"Nie udało się dopasować spline'a: {e}")
        # Alternatywnie: interpolacja liniowa
        plt.figure()
        plt.plot(pareto_points[:, 0], pareto_points[:, 1], 'o-', label="Interpolacja liniowa zbioru Pareto")

    plt.xlabel("F1")
    plt.ylabel("F2")
    plt.title(title)
    plt.legend()
    plt.grid()
    plt.show()


# Wizualizacja zbioru Pareto w przestrzeni decyzyjnej 3D
def plot_decision_space_3d(pareto_points, title):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(pareto_points[:, 0], pareto_points[:, 1], pareto_points[:, 2], color='b')
    ax.set_xlabel("x1")
    ax.set_ylabel("x2")
    ax.set_zlabel("x3")
    ax.set_title(title)
    plt.show()

# Wizualizacja zbioru Pareto w przestrzeni kryterialnej 3D
def plot_pareto_approximation_3d(pareto_points, title):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot(pareto_points[:, 0], pareto_points[:, 1], pareto_points[:, 2], 'o-', label="Punkty Pareto i ich aproksymacja")
    ax.set_xlabel("G1")
    ax.set_ylabel("G2")
    ax.set_zlabel("G3")
    ax.set_title(title)
    plt.legend()
    plt.show()

# Obliczenia i wizualizacja dla dwukryterialnego przypadku
pareto_decision_F, pareto_objective_F = generate_pareto_set_F_epsilon()
plot_decision_space_2d(pareto_decision_F, "Zbiór P(U, F) dla problemu dwukryterialnego")
plot_pareto_approximation_2d(pareto_objective_F, "Front Pareto FP(U) dla problemu dwukryterialnego")

# Obliczenia i wizualizacja dla trzykryterialnego przypadku
pareto_decision_G, pareto_objective_G = generate_pareto_set_G_epsilon()
plot_decision_space_3d(pareto_decision_G, "Zbiór P(U, F) dla problemu trzykryterialnego")
plot_pareto_approximation_3d(pareto_objective_G, "Front Pareto FP(U) dla problemu trzykryterialnego")
