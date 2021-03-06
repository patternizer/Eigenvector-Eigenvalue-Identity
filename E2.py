import numpy as np
from functools import reduce
from numpy import linalg as LA
import matplotlib.pyplot as plt        


# Calculate the norm square of the jth element of the ith eigenvector using the alternate algorithm
# H is a square np.matrix
def vij_sq(H, i, j):
    # Get the size of the matrix
    n = H.shape[0]

    # Get the eigenvalues of the matrix using numpy
    eigenvalues = np.linalg.eigvalsh(H)

    # Determine the jth minor
    Mj = np.delete(np.delete(H, j, 0), j, 1)

    # Get the eigenvalues of the minor
    minor_eigenvalues = np.linalg.eigvalsh(Mj)

    # Calculate the numerator
    numerator = 1.
    for k in range(n - 1):
        numerator *= eigenvalues[i] - minor_eigenvalues[k]

    # Calculate the denominator
    denominator = 1.
    for k in range(n):
        if k == i:
            continue
        denominator *= eigenvalues[i] - eigenvalues[k]

    return numerator / denominator


def eig_sq(H):
    # Get the size of the matrix
    n = H.shape[0]
    res = np.zeros((n, n))

    for i in range(n):
        for j in range(n):
            res[i, j] = vij_sq(H, j, i)

    return res


# Calculate the norm square with performance improvements
def vij_sq_perf(H, i, j):
    # Get the size of the matrix
    n = H.shape[0]

    # Get the eigenvalues of the matrix using numpy
    eigenvalues = np.linalg.eigvalsh(H)

    # Determine the jth minor
    Mj = np.delete(np.delete(H, j, 0), j, 1)

    # Get the eigenvalues of the minor
    minor_eigenvalues = np.linalg.eigvalsh(Mj)

    # Calculate the numerator
    eigenvaluei = eigenvalues[i]
    numerator = reduce(lambda x, y: x * y, [eigenvaluei - minor_eigenvalues[k] for k in range(n - 1)])

    # Calculate the denominator
    denominator = reduce(lambda x, y: x * y, [eigenvaluei - eigenvalues[k] for k in range(n) if k != i])

    return numerator / denominator


def eig_sq_perf(H):
    # Get the size of the matrix
    n = H.shape[0]
    res = np.zeros((n, n))

    for i in range(n):
        for j in range(n):
            res[i, j] = vij_sq_perf(H, j, i)

    return res


# Calculate the norm square of all the elements of all the eigenvectors using the alternate algorithm
# H is a square np.matrix
def eig_sq_vect(H):
    # Get size of the matrix
    n = H.shape[0]

    # Get eigenvalues of the matrix
    eigvals = np.linalg.eigvalsh(H)

    # Create a matrix of all the minors minors and a matrix of eigenvalues as required in the algorithm
    minors = np.empty((n, n - 1, n - 1), dtype=H.dtype)
    eig_matrix = np.empty((n, n - 1))
    for i in range(n):
        minors[i] = np.delete(np.delete(H, i, 0), i, 1)
        eig_matrix[i] = np.delete(eigvals, i)

    # Get eigenvalues of all the minors
    minor_eigvals = np.linalg.eigvalsh(minors)

    # Calculate the numerators and the denominators
    numerator = np.empty((n, n))
    denominator = np.empty((n,))
    for i in range(n):
        numerator[i] = np.prod(eigvals[i] - minor_eigvals, axis=1)
        denominator[i] = np.prod(eigvals[i] - eig_matrix[i])

    return np.divide(numerator.T, denominator.reshape((1, n)))


# Calculate the norm square of all the elements of all the eigenvectors using numpy's built in eigenvector calculator
# H is a square np.matrix
def eig_sq_np(H):
    # Get the eigenvalues and eigenvalues of the matrix
    eigenvalues, eigenvectors = np.linalg.eigh(H)
    return abs(eigenvectors) ** 2


# Prints true for each element that agrees between the E2 method and the method built into numpy
# H is a square np.matrix
# mode determines comparison with normal or improved function
def compare(H, mode=0):
    # The tolerance for comparison purposes
    tol = 1e-12

    # Select function depending upon the value of mode
    if mode == 0:
        res = eig_sq(H)
    elif mode == 1:
        res = eig_sq_perf(H)
    elif mode == 2:
        res = eig_sq_vect(H)
    else:
        raise IndexError

    # Return the comparison matrix
    return abs(res - eig_sq_np(H)) < tol


if __name__ == "__main__":
    
    # FPE as a function of matrix size or not
    sensitivity_analysis = True

    if not sensitivity_analysis:
        
        # Generate a random Hermitian matrix
        # Dimension of the matrix
            
        n = 8
        H = np.random.rand(n, n) + 1j * np.random.rand(n, n)
        H = 0.5 * (H + H.T)

        # Print the second element of the first eigenvector as calculated in both methods
        print("\n--- using the algorithm ---")
        basic = eig_sq(H)
        print("basic implementation: ", basic[0, 1])
        perf = eig_sq_perf(H)
        print("performant implementation: ", perf[0, 1])
        vect = eig_sq_vect(H)
        print("vectorized implementation implementation: ", vect[0, 1])
        
        print("\n--- using numpy ---")
        nump = eig_sq_np(H)
        print(nump[0, 1])
    
    else:
        nmin = 2
        nmax = 50
        fpe_basic_array = np.zeros([nmax-nmin+1])
        fpe_perf_array = np.zeros([nmax-nmin+1])
        fpe_vect_array = np.zeros([nmax-nmin+1])
        for i in range(nmin,nmax+1):    
            n = i
            H = np.random.rand(n, n) + 1j * np.random.rand(n, n)
            H = 0.5 * (H + H.T)
            basic = eig_sq(H)
            perf = eig_sq_perf(H)
            vect = eig_sq_vect(H)
            nump = eig_sq_np(H)
            fpe_basic = 100.*(LA.norm(basic)-LA.norm(nump))/LA.norm(basic)
            fpe_perf = 100.*(LA.norm(perf)-LA.norm(nump))/LA.norm(perf)
            fpe_vect = 100.*(LA.norm(vect)-LA.norm(nump))/LA.norm(vect)
            fpe_basic_array[i-nmin] = fpe_basic
            fpe_perf_array[i-nmin] = fpe_perf
            fpe_vect_array[i-nmin] = fpe_vect

        fig,ax = plt.subplots(figsize=(15,10))
        plt.scatter(np.arange(nmin, nmax+1), fpe_basic_array, label='f(basic-numpy)', marker='o', color='black')
        plt.scatter(np.arange(nmin, nmax+1), fpe_perf_array, label='f(perf-numpy)', marker='.', color='red')
        plt.scatter(np.arange(nmin, nmax+1), fpe_vect_array, label='f(vect-numpy)', marker='o', color='grey')
        plt.legend()
        plt.xlabel('Matrix size, n')
        plt.ylabel('FPE, %')
        plt.title('Sensitivity analysis')
        plt.savefig('sensitivity_analysis.png')
        
