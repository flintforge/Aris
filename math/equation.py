'''
ARIS
Author:  𝓟𝓱𝓲𝓵.𝓔𝓼𝓽𝓲𝓿𝓪𝓵  @ 𝓕𝓻𝓮𝓮.𝓯𝓻
Date:<2018-05-18 15:52:50>
Released under the MIT License
'''
from math import sqrt,pow,cos,sin,asin,pi

# t : time
# b : starting value
# c : change(start-end)
# d : duration

#0
def linear( t,b,c,d ):
    return c/d * t + b


''' below linear '''

def in_sine( t, b, c, d ) :
    return -c * cos(t/d * (pi/2)) + c + b
#1
def in_quad( t,b,c,d ) :
    t = t/d
    return c*t*t + b
#5
def in_cubic( t, b, c, d ) :
    t = t/d
    return c*t**3 + b
#9
def in_quart( t, b, c, d ) :
    t = t/d
    return c*t**4 + b
#13
def in_quint( t, b, c, d ) :
    t = t/d
    return c*t**5 + b

#21
def in_circ( t, b, c, d ) :
    t = t/d
    return -c * (sqrt(1 - t*t) - 1) + b

#25
def in_expo( t, b, c, d ) :
    if t == 0 :
        return b
    else:
        return c * pow(2, 10 * (t/d - 1)) + b - c * 0.001
#33
def in_back( t,b,c,d ) :
    s = 1.70158 # param overshoot
    t = t/d
    return c*(t)*t*((s+1)*t - s) + b


''' over linear '''


#18
def out_sine( t, b, c, d ) :
    return c * sin(t/d * (pi/2)) + b

def out_quad( t,b,c,d ) :
    t = t/d
    return -c*t*(t-2.0) + b

#6
def out_cubic( t, b, c, d ) :
    t = t/d - 1.
    return c*(t**3 + 1) + b
#10
def out_quart(  t, b, c, d ) :
    t = t/d - 1.
    return -c * (t**4 - 1) + b

#14
def out_quint( t, b, c, d ) :
    t = t/d-1.0
    return c*((t)*t*t*t*t + 1) + b

#22
def out_circ( t, b, c, d ) :
    t = t/d - 1.
    return c * sqrt(1 - (t)*t) + b

#26
def out_expo( t, b, c, d ) :
    if(t == d) :
        return b+c
    else :
        return c * 1.001 * (-pow(2, -10 * t/d) + 1) + b
#34
def out_back(  t, b, c, d ) :
    s = 1.70158 # param overshoot
    t = t/d-1
    return c*((t)*t*((s+1)*t + s) + 1) + b


# inout compound
# can also be composed with the set above
#3
def inoutquad( t,b,c,d ) :
    t = 2.0*t/d
    if t < 1.0 :
        return c/2*t*t + b
    else :
        return -c/2.0 * ((t-1.0)*(t-3.0) - 1.0) + b
#4
def outinquad( t,b,c,d ) :
    if t < d/2.0 :
        return out_quad(t*2.0, b, c/2.0, d )
    else :
        return in_quad((t*2.0)-d, b+c/2.0, c/2.0, d)


#7
def inoutcubic( t, b, c, d ) :
    t /= (d/2)
    if t < 1 :
        return c/2*t*t*t + b
    else :
        t -= 2
        return c/2*((t)*t*t + 2) + b
#8
def outincubic(  t, b, c, d ) :
    if t < d/2.0:
        return out_cubic(t*2.0, b, c/2.0, d)
    else :
        return in_cubic(t*2.0-d, b+c/2.0, c/2.0,d)



#11
def inoutquart(  t, b, c, d ) :
    t = (2.0*t)/d
    if t < 1:
        return c/2*t*t*t*t + b
    else :
        t -= 2.0
        return -c/2.0 * ((t)*t*t*t - 2) + b
#12
def outinquart( t, b, c, d ) :
    if t < d/2 :
        return out_quart(t*2, b, c/2, d)
    else :
        return in_quart((t*2)-d, b+c/2, c/2, d)

#15
def inoutquint( t, b, c, d ) :
    t = 2.0*t/d
    if(t) < 1 :
        return c/2*t*t*t*t*t + b
    else :
        t -= 2.0
        return c/2.0*((t)*t*t*t*t + 2.0) + b
#16
def outinquint( t, b, c, d ) :
    if t < d/2 :
        return out_quint(t*2, b, c/2, d )
    else :
        return in_quint((t*2)-d, b+c/2, c/2, d )


#19
def inoutsine( t, b, c, d ) :
    return -c/2 * (cos(pi*t/d) - 1) + b
