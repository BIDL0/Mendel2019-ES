#!/usr/bin/env python
#
# ******************************************************************************
# ******            BiCAS - Bidlo's Cellular Automata Simulator          *******
# ******************************************************************************
# This program requires the Python environment with NumPy and PyGame libraries.
#
# --------------------------------- Licence ------------------------------------
# BiCAS is provides under "The BSD 3-Clause License" the content of which is
# distributed within the LICENSE file that is a part of this project.
# ------------------------------------------------------------------------------
#
# Author:                           Michal Bidlo
#                          Brno University of Technology
#                        Faculty of Information Technology
#                       IT4Innovations Centre of Excellence
#                    Bozetechova 2, Brno 61266, Czech Republic
#                   E-mail: see http://www.fit.vutbr.cz/~bidlom
#
# ******************************************************************************
import os, sys, glob, pygame
from random import randint
import numpy as np
pygame.init()

# default CA size (_SIZE x _SIZE) - can be modified
_SIZE = 16
# window size in pixels (_WIN x _WIN) - can be modified
_WIN = 800

# color constants for cell states => maximum 16 states
# or add more colors to the list below
white = pygame.Color(0xFFFFFF00)
black = pygame.Color(0x00000000)
red = pygame.Color(0xFF000000)
green = pygame.Color(0x00FF0000)
blue = pygame.Color(0x0000FF00)
cyan = pygame.Color(0x00FFFF00)
magenta = pygame.Color(0xFF00FF00)
yellow = pygame.Color(0xFFFF0000)
gray = pygame.Color(0x64646400)
pink = pygame.Color(0xFF087F00)
brown = pygame.Color(0x825A2C00)
orange = pygame.Color(0xFA680000)
violet = pygame.Color(0xAA00FF00)
dred = pygame.Color(0x80000000)
dgreen = pygame.Color(0x00800000)
dblue = pygame.Color(0x00008000)

color = [ black, blue, white, red, yellow, green, brown, orange, cyan, violet,
          gray, magenta, pink, dred, dgreen, dblue ]

