import sys
def L(h):
    h=h.lstrip('#'); r=[int(h[i:i+2],16)/255 for i in (0,2,4)]
    f=lambda v: v/12.92 if v<=0.03928 else ((v+0.055)/1.055)**2.4
    return 0.2126*f(r[0])+0.7152*f(r[1])+0.0722*f(r[2])
def cr(a,b):
    x,y=L(a),L(b); return (max(x,y)+0.05)/(min(x,y)+0.05)
if __name__=='__main__':
    for par in sys.argv[1:]:
        a,b=par.split('/'); print(f"{par:16} {cr(a,b):5.2f}")
