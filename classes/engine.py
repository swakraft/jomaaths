from datetime import datetime
from typing import Literal
from random import Random
from init import client
from discord import Message, TextChannel, User


class Calc:
    def __init__(self, x, y, operation) -> None:
        self.x = x
        self.y = y
        self.operation = operation
        self.answer = float(eval(f"{x}{operation}{y}"))
    
    def __repr__(self) -> str:
        return f"<{self.x}{self.operation}{self.y}={self.answer}>"

    def __str__(self) -> str:
        return f"{self.x}{self.operation}{self.y}"

    @property
    def markdown_compatible(self) -> str:
        return self.__str__().replace('*', '\*')

class DerivateCalc:
    def __init__(self, polynomial: 'Polynomial', deg: int, eval: int) -> None:
        self.polynomial = polynomial
        self.deg = deg
        self.eval = eval
        for i in range(deg):
            polynomial = polynomial.derivate

        self.der = polynomial
        self.answer = polynomial(eval)
    
    def __str__(self):
        s = ''
        for i in range(self.deg):
            s += "'"

        return f"P(x)={self.polynomial}, solve P{s}({self.eval})".replace('^2', '²').replace('^3', '³').replace('^4', '⁴')
    
    def __repr__(self):
        s = ''
        for i in range(self.deg):
            s += "'"

        return f"P(x)={self.polynomial},  P{s}(x)={self.der}, P{s}({self.eval})={self.answer}"

class RangeSettings:
    def __init__(self, add_range: list[int] = None, subtract_range: list[int] = None, divide_range: list[int] = None, multiply_range: list[int] = None, coef_range: list[int] = None, eval_range: list[int] = None) -> None:
        self.add_range = add_range
        self.subtract_range = subtract_range
        self.divide_range = divide_range
        self.multiply_range = multiply_range
        self.coef_range = coef_range
        self.eval_range = eval_range
    
    def __repr__(self) -> str:
        return f"<RangeSettings add_range={self.add_range}, substract_range={self.subtract_range}, divide_range={self.divide_range}, multiply_range={self.multiply_range}, coef_range={self.coef_range}, eval_range={self.eval_range}>"
    
    def __getitem__(self, key: Literal["+", "-", "/", "*"]):
        match key:
            case "+":
                return self.add_range
        
            case "-":
                return self.subtract_range
            
            case "/":
                return self.divide_range
            
            case "*":
                return self.multiply_range
        
    def __iter__(self):
        return iter([self.add_range, self.subtract_range, self.multiply_range, self.divide_range])

class ProbSettings:
    def __init__(self, add_prob: float | int = 0, subtract_prob: float | int = 0, divide_prob: float | int = 0, multiply_prob: float | int = 0, der_prob: float | int = 0) -> None:
        self.add_prob = add_prob
        self.subtract_prob = subtract_prob
        self.divide_prob = divide_prob
        self.multiply_prob = multiply_prob
        self.der_prob = der_prob
        if sum(self.__iter__()) != 1:
            raise AssertionError("the sum of the probabilities is not equal to 1")
    
    def __repr__(self) -> str:
        return f"<RangeSettings add_prob={self.add_prob}, subtract_prob={self.subtract_prob}, divide_prob={self.divide_prob}, multiply_prob={self.multiply_prob}, der_prob={self.der_prob}>"

    def __iter__(self) -> float | int:
        return iter([self.add_prob, self.subtract_prob, self.multiply_prob, self.divide_prob, self.der_prob])
    
    def __getitem__(self, key: Literal["+", "-", "/", "*"]):
        match key:
            case "+":
                return self.add_prob
        
            case "-":
                return self.subtract_prob
            
            case "/":
                return self.divide_prob
            
            case "*":
                return self.multiply_prob
            
            case "der":
                return self.der_prob

class Polynomial:
    def __init__(self, coeffs: list[int | float], exps: list[int] = None) -> None:
        self.coeffs = coeffs
        if not exps:
            self.exps = [i for i in range(1, len(self.coeffs) + 1)][::-1]

        else:
            self.exps = exps

    def __repr__(self) -> str:
        t = ""
        for coeff, exp, i in zip(self.coeffs, self.exps, range(len(self.exps))):
            if coeff != 0:
                if exp == 1:
                    t += f"{self._sign_(coeff, i == 0)}x"

                elif exp == 0:
                    t += self._sign_(coeff, i == 0)

                else:
                    t += f"{self._sign_(coeff, i == 0)}x^{exp}"

        if t == '':
            return '0'

        return t

    def _sign_(self, n: int | float, f: bool) -> str:
        if n >= 0:
            if not f:
                return f"+{n}"

            else:
                return str(n)

        else:
            return str(n)


    def __call__(self, x: int | float) -> float:
        r = 0
        for coeff, exp in zip(self.coeffs, self.exps):
            r += coeff * x**exp

        return r

    @property
    def derivate(self) -> 'Polynomial':
        der_coeffs = []
        der_exps = []
        for coeff, exp in zip(self.coeffs, self.exps):
            der_coeffs.append(coeff * exp)
            if exp != 0:
                der_exps.append(exp - 1)

            else:
                der_exps.append(0)

        return Polynomial(der_coeffs, der_exps)

