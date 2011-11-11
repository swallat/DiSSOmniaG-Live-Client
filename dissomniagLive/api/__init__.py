class ApiProvider(object):
    
    def update(self, *args, **kwargs):
        from . import Update
        return Update.update(*args, **kwargs)
    
    def wait(self):
        print("Enter waiting")
        import time
        time.sleep(60)
        print("Leaving wait")
        return True


