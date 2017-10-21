import statistics


class Calc(object):
    def __init__(self):
        self.fields = {
            'abs': abs,
            'min': min,
            'max': max,
            'mode': statistics.mode,
            'print': print,
            'len': len,
            'round': round,
            'zip': zip,
            'sum': sum,
            'map': map,
            'int': int,
            'float': float
        }

    def add_fields(self, **fields):
        for key, value in fields.items():
            self.fields[key] = value

    def solve(self, equation):
        return eval(equation, {"__builtins__": None}, self.fields)
