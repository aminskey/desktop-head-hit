import tkinter as tk
import time
import pygetwindow as gw

from PIL import Image
from vector import Vector
from pyautogui import size

FPS = 20

class Base:
    def __init__(self, file, frames):
        self.window = tk.Toplevel()
        self.running = False

        self.anim = [tk.PhotoImage(file=file, format="gif -index %i" % (i)) for i in range(frames)]
        self.index = 0
        self.dir = 1
        self.maxFrames = 10
        self.img = self.anim[self.index]

        self.timestamp = time.time()
        self.window.overrideredirect(True)
        self.window.attributes('-topmost', True)
        self.window.wm_attributes('-transparentcolor', 'black')

        self.label = tk.Label(self.window, bd=0, bg='black')

        self.acc = Vector(0, 0)
        self.vel = Vector(FPS//6, 0)
        self.pos = Vector(0, 0)
        self.res = size() # Get display size

        self.spawnTime = time.time()
        self.maxTime = 20
        self.speedCap = 5

        self.window.geometry(f"{self.img.width()}x{self.img.height()}+{self.pos.x}+{self.pos.y}")
        self.label.configure(image=self.img)

        self.label.pack()

    def run(self):
        self.running = True
        self.window.after(0, self.update)
        self.window.mainloop()

    def update(self):
        self.vel += self.acc
        self.pos += self.vel

        if time.time() > self.timestamp + 1/FPS:
            self.index += 1 * self.dir
            self.img = self.anim[self.index%self.maxFrames]
            self.timestamp = time.time()

        if self.vel.length > self.speedCap:
            self.vel.limit(self.speedCap)

        self.window.geometry(f"{self.img.width()}x{self.img.height()}+{int(self.pos.x)}+{int(self.pos.y)}")
        self.label.configure(image=self.img)

        self.label.pack()
        self.window.after(10, self.update)


class Ball(Base):
    units = 0
    def __init__(self):
        super().__init__("ball.gif", 10)
        self.acc.y = 0.2

    def update(self):
        if self.pos.x > self.res[0] - self.img.width() or self.pos.x < 0:
            self.vel.x *= -1
            self.dir *= -1

        for win in gw.getWindowsWithTitle(""):
            if win.isMinimized or win.left < 0 or win.top < 0:
                continue
            if win.left < self.pos.x < win.left + win.width - self.img.width()//2 and win.top + self.img.width() > self.pos.y + self.img.height() > win.top:
                print(win.title)
                self.pos.y = win.top - self.img.height()
                if abs(self.vel.y) > 0:
                    self.vel.y *= -0.5

            """
            if win.left < self.pos.x + self.img.width() < win.left - self.img.width()//2 and self.pos.y > win.top:
                self.vel.x *= -1
                self.dir *= -1
                break
            """


        super().update()

class Bomb(Base):
    def __init__(self):
        super().__init__("bomb.gif", 26)
        self.acc.y = 0.2
        self.vel.x = 1

        self.walk = self.anim[:14]
        self.blowUp = self.anim[14:]

        frames = Image.open("explosion.gif").n_frames
        self.fire = [tk.PhotoImage(file="explosion.gif", format="gif -index %i" % (i)) for i in range(frames)]

        self.maxTime = 5

        print(len(self.walk), len(self.blowUp))

        self.pos = Vector(size()[0]//2, size()[1]*3//4)
        self.anim = self.walk

    def update(self):

        global FPS

        if self.pos.x > self.res[0] - self.img.width() or self.pos.x < 0:
            self.vel.x *= -1
            self.dir *= -1

        for win in gw.getWindowsWithTitle(""):
            if win.isMinimized or win.left < 0 or win.top < 0:
                continue
            if win.left < self.pos.x < win.left + win.width - self.img.width()//2 and win.top + self.img.width() > self.pos.y + self.img.height() > win.top:
                print(win.title)
                self.pos.y = win.top - self.img.height()
                if abs(self.vel.y) > 0:
                    self.vel.y *= -0.5

        if self.anim == self.walk:
            if time.time() > self.spawnTime + self.maxTime:
                self.anim = self.blowUp
                self.maxFrames = len(self.blowUp) - 1
                self.vel = Vector(0, 0)
                self.index = 0

        if self.index > len(self.anim) - 1 and self.anim == self.blowUp:
            self.index = 0
            self.anim = self.fire
            self.maxFrames = len(self.fire) - 1
            FPS = 60

        if self.index > len(self.anim) - 1 and self.anim == self.fire:
            self.window.destroy()
            quit()

        super().update()