"""doc string"""


class Application(object):
    """doc string"""
    flags = []
    target = 24

    def __init__(self, target):
        self.flags = ["+", "-", "x", "/"]
        self = target

    def calculate(self, number1, number2, number3, number4):
        """doc string"""
        count = 0
        numbers = [number1, number2, number3, number4]
        for number in numbers[0:]:
            for flag in self.flags[0:]:
                if flag == "+":
                    print flag


if __name__ == "__main__":
    application = Application(24)
    application.calculate(4, 5, 1, 9)
