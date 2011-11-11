class ApiProvider(object):
    
    def update(self, infoXml):
        from . import Update
        return Update.update(infoXml)
    
    def add(self, a, b):
        return a+b
    
    def wait(self):
        print("Enter waiting")
        import time
        time.sleep(60)
        print("Leaving wait")
        return True