class Engine:
    def __init__(self, operations_probs: ProbSettings = ProbSettings(0.25, 0.25, 0.25, 0.25, 0), range: RangeSettings = RangeSettings([1, 10], [1, 10], [1, 10], [1, 10], [-10, 10], [-3, 3]), length: int = 10, seed: int = None) -> None:
        if seed is None:
            seed = int(datetime.now().timestamp() * 1000)

        self.operations = ['+', '-', '/', '*', 'der']
        self.operations_probs = operations_probs
        self.range = range
        self.length = length
        self.seed = seed
        self.random = Random(seed)
        self.calcs: list[Calc | Polynomial] = []
        self.generate()
    
    def generate(self):
        for i in range(self.length):
            operation = self.random.choices(self.operations, list(self.operations_probs))[0]
            match operation:
                case '/':
                    while True:
                        x = self.random.randint(self.range.divide_range[0], self.range.divide_range[1])
                        y = self.random.randint(self.range.divide_range[0], self.range.divide_range[1])
                        if x%y == 0:
                            self.calcs.append(Calc(x, y, operation))
                            break
                
                case '*':
                    x = self.random.randint(self.range.multiply_range[0], self.range.multiply_range[1])
                    y = self.random.randint(self.range.multiply_range[0], self.range.multiply_range[1])
                    self.calcs.append(Calc(x, y, operation))
                
                case '+':
                    x = self.random.randint(self.range.add_range[0], self.range.add_range[1])
                    y = self.random.randint(self.range.add_range[0], self.range.add_range[1])
                    self.calcs.append(Calc(x, y, operation))
                
                case '-':
                    x = self.random.randint(self.range.subtract_range[0], self.range.subtract_range[1])
                    y = self.random.randint(self.range.subtract_range[0], self.range.subtract_range[1])
                    self.calcs.append(Calc(x, y, operation))
                
                case 'der':
                    size = self.random.randint(2, 4)
                    p = Polynomial(
                        [self.random.randint(self.range.coef_range[0], self.range.coef_range[1]) for i in range(size)]
                    )
                    self.calcs.append(DerivateCalc(p, self.random.randint(0, 2), self.random.randint(self.range.eval_range[0], self.range.eval_range[1])))
    
    def __repr__(self) -> str:
        return f"<Engine length={self.length}, operations={self.operations}, operations_probs={self.operations_probs}, range{self.range}"
    
    @classmethod
    def baby(cls):
        return cls(ProbSettings(0.5, 0.5, 0, 0, 0), RangeSettings([1, 10], [1, 10]), 5)

    @classmethod
    def esay(cls):
        return cls(ProbSettings(0.25, 0.25, 0.25, 0.25), RangeSettings([1, 10], [1, 10], [1, 10], [1, 10]), 10)
    
    @classmethod
    def normal(cls):
        return cls(
            range = RangeSettings(
                add_range = [1, 100],
                subtract_range = [1, 100],
                divide_range = [1, 100],
                multiply_range = [1, 10]
            ),
            length = 15
        )

    @classmethod
    def medium(cls):
        return cls(
            operations_probs = ProbSettings(der_prob = 1),
            length = 3
        )
    
    @classmethod
    def from_difficulty_id(cls, difficulty_id: Literal["baby", "easy", "normal", "medium", "custom"]):
        match difficulty_id:
            case "baby":
                return cls.baby()
            
            case "easy":
                return cls.esay()
            
            case "normal":
                return cls.normal()
            
            case "medium":
                return cls.medium()
        
            case "custom":
                return cls()
            
            case _:
                raise ValueError(f"Unknown difficulty id: {difficulty_id}")
    
    async def start(self, channel: TextChannel, user: User) -> list[dict]:
        stats:list[dict] = []
        for calc in self.calcs:
            await channel.send(
                content = str(calc),
            )
        
            def check(message: Message):
                return message.author.id == user.id and message.channel.id == channel.id
            
            start = datetime.now()
            message: Message = await client.wait_for("message", check = check)
            end = datetime.now()
            content = message.content.strip()
            stat = {
                "duration": (end - start).total_seconds(),
                "calc": str(calc),
                "user_answer": content,
                "answer": calc.answer,
                "date": int(datetime.now().timestamp())
            }

            try: 
                content = int(content)
            
            except:
                message.reply(content = "Please only send numbers")
            
            if content == calc.answer:
                #await message.add_reaction("✅")
                stat['success'] = True
            
            else:
                #await message.add_reaction("😐")
                stat['success'] = False
            
            stats.append(stat)
        
        return stats
