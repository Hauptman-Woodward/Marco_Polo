
class foo():
    def __init__(self, dogs):
        self.dogs = dogs
    
    @classmethod
    def make(cls, dogs):
        return cls(dogs=10)
    
    def new_foo(self):
        self = foo.make(10)
f = foo(5)
f.new_foo()
print(f.dogs)