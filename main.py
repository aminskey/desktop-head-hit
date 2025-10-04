import tkinter as tk
import pygetwindow as gw
import threading

from vector import Vector
from pyautogui import size
from PIL import Image, ImageTk
from random import randint
from math import sin

FPS = 20

s1 = s2 = 0
players = []

class Player:
    def __init__(self, root, s=(64, 64), controls=["<Left>", "<Right>", "<space>"], color="#11ff11"):
        self.res = size() # Get display size

        global players
        players.append(self)

        self.num = players.index(self)
        self.title = "Player {}".format(self.num)

        self.pos = Vector((1+self.num)//(self.res[0]+2), 10)
        self.vel = Vector(1, 0)
        self.acc = Vector(0, 0.2)

        self.size = s
        self.score = 0


        self.window = tk.Toplevel(root)
        self.window.title(self.title)
        self.window.geometry(f"{self.size[0]}x{self.size[1]}+{int(self.pos.x)}+{int(self.pos.y)}")
        self.window.overrideredirect(True)
        self.window.attributes('-topmost', True)
        self.window.configure(background=color)

        self.controls = controls
        lb = tk.Label(self.window, text=f"{self.num + 1}", background=color, font=("Consolas", 25))
        lb.pack()
        self.window.after(10, self.update)

    def horiz(self, x, *args):
        self.vel.x = x

    def jump(self, y, *args):
        self.vel.y = y

    def update(self):
        self.vel += self.acc
        self.pos += self.vel

        if self.pos.x > self.res[0] - self.size[0] or self.pos.x < 0:
            self.vel.x *= -1
            self.pos += self.vel*1.2

        for win in gw.getWindowsWithTitle(""):
            if win.isMinimized or win.left < 0 or win.top < 0 or win.title == self.title:
                continue
            if win.left < self.pos.x < win.left + win.width - self.size[0]//2:

                # Lands on top of a window
                if win.top + 50 > self.pos.y + self.size[1] > win.top:
                    if "Player" in win.title:
                        for player in players:
                            if player.title == win.title:
                                self.score += 1
                                player.pos = Vector(self.res[0]//2, self.res[1]//2)
                                player.window.geometry(
                                    f"{player.size[0]}x{player.size[1]}+{int(player.pos.x)}+{int(player.pos.y)}")
                                break

                    # apply friction
                    self.vel.x *= 0.88

                    # position player
                    self.pos.y = win.top - self.size[1]

                    # decrease bounce
                    if abs(self.vel.y) > 0:
                        self.vel.y *= -0.5

        if self.pos.y < 0 or self.pos.y > self.res[1]:
            self.pos.y = self.res[1]//2


        if self.num == 0:
            global s1
            s1 = self.score
        elif self.num == 1:
            global s2
            s2 = self.score

        self.vel.limit(7)

        self.window.geometry(f"{self.size[0]}x{self.size[1]}+{int(self.pos.x)}+{int(self.pos.y)}")
        self.window.after(10, self.update)

    def run(self):
        self.running = True
        self.window.after(0, self.update)
        self.window.mainloop()

class ScoreLabel:
    def __init__(self, root):
        self.screen_size = size()

        self.window = tk.Toplevel(root)
        #self.window.configure(background="blue")
        self.window.overrideredirect(True)
        self.window.attributes('-topmost', True)
        #self.window.wm_attributes('-transparentcolor', 'black')
        self.window.after(10, self.update)

        self.label = tk.Label(self.window, padx=20, pady=15, fg="white", relief="sunken", bd=10, width=70)
        self.label.pack()
    def update(self):

        self.label.configure(text=f"P1 # {s1} : {s2} # P2", fg="green", bg="black", font=("Consolas", 16), padx=10)

        x = (self.screen_size[0] - self.window.winfo_width())//2
        y = (self.screen_size[1] - self.window.winfo_height())//2
        self.window.geometry(f"{self.window.winfo_width()}x{self.window.winfo_height()}+{x}+{y}")
        self.window.after(1, self.update)

def genPlayer(root, color, inp):

    p = Player(root, color=color, controls=inp)

    root.bind(p.controls[0], lambda *args: p.horiz(-4, *args))
    root.bind(p.controls[1], lambda *args: p.horiz(4, *args))
    root.bind(p.controls[2], lambda *args: p.jump(20, *args))

    print(p.num)

    p.run()

def genLevel(root):
    dir = -1
    startPoint = [size()[0]//2, size()[1] - 55*2]

    for i in range(10):

        if startPoint[1] < size()[1]//4 and dir < 0:
            dir = 1
            startPoint[0] = size()[0]//4

        if startPoint[1] > size()[1] * 7//8 and dir > 0:
            dir = -1
            startPoint[0] = size()[0]* 3//4


        startPoint[1] += i * 120 * dir
        startPoint[0] += 30 * sin(startPoint[1]*2)+randint(-200, 200)

        tmp = tk.Toplevel(root)
        tmp.geometry(f"200x56+{int(startPoint[0])}+{int(startPoint[1])}")
        #tmp.configure(background="white")
        tmp.overrideredirect(True)
        tmp.attributes('-topmost', True)
        tmp.wm_attributes('-transparentcolor', 'white')

        print(i, startPoint)

        buff = Image.open("grass.png")
        img = ImageTk.PhotoImage(buff)
        lb = tk.Label(tmp, image=img, width=200, height=56)
        lb.pack()

        lb.image = img


def play(root):
    t1 = threading.Thread(target=genPlayer, args=(root, "#11ff11", ["<Left>", "<Right>", "<Up>"]))
    t2 = threading.Thread(target=genPlayer, args=(root, "#ff1111", ["<a>", "<d>", "<w>"]))

    t1.start()
    t2.start()

    ScoreLabel(root)




if __name__ == '__main__':

    root = tk.Tk()
    root.attributes('-topmost', True)
    root.configure(background="black")
    root.geometry("300x200")

    genLevel(root)
    play(root)

    root.mainloop()


