class ApiProvider(object):
    
    def add(self, a, b):
        from . import SimpleMath
        return SimpleMath.add(a, b)
    
    def sub(self, a, b):
        from . import SimpleMath
        return SimpleMath.sub(a, b)

    def mult(self, a, b):
        from . import SimpleMath
        return SimpleMath.mult(a, b)

    def div(self, a, b):
        from . import SimpleMath
        return SimpleMath.div(a, b)
    
    def wait(self):
        print("Enter waiting")
        import time
        time.sleep(60)
        print("Leaving wait")
        return True


