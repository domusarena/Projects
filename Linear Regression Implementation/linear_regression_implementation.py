import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# parameters to be calculated
theta = np.zeros((2,1))

# function to fit regression line to data
def fit_linear_regression (data_file):
    data = pd.read_csv(data_file, header = None, dtype='float64')

    X = data[[0]].to_numpy()
    y = data[[1]].to_numpy()
    N = len(y)

    # plot data
    plt.scatter(X, y)

    X_new = np.hstack([np.ones((N,1)), X])

    # gradient descent parameters
    iterations = 1500
    alpha = 0.01

    global theta

    # gradient descent
    for i in range(0,iterations):
        h = X_new @ theta
        error = h - y
        theta_change = alpha * (1/N) * X_new.T @ error
        theta = theta - theta_change
    
    print(np.array2string(theta[0])[1:-1])
    print("The fitted line has the equation: y = " + np.array2string(theta[0])[1:-1] + " + " + np.array2string(theta[1])[1:-1] + " x")

    # plot fitted regression line against data
    x = np.linspace(X.min(), X.max(), 50)
    y_fit = theta[0] + theta[1] * x
    plt.scatter(X, y)
    plt.plot(x, y_fit, '-r')
    plt.show

# function to predict response values from certain input variables
def predict_response(x):
    result = theta[0] + theta[1] * x
    print("The predicted response for " + str(x) + " is: " + np.array2string(result)[1:-1])

if __name__ == '__main__':
    fit_linear_regression('ex1data1.txt')

    predict_response(35000)
