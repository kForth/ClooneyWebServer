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
            'zip': lambda *arg: list(zip(*arg)),
            'zip_sum': lambda arg: [sum(e) for e in arg],
            'sum': sum,
            'map': map,
            'int': int,
            'float': float,
            'list': list
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