class CA:
    def __init__(self, rows=20, cols=20, states=2, nsize=5):
        self.shelp = 1
        self.age = 0
        self.cell = np.empty((rows+2, cols+2), object)
        self.temp = np.empty((rows+2, cols+2), object)
        self.istt = np.empty((rows+2, cols+2), object)
        for row in range(rows + 2):
            for col in range(cols + 2):
                self.cell[row][col] = "00"
                self.temp[row][col] = "00"
                self.istt[row][col] = "00"
        self.ltf_dict = {}
        self.ltf_list = []
        self.ltf_index = 0
        self.ltf_limit = 0
        self.rows = rows
        self.cols = cols
        self.states = states
        self.nsize = nsize
        self.cell_w = pygame.display.Info().current_w / self.cols
        self.cell_h = pygame.display.Info().current_h / self.rows
        self.hy = 0

    def set_cell(self, row, col, state):
        temp = int(state)
        self.cell[row][col] = "%02d" % temp

    def get_cell(self, row, col):
        return int(self.cell[row][col])

    def set_clicked_cell(self, (pos_x, pos_y)):
        row = pos_y / self.cell_h + 1
        col = pos_x / self.cell_w + 1
        temp = (self.get_cell(row, col) + 1) % self.states
        self.set_cell(row, col, temp)

    def zero_init(self):
        self.age = 0
        for row in range(1, self.rows+1):
            for col in range(1, self.cols+1):
                self.set_cell(row, col, 0)

    def istt_init(self):
        self.age = 0
        for row in range(1, self.rows+1):
            for col in range(1, self.cols+1):
                self.set_cell(row, col, self.istt[row][col])

    def draw_text(self, win, label):
        global _WIN

        font = pygame.font.SysFont("monospace", 24)
        font.set_bold(1)
        text = font.render(label, 1, (255, 255, 0))
        if self.hy == 0:
            win.blit(text, (20, 10))
            self.hy = self.hy + 40
        else:
            win.blit(text, (20, self.hy))
            self.hy = self.hy + 20

    def show_help(self, win):
        self.hy = 0
        self.draw_text(win, "Interactive BiCAS Control")
        self.draw_text(win, "The window title shows the name of the")
        self.draw_text(win, ".tab transition function file (if any)")
        self.draw_text(win, "If there are more .tab files in current")
        self.draw_text(win, "  directory, the arrow keys up and down")
        self.draw_text(win, "  may be used to switch between them")
        self.draw_text(win, "SPACE: run/pause CA development")
        self.draw_text(win, "t: perform a single CA step")
        self.draw_text(win, "i: return to the initial CA state")
        self.draw_text(win, "c: capture current CA state to .png")
        self.draw_text(win, "click: increment a cell state")
        self.draw_text(win, "ESC: exit BiCAS")
        self.draw_text(win, "h: show this help")
        pygame.display.update()

    def draw(self, win):
        for row in range(1, self.rows+1):
            for col in range(1, self.cols+1):
                pygame.draw.rect(win, color[self.get_cell(row, col)],
                                ((col-1)*self.cell_w, (row-1)*self.cell_h,
                                self.cell_w, self.cell_h), 0)
                pygame.draw.rect(win, dblue,
                                ((col-1)*self.cell_w, (row-1)*self.cell_h,
                                self.cell_w, self.cell_h), 1)
        pygame.display.update()
        if self.shelp == 1:
            self.show_help(win)

    def develop(self, win):
        for row in range(1, self.rows+1):
            for col in range(1, self.cols+1):
                self.LTF_next(row, col)
        for row in range(1, self.rows+1):
            for col in range(1, self.cols+1):
                self.set_cell(row, col, self.temp[row][col])
        self.draw(win)
        self.age = self.age + 1

    def LTF_next(self, row, col):
        if self.nsize == 5:
            north=self.cell[row-1][col] if row>1 else self.cell[self.rows][col]
            west =self.cell[row][col-1] if col>1 else self.cell[row][self.cols]
            cent =self.cell[row][col]
            east =self.cell[row][col+1] if col<self.cols else self.cell[row][1]
            south=self.cell[row+1][col] if row<self.rows else self.cell[1][col]
            key =  ''.join([ north, west, cent, east, south ])
            self.temp[row][col] = self.ltf_dict.get(key, self.cell[row][col])

        elif self.nsize == 9:
            row_cm = row - 1 if row > 1 else self.rows
            row_cp = row + 1 if row < self.rows else 1
            col_cm = col - 1 if col > 1 else self.cols
            col_cp = col + 1 if col < self.cols else 1
            key =  ''.join([ self.cell[row_cm][col_cm], self.cell[row_cm][col],
                             self.cell[row_cm][col_cp], self.cell[row][col_cm],
                             self.cell[row][col]    , self.cell[row][col_cp],
                             self.cell[row_cp][col_cm], self.cell[row_cp][col],
                             self.cell[row_cp][col_cp] ])
            self.temp[row][col] = self.ltf_dict.get(key, self.cell[row][col])

        else:
            print "Unsupported neighbourhood:", self.nsize
            exit(1)

    def read_state(self, sfile):
        istate = []
        for line in sfile.readlines():
            istate.append(line.strip().split(' '))
        sfile.close()
        roff = (self.rows - len(istate)) / 2
        coff = (self.cols - len(istate[0])) / 2
        for r in range(0, len(istate)):
            for s in range(0, len(istate[0])):
                self.istt[r+roff+1][s+coff+1] = istate[r][s]
        self.istt_init()

    def state_file_default(self):
        try:
            caf = open("default.cas", "r")
        except IOError:
            print "CA state file not specified, the default cell state is 0."
            return
        with caf:
            self.read_state(caf)

    def state_file_custom(self, file_name):
        try:
            caf = open(file_name, "r")
        except IOError:
            print "Unable to open the CA state file:", file_name
            self.state_file_default()
            return
        with caf:
            self.read_state(caf)

    def read_ca(self, file_name):
        row = 0
        rules = 0
        try:
            caf = open(file_name, "r")
        except IOError:
            print "Unable to open the transition function file:", file_name
            exit(1)
        with caf:
            for line in caf:
                line = line.strip().split(' ')
                if row == 0:    # nactena hlavicka: [2] pocet_stavu
                    if len(line) == 2:
                        if int(line[0]) != 2:
                            print "Head error: unsupported dimension %d (must be 2)"%int(line[0])
                            exit(1)
                        self.states = int(line[1])
                    elif len(line) == 1:
                        self.states = int(line[0])
                        if self.states > len(color):
                            print "Too many CA states: %d (the maximum is %d)" % \
                                (self.states, len(color))
                            exit(1)
                    else:
                        print "Head error: the 1st line of .tab must be the number of states"
                        exit(1)
                elif line[0] != "#": # reading the transition rules (rows)
                    # if they are not commented out by #
                    right = "%02d" % int(line.pop()) # the last int = next state
                    left = ''
                    self.nsize = len(line)
                    if self.nsize != 5 and self.nsize != 9:
                        print "Unsupported neighbourhood:", self.nsize
                        exit(1)
                    for i in range(self.nsize):
                        left = left + "%02d" % int(line[i])
                    self.ltf_dict[left] = right
                    rules = rules + 1
                row = row + 1
            caf.close()
        print "The number of states:", self.states
        print "Cellular neighbourhood:", self.nsize
        print "Transition rules read:", rules
        pygame.display.set_caption(file_name)

    def read_tab_files(self):
        self.ltf_list = glob.glob("*.tab")
        if not self.ltf_list:
            return # if no .tab file exists, then create "empty" CA

        self.ltf_list.sort()
        self.ltf_limit = len(self.ltf_list)
        if "default.tab" in self.ltf_list:
            # if default.tab fie exist, set it as the default transition f.
            # (i.e. find its index in the list of possible other .tab files)
            self.ltf_index = self.ltf_list.index("default.tab")
        # ...and read the transition rules from this file
        self.read_ca(self.ltf_list[self.ltf_index])

    def ltf_change_next(self):
        self.ltf_dict.clear()
        if self.ltf_index < self.ltf_limit-1:
            self.ltf_index = self.ltf_index + 1
        else:
            sys.exit(0) # exit after reaching the last transition function
                        # in the list (after pressing arrow down key)
            self.ltf_index = 0
        self.read_ca(self.ltf_list[self.ltf_index])

    def ltf_change_prev(self):
        self.ltf_dict.clear()
        if self.ltf_index > 0:
            self.ltf_index = self.ltf_index - 1
        else:
            self.ltf_index = self.ltf_limit-1
        self.read_ca(self.ltf_list[self.ltf_index])

