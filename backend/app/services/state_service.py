import redis

class StateService:
    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379, db=0)
    
    def test_redis(self):
        try:
            return self.redis.ping()
        except:
            return False