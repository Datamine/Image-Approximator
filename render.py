# John Loeber | Dec 16 2014 | Python 2.7.8 | www.johnloeber.com

from colormath.color_conversions import convert_color
from colormath.color_objects import LabColor, sRGBColor
from copy import deepcopy
from sys import argv, exit
from PIL import Image, ImageDraw
from time import sleep
import pygame

class Triangle(object):
    """
    To collect the coords marking each triangle, and for related computations.
    """
    def __init__(self,p1,p2,p3):
        """
        Where p1, p2, p3 are all tuples of (x,y) coords
        """
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
    def split(self):
        # defining the hypotenuse as the two points that form the line
        hypotenuse = max([(self.p1,self.p2),(self.p1,self.p3),(self.p2,self.p3)],l2norm)
        halfway = ((hypotenuse[0][0]+hypotenuse[1][0])/2.0, 
                   (hypotenuse[0][1]+hypotenuse[1][1])/2.0)
        opposite = [x for x in [self.p1,self.p2,self.p3] if x not in hypotenuse][0]
        return Triangle(hypotenuse[0],halfway,opposite), Triangle(hypotenuse[1],halfway,opposite)
    def area(self):
        # using Heron's formula
        a = l2norm(self.p1,self.p2)
        b = l2norm(self.p2,self.p3)
        c = l2norm(self.p1,self.p3)
        s = (a+b+c)/2.0
        return (s*(s-a)*(s-b)*(s-c))**0.5
    def getpoints(self):
        # return all coordinates inside the triangle
        # using barymetric method for testing point-in-triangle 
        # made reference to http://jsfiddle.net/PerroAZUL/zdaY8/1
        coords = []
        area = self.area()
        sign = -1 if area <0 else 1
        minx = min(self.p1[0],self.p2[0],self.p3[0])
        miny = min(self.p1[1],self.p2[1],self.p3[1])
        maxx = max(self.p1[0],self.p2[0],self.p3[0])+1
        maxy = max(self.p1[1],self.p2[1],self.p3[1])+1
        for x in range(minx,maxx):
            for y in range(miny,maxy):
                s = (self.p1[1] * self.p3[0] - self.p1[0] * self.p3[1] + (self.p3[1] - self.p1[1]) * x + (self.p1[0] - self.p3[0]) * y) * sign
                if s > 0:
                    t = (self.p1[0] * self.p2[1] - self.p1[1] * self.p2[0] + (self.p1[1] - self.p2[1]) * x + (self.p2[0] - self.p1[0]) * y) * sign
                    if t > 0 and (s+t) < 2 * area * sign:
                        coords.append(x,y)
        return coords
        
def l2norm(a,b):
    """
    Returns the L2-Norm of two points.
    """
    return ((b[0]-a[0])**2+(b[1]-a[1])**2)**0.5

def getinput():
    """
    Parses the user's command-line input.
    """
    depth = int(argv[1])
    if depth < 1:
        print "Error! Depth too small! Must be at least 1. Exiting."
        exit(0)
    try:
        im = Image.open(argv[2])
    except:
        print "Error: can't open submitted image. Exiting."
        exit(0)
    if im.size[0] < 10 or im.size[1] < 10:
        # Arbitrary dim reqs. Little point in running this on small imgs.
        print "Image too small. Minimum dimensions are 10x10. Exiting."
        exit(0)
    return depth, im

def getaverage(list):
    """
    Returns the average color of a list of colors in the Lab Color Space
    """
    lenl = len(list)
    suml, suma, sumb = 0.0,0.0,0.0
    for x in list:
        suml += x.lab_l
        suma += x.lab_a
        sumb += x.lab_b
    return LabColor(lab_l = suml/lenl, lab_a = suma/lenl, lab_b = sumb/lenl)

def main():
    depth, im = getinput()
    pygame.init()
    screen = pygame.display.set_mode(im.size)

    title = pygame.font.Font('BebasNeue.ttf',72)
    message = title.render("Loading...",1,(200,200,0))
#    screen.blit(message,((im.size[0]-message.get_rect().width)/2,(im.size[1]-message.get_rect().height)/2))
    screen.blit(message,(50,50))
    pygame.display.flip()
    

    imagedata = list(im.getdata())
    imagecolors = [sRGBColor(a/255.0,b/255.0,c/255.0) for (a,b,c) in imagedata]
    imagelab = [convert_color(x,LabColor) for x in imagecolors]

## making the average-colored rectangle

    avimlab = convert_color(getaverage(imagelab),sRGBColor)
    avgimagergb = tuple(map(lambda x: int(round(x)), 
                        (avimlab.rgb_r*255,avimlab.rgb_g*255,avimlab.rgb_b*255)))

    display = Image.new("RGB",im.size,avgimagergb)
    string = display.tostring()
    toshow = pygame.image.fromstring(string,im.size,"RGB")
    screen.blit(toshow,(0,0))
    pygame.display.flip()

## splitting the rectangle into two triangles    

    T1 = Triangle((0,0),(im.size[0],0),(im.size[0],im.size[1]))
    T2 = Triangle((0,0),(0,im.size[1]),(im.size[0],im.size[1]))
    t1coords = T1.getpoints()
    t2coords = T1.getpoints()    

    for coords in [t1coords,t2coords]:
        suml,suma,sumb = 0.0,0.0,0.0
        update = []
        count = 0
        for (x,y) in coords:
            flat = x+(y*im.size[0])
            update.append(flat)
            count += 1
            suml += imagelab[x].lab_l
            suma += imagelab[x].lab_a
            sumb += imagelab[x].lab_b
        
        newavg = convert_color(LabColor(lab_l = suml/count,lab_a = suma/count, lab_b = sumb/count),sRGBColor)
        newavgimagergb = tuple(map(lambda x: int(round(x)), (newavg.rgb_r*255,newavg.rgb_g*255,newavg.rgb_b*255)))
        for i in update:
            display.putpixel((i%im.size[0],i/im.size[1]),newavgimagergb)

    newstr = display.tostring()
    toshow = pygame.image.fromstring(newstr,im.size,"RGB")
    screen.blit(toshow,(0,0))
    pygame.display.flip()

        

    """
    gradient = im.size[1]/float(im.size[0])
    count = 0
    suml,suma,sumb = 0.0,0.0,0.0
    update = []
    for x in range(im.size[0] * im.size[1]):
        if (x%im.size[1] <= x/im.size[0] * gradient):
            update.append(x)
            count +=1
            suml += imagelab[x].lab_l
            suma += imagelab[x].lab_a
            sumb += imagelab[x].lab_b
    newavg = convert_color(LabColor(lab_l = suml/count,lab_a = suma/count, lab_b = sumb/count),sRGBColor)
    newavgimagergb = tuple(map(lambda x: int(round(x)), (newavg.rgb_r*255,newavg.rgb_g*255,newavg.rgb_b*255)))
    for i in update:
        display.putpixel((i%im.size[0],i/im.size[1]),newavgimagergb)
    newstr = display.tostring()
    toshow = pygame.image.fromstring(newstr,im.size,"RGB")
    screen.blit(toshow,(0,0))
    pygame.display.flip()
    """



    sleep(5)

    pxtogo = deepcopy(imagelab)
    pxhandled = []
        
if __name__=="__main__":
    main()
