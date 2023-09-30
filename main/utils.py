import math

def equationroots( a, b, c):
 
    # calculating discriminant using formula
    dis = b * b - 4 * a * c
    sqrt_val = math.sqrt(abs(dis))
     
    # checking condition for discriminant
    if dis > 0:
        return[(-b + sqrt_val)/(2 * a), (-b - sqrt_val)/(2 * a)]

     
    elif dis == 0:
        return [(-b / (2 * a))]
     
    # when discriminant is less than 0
    else:
        raise Exception("Complex Roots")