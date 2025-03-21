from math import sqrt, atan, pi, degrees

class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y


    @property
    def tuple(self):
        return (self.x, self.y)

    @property
    def length(self):
        return sqrt(self.x ** 2 + self.y ** 2)
    @property
    def polar(self):
        return atan(self.y / self.x)
    @property
    def polar360(self):
        if self.x > 0:
            return atan(self.y / self.x)
        elif self.x < 0:
            return atan(self.y / self.x) + pi
        else:
            return 0

    def dotprod(self, other):
        return self.x * other.x + self.y * other.y

    def normalize(self):
        if self.length <= 0:
            return Vector(0, 0)
        return self/self.length

    def limit(self, other: float):
        if self.length > other:
            self.normalize()
            self * other

    def __add__(self, other):
        if isinstance(other, Vector):
            return Vector(self.x + other.x, self.y + other.y)

    def __iadd__(self, other):
        if isinstance(other, Vector):
            self.x += other.x
            self.y += other.y
        return self

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, other: float):
        return Vector(self.x * other, self.y * other)

    def __truediv__(self, other: float):
        return Vector(self.x / other, self.y / other)

    def __neg__(self):
        return Vector(-self.x, -self.y)

    def __str__(self):
        return f"Vector: x={self.x} y={self.y} length={self.length}, angle={degrees(self.polar360)}"
