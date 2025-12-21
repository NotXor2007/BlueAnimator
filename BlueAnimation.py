import pygame, sys
from tkinter import colorchooser
import math
import threading

BLACK = (0,0,0)
BLUE = (0,0,240)
RED = (240,0,0)
WHITE = (255,255,255)

class Exporter:

    def __init__(self):
        pass

    def export(self, canvas, app):
        posx,posy = canvas.posx, canvas.posy
        hsize,vsize = canvas.HSize, canvas.VSize
        frames = canvas.frames
        surface = app.window
        data = bytearray(list())
        data.append(10)
        bytedata = hsize.to_bytes(2,"big")
        for index in range(0,len(bytedata),1):
            data.append(bytedata[index])
        bytedata = vsize.to_bytes(2,"big")
        for index in range(0,len(bytedata),1):
            data.append(bytedata[index])
        for frameindex in range(0,len(frames),1):
            canvas.frame = frameindex
            canvas.show(app)
            pygame.display.update()
            for x in range(posx,hsize,1):
                for y in range(posy,vsize,1): 
                    pixel = surface.get_at((x,y))
                    for color in pixel:
                        data.append(color)
        with open("./output.smedia", "wb") as output:
            output.write(data)


class Canvas:

    def __init__(self, posx, posy):
        self.posx, self.posy = posx, posy
        self.HSize = 0
        self.VSize = 0
        self.frames = [[[],],]
        self.frame = 0
        self.thickness = 5
        self.color = (0,0,0)
        self.mouseinc = False
    
    def __mouseInCanvas(self):
        mx, my = pygame.mouse.get_pos()
        if self.posx+self.thickness//2 <= mx <= self.posx+self.HSize-self.thickness//2:
            if self.posy+self.thickness//2 <= my <= self.posy+self.VSize-self.thickness//2:
                self.mouseinc = True
                return
        self.mouseinc = False

    def addFrame(self):
        self.frames.append([[],])

    def handleEvents(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                pygame.display.toggle_fullscreen()
        self.__mouseInCanvas()
        if self.mouseinc:
            pygame.mouse.set_visible(False)
            if event.type == pygame.MOUSEBUTTONUP:
                self.frames[self.frame].append([])
            if event.type == pygame.MOUSEWHEEL: 
                self.thickness += event.y
                if self.thickness < 1: self.thickness = 1
            if event.type == pygame.MOUSEMOTION:
                if pygame.mouse.get_pressed()[0]:
                    self.frames[self.frame][len(self.frames[self.frame])-1].append(pygame.mouse.get_pos())
                elif pygame.mouse.get_pressed()[2]:
                    self.frames[self.frame] = [[],]
        else: pygame.mouse.set_visible(True)

    def show(self, frame):
        self.HSize,self.VSize = frame.window.get_size()
        pygame.draw.rect(frame.window,WHITE,((self.posx,self.posy),(self.HSize,self.VSize)))
        pygame.draw.rect(frame.window,BLACK,((self.posx,self.posy),(self.HSize,self.VSize-self.posy)),10)
        for innerlst in self.frames[self.frame]:
            for i in range(0, len(innerlst), 1):
                if i < len(innerlst) - 1:
                    pygame.draw.line(frame.window,self.color,innerlst[i],innerlst[i+1],self.thickness)
                    pygame.draw.circle(frame.window,self.color,innerlst[i],self.thickness//2)
        if self.mouseinc:
            pygame.draw.circle(frame.window, (abs(180-self.color[0]),abs(180-self.color[1]),abs(180-self.color[2])),pygame.mouse.get_pos(),self.thickness)

class UIColorSelector:

    def __init__(self,posx, posy, thickness, barLength, HMargin, VMargin):
        self.thickness = thickness
        self.barLength = barLength
        self.HMargin, self.VMargin = HMargin, VMargin
        self.posx, self.posy = posx, posy
        self.showColorRect = False
        self.showColorBars = False
        self.colorImg = pygame.Surface((256,256))
        self.blue = 0
        self.rgb = [0,0,0,0]
        self.x1 = self.posx+self.thickness+self.HMargin
        self.x2 = self.posx+self.barLength-1
        self.y = self.posy+self.thickness+self.VMargin

    def __createColorRect(self):
        self.colorImg.lock()
        for green in range(0,255,1):
            for red in range(0,255,1):
                self.colorImg.set_at((red,green),(red,green,self.blue))
        self.colorImg.unlock()

    def addColorRect(self):
        self.showColorRect = True
        self.__createColorRect()
    
    def addColorBars(self):
        self.showColorBars = True
        #self.__createColorBar()

    def mouseOnBar(self):
        mx, my = pygame.mouse.get_pos()
        if self.x1 <= mx <= self.x2:
            if self.y-self.thickness <= my <= self.y+self.thickness*2:
                return True
        return False

    def handleEvents(self,event):
        if event.type == pygame.MOUSEWHEEL:
            if event.y == 1 and self.rgb[self.rgb[len(self.rgb)-1]] < 255: 
                self.rgb[self.rgb[len(self.rgb)-1]] += 1
            elif event.y == -1 and self.rgb[self.rgb[len(self.rgb)-1]] > 0: 
                self.rgb[self.rgb[len(self.rgb)-1]] -= 1
    
    def show(self, frame):
        if self.showColorRect:
            frame.window.blit(self.colorImg,(self.posx+self.thickness,self.posy+self.thickness))
            radius = self.HSize//2*2**0.5+self.thickness
            pygame.draw.circle(frame.window,BLACK,(self.posx+self.HSize//2,self.posy+self.VSize//2),radius,self.thickness)
            angle = (((360/255)*self.blue)/180)*math.pi
            circlex = math.cos(angle)*(radius-self.thickness//2)+self.posx+self.HSize//2
            circley = -math.sin(angle)*(radius-self.thickness//2)+self.posy+self.VSize//2
            pygame.draw.circle(frame.window,WHITE,(circlex,circley),self.thickness*2)
        
        if self.showColorBars:
            while self.rgb[len(self.rgb)-1] < 3:
                pygame.draw.line(frame.window,BLACK,(self.x1,self.y),(self.x2,self.y),self.thickness)
                pygame.draw.circle(frame.window,WHITE,(self.x1+self.barLength*self.rgb[self.rgb[len(self.rgb)-1]]/255,self.y),self.thickness*2)
                
                self.y += self.VMargin
                self.rgb[len(self.rgb)-1] += 1
            self.rgb[len(self.rgb)-1] = 0
            self.y = self.posy+self.thickness+self.VMargin
        pygame.draw.rect(frame.window,BLACK,((self.posx,self.posy),(self.thickness+self.HMargin+self.barLength,self.VMargin*4+self.thickness*2)),self.thickness)

class MenuEntry:

    def __init__(self, menu, text, color, fontSize):
        self.font = pygame.font.Font("freesansbold.ttf",size=fontSize)
        self.text = text
        self.color = color
        self.antialiased = True
        self.textImg = None
        self.menu = menu
        self.__renderText()

    def __renderText(self):
        self.textImg = self.font.render(self.text,self.antialiased,self.color)
    
    def setColor(self, color):
        self.color = color
        self.__renderText()

    def setSize(self, fontSize):
        self.font = pygame.font.Font("freesansbold.ttf",size=fontSize)
        self.menu.update(self.font.get_height())
        self.__renderText()

class UIMenu:

    def __init__(self, posx, posy, thickness, HMargin, VMargin):
        self.thickness = thickness
        self.VSize = self.thickness
        self.HMargin = HMargin
        self.VMargin = VMargin
        self.HOffset = 0
        self.posx, self.posy = posx, posy
        self.onHoverf = None
        self.notOnHoverf = None
        self.onClickf = None
        self.notOnClickf = None
        self.entries = list()
 
    def addEntry(self,text,color,fontSize):
        entry = MenuEntry(self, text, color, fontSize)
        self.update(entry.font.get_height())
        self.entries.append(entry)
        return entry

    def update(self, fontHeight):
        change = True
        for entry in self.entries:
            if fontHeight < entry.font.get_height():
                change = False
                break
        if change: self.VSize = fontHeight+(self.VMargin+self.thickness)*2
    
    def onClick(self, function):
        self.onClickf = function

    def notOnClick(self, function):
        self.notOnClickf = function
    
    def onHover(self, function):
        self.onHoverf = function

    def notOnHover(self, function):
        self.notOnHoverf = function
    
    def mouseOnEntry(self, entry, mx, my, hoffset):
        entryx, entryy = entry.textImg.get_offset()
        entryw, entryh = entry.textImg.get_size()
        if entryx+hoffset <= mx <= entryx+hoffset + entryw:
           if entryy <= my <= entryy + entryh:
               return True
        return False

    def handleEvents(self,event):
        mousex, mousey = pygame.mouse.get_pos()
        clicked = False
        self.HOffset = self.HMargin+self.thickness
        
        for entry in self.entries:
            onhover = self.mouseOnEntry(entry, mousex, mousey, self.HOffset)
            if self.onHoverf != None and onhover:
                self.onHoverf(entry)
            if self.notOnHoverf != None and not onhover:
                self.notOnHoverf(entry)
            if self.onClickf != None and onhover:
                if event.type == pygame.MOUSEBUTTONDOWN: 
                    if not clicked: self.onClickf(entry)
                    clicked = True
                if event.type == pygame.MOUSEBUTTONUP: clicked = False
            if self.notOnClickf != None and onhover:
                if event.type == pygame.MOUSEBUTTONDOWN: 
                    clicked = True
                if event.type == pygame.MOUSEBUTTONUP: 
                    if clicked: self.notOnClickf(entry)
                    clicked = False
           
            self.HOffset += self.HMargin*2+self.thickness+entry.textImg.get_width()
        self.HOffset = 0

    def show(self, frame):
        for entry in self.entries:
            frame.window.blit(entry.textImg,(self.HOffset+self.HMargin+self.thickness,self.VMargin+self.thickness))
            self.HOffset += self.HMargin*2+self.thickness+entry.textImg.get_width()
        self.HOffset = 0
        pygame.draw.rect(frame.window,BLACK,((self.posx,self.posy),(frame.width,self.VSize)),self.thickness)
    
class MainApp:

    def __init__(self, size:tuple):
        pygame.init()
        self.width, self.height = size
        self.window = pygame.display.set_mode(size, pygame.RESIZABLE)
        pygame.display.set_caption("BlueAnimation")
        self.components = list()

    def add(self, component):
        self.components.append(component)

    def mainloop(self):
        while True:
            self.window.fill((248,248,248))
            self.width, self.height = self.window.get_size()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                for component in self.components:
                    component.handleEvents(event)
            
            for component in self.components:
                component.show(self)
            pygame.display.update()

def change_size(entry):
    entry.setSize(40)
    if entry.text == ">" or entry.text == "<":
        entry.setColor(RED)
    else:
        entry.setColor(BLUE)

def reset_size(entry):
    entry.setSize(30)
    entry.setColor(BLACK)

def entryClicked(entry):
    if entry.text == "Exit":
        pygame.quit()
        sys.exit(0)
    elif entry.text == "SelectColor":
        thread = threading.Thread(target=colorchooser.askcolor)
        thread.start()
    elif entry.text == ">":
        canvas.addFrame()
        canvas.frame += 1
        frame_entry.text = "Frame:"+str(canvas.frame+1)
    elif entry.text == "<":
        if canvas.frame > 0:
            canvas.frame -= 1
            frame_entry.text = "Frame:"+str(canvas.frame+1)
    elif entry.text == "Export":
        exporter.export(canvas, app)

#TODO
def hexToRGB(color:str):
    print(color)

app = MainApp((1000,600))
exporter = Exporter()

menu = UIMenu(0,0,8,8,8)
menu.addEntry("Export",BLACK,30)
menu.addEntry("SelectColor",BLACK,30)
menu.addEntry("<",BLACK,30)
menu.addEntry(">",BLACK,30)
about = menu.addEntry("About",BLACK,30)
menu.addEntry("Exit",BLACK,30)
frame_entry = menu.addEntry("Frame:1",BLACK,30)
menu.onHover(change_size)
menu.notOnHover(reset_size)
menu.onClick(entryClicked)

canvas = Canvas(0,70)

app.add(menu)
app.add(canvas)
app.mainloop()


