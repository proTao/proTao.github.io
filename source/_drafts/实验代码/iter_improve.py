def iter_improve(update, test, guess=0):
    while not test(guess):
        guess = update(guess)
        print("guess:", guess)
    return guess
    
def newton_update(f):
    def update(x):
        return x - f(x) / approx_derivative(f, x)
    return update
    
def find_solution(f, init=0):
    def test(x):
        return approx_eq(f(x), 0)
    return iter_improve(newton_update(f), test, guess=init)
    
    
def approx_derivative(f, x, delta=1e-5):
    df = f(x + delta) - f(x)
    derivation = df/delta
    print("derivation:", derivation)
    return derivation
    
    
def near(x, f, g):
    return approx_eq(f(x), g(x))
    
def approx_eq(x, y, tolerance=1e-5):
    return abs(x - y) < tolerance


if __name__ == "__main__":
    print(find_solution(lambda x:x**2-2))
