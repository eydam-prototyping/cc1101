INPUT = 0
OUTPUT = 1
PUD_OFF = 0
PUD_DOWN = 1
PUD_UP = 2
RISING_EDGE = 0
FALLING_EDGE = 1
EITHER_EDGE = 2


class _callback:
    def __init__(self):
        pass

    def cancel(self):
        pass
    

class pi:
    def __init__(self):
        pass

    def set_mode(self, pin, mode):
        pass

    def set_pull_up_down(self, pin, pud):
        pass

    def callback(self, pin, edge, callback) -> _callback:
        pass

    def stop(self):
        pass