def main_loop(ca, win):
    devel = 0
    capture = 0
    while True:        # interactive keyboard control
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                ca.shelp = 0
                keyb = event.key
                if keyb == pygame.K_SPACE:
                    devel = 1 - devel       # CA runs or not (devel=1 or 0)
                elif keyb == pygame.K_c:
                    if devel == 0:
                        cap_img = "%03d" % capture
                        capture = capture + 1
                        pygame.image.save(win, cap_img + ".png")
                        # uncomment if you wish to perform a step after capture
#                        ca.develop(win)
                elif keyb == pygame.K_t:
                    if devel == 0:
                        ca.develop(win)
                    print "step %d" % ca.age
                elif keyb == pygame.K_i:
                    ca.istt_init()
                    ca.draw(win)
                    devel = 0
                    capture = 0
                elif keyb == pygame.K_s:
                    ca.zero_init()
                    ca.draw(win)
                    devel = 0
                    capture = 0
                elif keyb == pygame.K_h:
                    if devel == 1:
                        devel = 0
                    ca.shelp = 1
                    ca.draw(win)
                # switching transition functions if multiple .tab files exist
                elif keyb == pygame.K_DOWN or keyb == pygame.K_RIGHT:
                    if ca.ltf_list:
                        ca.istt_init()
                        ca.draw(win)
                        devel = 0
                        capture = 0
                        ca.ltf_change_next()
                elif keyb == pygame.K_UP or keyb == pygame.K_LEFT:
                    if ca.ltf_list:
                        ca.istt_init()
                        ca.draw(win)
                        devel = 0
                        capture = 0
                        ca.ltf_change_prev()
                elif keyb == pygame.K_ESCAPE:
                    sys.exit(0)
            # a click increments (with overflow) the cell state
            elif event.type == pygame.MOUSEBUTTONDOWN:
                ca.shelp = 0
                ca.set_clicked_cell(pygame.mouse.get_pos())
                ca.draw(win)
        if devel == 1:
            ca.develop(win)
            # if you wish to slow down the CA development,
            # uncomment this and specify the delay in ms
#            pygame.time.wait(150)

def run_parser():
    global _SIZE

    ca = None
    size = _SIZE
    state = False
    ltf = False

    i = 1
    runl = len(sys.argv)
    if i < runl:
        if sys.argv[i].isdigit():
            new_size = int(sys.argv[i])
            if new_size > 0:
                print "The CA size specified:", new_size
                size = new_size
            else:
                print "The default CA size is:", size, "x", size
            i = i + 1

    ca = CA(size, size)

    if i < runl:
        if sys.argv[i].endswith("tab"):
            print "Reading a transition function file:", sys.argv[i]
            ca.read_ca(sys.argv[i])
            ltf = True
        elif sys.argv[i].endswith("cas"):
            print "Initial state file specified:", sys.argv[i]
            ca.state_file_custom(sys.argv[i])
            state = True
        else:
            print "WARNING, unknown argument:", sys.argv[i]
        i = i + 1

    if i < runl and not state and sys.argv[i].endswith("cas"):
        print "Initial state file specified:", sys.argv[i]
        ca.state_file_custom(sys.argv[i])
        state = True
        i = i + 1

    if i < runl:
        print "Ignoring remaining arguments:",
        while i < runl:
            print sys.argv[i],
            i = i + 1
        print

    if not state:
        ca.state_file_default()
    if not ltf:
        ca.read_tab_files()

    return ca

def usage():
    print "Usage:"
    print "-----------------------------------------------------------"
    print "BiCAS.py [integer_ca_size] [ltf_file.tab] [istate_file.cas]"
    print "! The arguments are optional but their order is important !"
    print "-----------------------------------------------------------"

def main():
    global _WIN

    usage()
    win = pygame.display.set_mode((_WIN, _WIN))
    pygame.display.set_caption("BiCAS --- Bidlo's Cellular Automata Simulator")
    ca = run_parser()
    ca.draw(win)
    pygame.display.flip()
    main_loop(ca, win)

if __name__ == "__main__":
    main()