#20
def outinsine( t, b, c, d ) :
    if t < d/2:
        return out_sine(t*2, b, c/2, d)
    else:
        return in_sine((t*2)-d, b+c/2, c/2, d)

#23
def inoutcirc( t, b, c, d ) :
    t = t/(d/2)
    if(t) < 1:
        return -c/2 * (sqrt(1 - t*t) - 1) + b
    else:
        t = t-2
        return c/2 * (sqrt(1 - t*t) + 1) + b
#24
def outincirc( t, b, c, d ) :
    if t < d/2:
        return out_circ(t*2, b, c/2, d )
    else :
        return in_circ((t*2)-d, b+c/2, c/2, d)


#27
def inoutexpo( t, b, c, d ) :
    if t == 0:
        return b
    elif t == d:
        return b+c
    else:
        t /= d/2
    if t < 1 :
        return c/2 * pow(2, 10 * (t - 1)) + b - c * 0.0005
    else:
        t -= 1
        return c/2 * 1.0005 * (-pow(2, -10 * t) + 2) + b
#28
def outinexpo(  t, b, c, d ) :
    if t < d/2:
        return out_expo(t*2, b, c/2, d )
    else :
        return in_expo((t*2)-d, b+c/2, c/2, d)
#29
def inelastic( t, b, c, d, a=0):# a=amplitude
    if t == 0 :
        return b
    else :
        t = t/d
        if((t) == 1): return b+c
        else:
            p = d * .3  # periods
            if a < abs(c) :
                a = c
                s = p/4.0
            else :
                s = p/(2*pi) * asin(c/a)
            t -= 1
            return -(a*pow(2,10*(t)) * sin( (t*d-s)*(2*pi)/p )) + b

#30
def outelastic( t,b,c,d, a=0 ) :
    if t == 0:
        return b
    else:
        t /= d
    if t == 1:
        return b+c
    else:
        p = d*.3  # period
        if a < abs(c):
            a = c
            s = p/4.0
        else :
            s = p/(2*pi) * asin(c/a)
        return(a*pow(2,-10*t) * sin( (t*d-s)*(2*pi)/p ) + c + b)

#31
def inoutelastic( t,b,c,d ) :
        if t == 0 :
            return b
        else:
            t /= (d/2)
            if(t == 2) :
                return b+c
            else :
                p = d*(.3*1.5) # period
                a = 0
                if a < abs(c) :
                    a = c
                    s = p/4.0
                else :
                    s = p/(2*pi) * asin(c/a)
                if t < 1:
                    t -= 1
                    return -.5*(a*pow(2,10*(t)) * sin( (t*d-s)*(2*pi)/p )) + b
                else :
                    t -= 1
                    return a*pow(2,-10*(t)) * sin( (t*d-s)*(2*pi)/p )*.5 + c + b

#32
def outinelastic( t,b,c,d ) :
        if t < d/2 :
            return outelastic(t*2, b, c/2, d)
        else :
            return inelastic((t*2)-d, b+c/2, c/2, d)



#35
def inoutback(  t, b, c, d ) :
    s = 1.70158
    s *= 1.525
    t = t/(d/2)
    if(t) < 1 :
        return c/2*(t*t*(((s)+1)*t - s)) + b
    else :
        t -= 2
        return c/2*((t)*t*((s+1)*t + s) + 2) + b
#36
def outinback( t,b,c,d ) :
    if t < d/2 :
        return out_back(t*2, b, c/2, d)
    else :
        return in_back((t*2)-d, b+c/2, c/2, d )
#37
def inbounce( t,b,c,d ) :
    return c - outbounce(d-t, 0, c, d) + b
#38
def outbounce( t,b,c,d ) :
    t /= d
    if t < (1/2.75) :
        return c*(7.5625*t*t) + b
    elif t < (2/2.75):
        t -= (1.5/2.75)
        return c*(7.5625*(t)*t + .75) + b
    elif t < (2.5/2.75) :
        t -= (2.25/2.75)
        return c*(7.5625*(t)*t + .9375) + b
    else :
        t -= (2.625/2.75)
        return c*(7.5625*(t)*t + .984375) + b

#39
def inoutbounce( t, b, c, d ) :
    if t < d/2:
        return inbounce(t*2, 0, c, d) * .5 + b
    else :
        return outbounce(t*2-d, 0, c, d) * .5 + c*.5 + b

#40
def outinbounce( t, b, c, d ) :
    if t < d/2:
        return outbounce(t*2, b, c/2, d)
    else :
        return inbounce((t*2)-d, b+c/2, c/2, d)

