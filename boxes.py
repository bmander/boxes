from PIL import Image
from math import sin, cos, pi, radians

import Image, ImageDraw

def plotterify(points):
    builder = []
    
    builder.append( "PU%d,%d;"%(points[0][0], points[0][1]) )
    
    builder.append( "PD" )
    
    builder.append( ",".join(["%d,%d"%(x,y) for x, y in points[1:]]) )
        
    builder.append( ";" )
    
    return "".join(builder)

def cons(ary):
    for i in range(len(ary)-1):
        yield ary[i], ary[i+1]

def even(n):
    return n%2==0
    
def odd(n):
    return n%2!=0
    
def move(cursor, x, y):
    return (cursor[0]+x,cursor[1]+y)
    
def move_line(line, vector):
    return [(pt[0]+vector[0],pt[1]+vector[1]) for pt in line]
    
def rotate_point(theta, point):
    x,y = point
    xprime = cos(theta)*x-sin(theta)*y
    yprime = sin(theta)*x+cos(theta)*y
    
    return (xprime, yprime)
    
def rotate_line(theta, line):
    return [rotate_point(theta,point) for point in line]
        
def extent(geometry):
    left = min([x for (x,y) in geometry])
    bottom = min([y for (x,y) in geometry])
    right = max([x for (x,y) in geometry])
    top = max([y for (x,y) in geometry])
        
    return left,bottom,right,top

def make_dovetailed_side(length, teeth, stockwidth,start_high=True):
    if teeth%2!=0 or teeth==0:
        raise Exception( "number of teeth must be greater than 0 and divisible by 2" )
        
    toothwidth = (length-stockwidth)/float(teeth)
    
    pts = [(stockwidth,0)]
    for i in range(teeth):
        pts.append( move(pts[-1],toothwidth,0) )
        
        if even(i):
            pts.append( move(pts[-1], 0, -stockwidth) )
        elif i!=teeth-1:
            pts.append( move(pts[-1], 0, stockwidth) )
            
    return pts
    
def make_box_side(length, width, teeth, stockwidth):
    if teeth%2!=0 or teeth==0:
        raise Exception( "number of teeth must be greater than 0 and divisible by 2" )
        
    toothwidth = length/float(teeth)
    
    pts = [(stockwidth,0)]
    for i in range(teeth):
        pts.append( move(pts[-1],0,toothwidth) )
        
        if even(i):
            pts.append( move(pts[-1], -stockwidth, 0) )
        elif i!=teeth-1:
            pts.append( move(pts[-1], stockwidth, 0) )
            
    pts.append( move(pts[-1], width-stockwidth, 0) )
    
    for i in range(teeth):
        if i==teeth-1:
            pts.append( move(pts[-1],0,-(toothwidth+stockwidth)) )
        else:
            pts.append( move(pts[-1],0,-toothwidth) )
        
        if even(i):
            pts.append( move(pts[-1], stockwidth, 0) )
        elif i!=teeth-1:
            pts.append( move(pts[-1], -stockwidth, 0) )
            
    return pts
    

class LaserBox:
    def __init__(self, dx, dy, dz, stockwidth, dovetail_width):
        self.dx = dx
        self.dy = dy
        self.dz = dz-stockwidth
        self.stockwidth = stockwidth
        self.dovetail_width = dovetail_width
        
    def design(self):
        geom=[]
        
        x_teeth = ((self.dx/(self.dovetail_width*2))+1)*2
        y_teeth = ((self.dy/(self.dovetail_width*2))+1)*2
        z_teeth = ((self.dz/(self.dovetail_width*2))+1)*2
            
        dovetailed_sida_a = make_dovetailed_side(self.dx,x_teeth,self.stockwidth)
        dovetailed_side_b = make_dovetailed_side(self.dy,y_teeth,self.stockwidth)

        geom.extend( dovetailed_sida_a,  )
        geom.extend( move_line(rotate_line(radians(-90),dovetailed_side_b[1:]),(self.dx,0) ) )
        geom.extend( move_line(rotate_line(radians(-180),dovetailed_sida_a[1:]),(self.dx,-self.dy) ) )
        geom.extend( move_line(rotate_line(radians(-270),dovetailed_side_b[1:]),(0,-self.dy) ) )

        box_side_a = make_box_side( self.dz, self.dx, z_teeth, self.stockwidth)
        box_side_b = make_box_side( self.dz, self.dy, z_teeth, self.stockwidth)
        geom.extend( box_side_a )
        geom.extend( move_line(rotate_line(radians(-90),box_side_b[1:]),(self.dx,0) ) )
        geom.extend( move_line(rotate_line(radians(-180),box_side_a[1:]),(self.dx,-self.dy) ) )
        geom.extend( move_line(rotate_line(radians(-270),box_side_b[1:]),(0,-self.dy) ) )
        
        #resize into PLT units
        geom = [(int(round(x*40)),int(round(y*40))) for x,y in geom]
            
        #translate into the first quadrant
        left,bottom,right,top = extent(geom)
        geom = move_line(geom, (-left,-bottom))
        
        return geom

def print_design_image(design, filename="vector.png"):

    geom = [(x,-y) for (x,y) in laserbox.design()]
            
    left,bottom,right,top = extent(geom)

    width = right-left
    height = top-bottom
            
    im = Image.new("RGB",(width+1,height+1))

    geom = move_line(geom, (-left,-bottom))

    draw = ImageDraw.Draw(im)
    for (x1,y1),(x2,y2) in cons(geom):
        line =(x1,y1,x2,y2)
        #print line
        draw.line(line, fill=(255,255,255), width=4)
    del draw

    # write to stdout
    im.save(open(filename,"w"), "PNG")
    
def print_to_plt(design, filename="box.plt"):
    fp = open(filename, "w")
    
    fp.write("SP1;")
    fp.write(plotterify(design))
    
    fp.close()
    
if __name__=='__main__':
    for i in range(5):
        width=3+i*6
        height=3+i*3
        
        print width, height
        
        laserbox = LaserBox( width, width, height, 3, 6 )

        design = laserbox.design()
        
        print_design_image( design, filename="box%d.png"%i )
        
        print_to_plt(design, filename="box%d.plt"%i)
