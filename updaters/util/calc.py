import statistics


class Calc(object):
    def __init__(self):
        self.fields = {
            'abs': abs,
            'min': min,
            'max': max,
            'mode': statistics.mode,
            'mean': statistics.mean,
            'print': print,
            'len': len,
            'round': round,
            'zip': lambda *x: list(zip(*x)),
            'zip_sum': lambda x: [sum(e) for e in x],
            'sum': sum,
            'map': map,
            'int': int,
            'float': float
        }

    def add_fields(self, **fields):
        for key, value in fields.items():
            self.fields[key] = value

    def solve(self, equation):
        try:
            value = eval(equation, {"__builtins__": None}, self.fields)
            return value
        except Exception as ex:
            print(equation)
            print(ex)
            raise ex
