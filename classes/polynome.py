class Polynome:
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
    def derivate(self) -> 'Polynome':
        der_coeffs = []
        der_exps = []
        for coeff, exp in zip(self.coeffs, self.exps):
            der_coeffs.append(coeff * exp)
            if exp != 0:
                der_exps.append(exp - 1)
            
            else:
                der_exps.append(0)
        
        return Polynome(der_coeffs, der_exps)