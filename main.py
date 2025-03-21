import tkinter as tk
import time
import pygetwindow as gw
import threading

from vector import Vector
from pyautogui import size
from PIL import Image
from time import sleep

FPS = 20

s1 = s2 = 0
players = []

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
        lb = tk.Label(self.window, text=f"{self.num + 1}", background=color, font=("Consolas", 15))
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
                if win.top + self.size[0] > self.pos.y + self.size[1] > win.top:
                    if "Player" in win.title:
                        print("woo")
                        for player in players:
                            if player.title == win.title:
                                player.score += 1
                                self.pos = Vector(self.res[0]//2, self.res[1]//2)
                                break
                        break

                    # apply friction
                    self.vel.x *= 0.88

                    # position player
                    self.pos.y = win.top - self.size[1]

                    # decrease bounce
                    if abs(self.vel.y) > 0:
                        self.vel.y *= -0.5



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

class ScoreLabel:
    def __init__(self, root):
        self.screen_size = size()

        self.window = tk.Toplevel(root)
        self.window.configure(background="blue")
        self.window.overrideredirect(True)
        self.window.attributes('-topmost', True)
        self.window.wm_attributes('-transparentcolor', 'black')
        self.window.after(10, self.update)

        self.label = tk.Label(self.window, text=f"Player 1 # 500 : 500 # Player 2", padx=20, pady=15, fg="white")
        self.label.pack(padx=10)
    def update(self):

        self.label.configure(text=f"P1 # {s1} : {s2} # P2", fg="white", bg="blue", font=("Courier New", 16), padx=10)

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


if __name__ == '__main__':
    root = tk.Tk()
    root.configure(background='black')
    #root.overrideredirect(True)
    root.attributes('-topmost', True)
    #root.wm_attributes('-transparentcolor', 'black')

    scores = ScoreLabel(root)

    t1 = threading.Thread(target=genPlayer, args=(root, "#11ff11", ["<Left>", "<Right>", "<Up>", "<Down>"]))
    t2 = threading.Thread(target=genPlayer, args=(root, "#ff1111", ["<a>", "<d>", "<w>", "<s>"]))

    t1.start()
    t2.start()

    root.mainloop()