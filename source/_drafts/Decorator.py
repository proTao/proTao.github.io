# decorator is a use way of closure
# reference: [Python Decorators Overview]:(https://www.pythoncentral.io/python-decorators-overview/)
# reference: [简单 12 步理解 Python 装饰器](http://python.jobbole.com/85056/)
# 通过查看它的 func_closure 属性可以看出函数闭包特性。
# 使用装饰器极大地复用了代码，但是他有一个缺点就是原函数的元信息不见了

# ----------1: @ statement-------------
def test1():
    def decorator(fn):
        def inner(n):
            return fn(n) + 1
        return inner


    # the "@" statement is same as f = decorator(f)
    @decorator
    def f(n):
        return n + 1




# ----------2: a example------------
def test2():
    def wrap_with_prints(fn):
        # This will only happen when a function decorated
        # with @wrap_with_prints is defined
        print('print this when do decorate the function not run the function')
     
        def wrapped():
            # This will happen each time just before
            # the decorated function is called
            print('prepare to run %s' % fn.__name__)
            # Here is where the wrapper calls the decorated function
            fn()
            # This will happen each time just after
            # the decorated function is called
            print('done running %s' % fn.__name__)
     
        return wrapped
     
    @wrap_with_prints
    def func_to_decorate():
        print('some be wrapped')
     
    func_to_decorate()

# ----------3: use to log-------------
def test3():
    def log_calls(fn):
        ''' Wraps fn in a function named "inner" that writes
        the arguments and return value to logfile.log '''
        def inner(*args, **kwargs):
            # Call the function with the received arguments and
            # keyword arguments, storing the return value

            out = fn(*args, **kwargs)
     
            # Write a line with the function name, its
            # arguments, and its return value to the log file
            print('{} called with args {} and kwargs {}, returning {}\n'.format(fn.__name__,  args, kwargs, out))
     
            # Return the return value
            return out
        return inner

    @log_calls
    def add(a,b):
        return a+b
    add(1,2)

# ----------4: multiple decorators-------------
"""
You can chain decorators.
but failing to put decorators in the correct order can cause confusing
it is difficult-to-trace errors.
"""
def test4():
    def b(fn):
        return lambda s: '<b>{}</b>'.format(fn(s))
     
    def em(fn):
        return lambda s: '<em>{}</em>'.format(fn(s))
     
    @b
    @em
    def greet(name):
        return('Hello, {}!'.format(name))

    print(greet("zyt"))


# ---------------5: Decorators with Arguments----------------------------
def test5():
    def add_log_out(log_level):
        def wrapper(f):
            def return_f(*real_para):
                """inner doc
                """
                print("[{}]: {} with parameter {}".format(log_level, f.__name__, real_para))
                return f(*real_para)

            return return_f
        return wrapper

    # same as "add = add_log_out("INFO")(add)"
    @add_log_out("INFO")
    def add(a,b):
        """return a + b
        """
        return a+b

    print(add(1,2))
    print(add.__name__)
    print(add.__doc__)

# ---------------6: reserve old functions information----------------------------
from functools import wraps
def test6():
    def add_log_out(log_level):
        def wrapper(f):
            @wraps(f)
            def return_f(*real_para):
                """inner doc
                """
                print("[{}]: {} with parameter {}".format(log_level, f.__name__, real_para))
                return f(*real_para)

            return return_f
        return wrapper

    # same as "add = add_log_out("INFO")(add)"
    @add_log_out("INFO")
    def add(a,b):
        """return a + b
        """
        return a+b

    print(add(1,2))
    print(add.__name__)
    print(add.__doc__)


if __name__ == "__main__":
    test6()