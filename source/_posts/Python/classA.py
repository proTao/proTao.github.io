class A(object):
    value = "python"
    def __init__(self):
        print("A::init")

    def f(self):
        print("A::f")

    def g(self, a):
        self.value = a
        print("A::g -> ", self.value)

a=A()
a.f()
a.g(10)
