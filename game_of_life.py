import tkinter as tk
from tkinter import messagebox as mb
from time import sleep


class GameOfLife(tk.Tk):
    def __init__(self):
        super().__init__()
        self.board_btn = tk.Button(self, text="Start", command=self.start)
        self.size_btn = tk.Button(self, text="Change size", command=self.size)
        self.quit_btn = tk.Button(self, text="Quit", command=self.exit)
        self.clear_btn = tk.Button(self, text="Clear", command=self.clear)
        self.x_entry = tk.Entry(self, width=5)
        self.x_entry.insert(0, '20')
        self.y_entry = tk.Entry(self, width=5)
        self.y_entry.insert(0, '15')
        self.x_label = tk.Label(self, text='X:')
        self.y_label = tk.Label(self, text='Y:')
        self.board_btn.grid(row=2, column=0, columnspan=2, padx=5, pady=2)
        self.size_btn.grid(row=2, column=2, columnspan=2, padx=3, pady=1)
        self.quit_btn.grid(row=1, column=3, sticky='E', padx=3, pady=1)
        self.clear_btn.grid(row=0, column=3, sticky='E', padx=3, pady=1)
        self.x_entry.grid(row=0, column=1)
        self.y_entry.grid(row=1, column=1)
        self.x_label.grid(row=0, column=0, sticky='E')
        self.y_label.grid(row=1, column=0, sticky='E')
        self.resizable(0, 0)
        self.cell_size = 15
        self.board = None
        self.field_id = []
        self.canvas = None
        self.start_flag = False
        self.field_window = None
        self.time = 0.5
        self.clear()
        self.size()

    def board_window(self, x, y):
        """ Create the board window """
        self.field_window = tk.Toplevel(self)
        self.canvas = tk.Canvas(self.field_window, width=x * self.cell_size, height=y * self.cell_size)
        self.field_window.title('Game of life')
        self.field_id = []
        for y, row in enumerate(self.board):
            for x, pos in enumerate(row):
                self.field_id.append(self.canvas.create_rectangle(
                    self.cell_size * x,
                    self.cell_size * y,
                    self.cell_size + (self.cell_size * x),
                    self.cell_size + (self.cell_size * y),
                    fill=self.color(y, x)
                ))
        self.canvas.bind("<Button-1>", self.click)
        self.canvas.pack()
        self.field_window.resizable(0, 0)

    def clear(self):
        """ clear the board """
        self.board = [[False for _ in range(int(self.x_entry.get()))] for _ in range(int(self.y_entry.get()))]
        self.size()

    def size(self):
        """ resize the board """
        if self.start_flag:
            return
        if self.field_window:
            self.field_window.destroy()
        old = len(self.board[0]), len(self.board)
        new = [self.x_entry.get(), self.y_entry.get()]
        max_dim = [(10, 100), (6, 60)]
        for i, dim in enumerate(new):
            try:
                new[i] = max(max_dim[i][0], (min(max_dim[i][1], int(dim))))
            except ValueError:
                new[i] = old[i]
        new_x, new_y = new
        old_x, old_y = old
        self.x_entry.delete(0, 'end')
        self.y_entry.delete(0, 'end')
        self.x_entry.insert(0, str(new_x))
        self.y_entry.insert(0, str(new_y))
        if new_y > old_y:
            self.board = [old_x * [False]] * ((new_y - old_y) // 2) + self.board + \
                         [[False] * old_x] * (new_y - old_y - (new_y - old_y) // 2)
        else:
            self.board = self.board[(old_y - new_y) // 2:(old_y - new_y) // 2 + new_y]

        self.board = [
            [False] * ((new_x - old_x) // 2)
            + self.board[i][max((old_x - new_x), 0) // 2:(old_x - new_x) // 2 + new_x]
            + [False] * (new_x - old_x - (new_x - old_x) // 2)
            for i in range(new_y)
        ]
        self.board_window(new_x, new_y)

    def click(self, event):
        if self.start_flag:
            return
        y, x = event.y, event.x
        by, bx = y // self.cell_size, x // self.cell_size
        items = self.canvas.find_closest(x, y)
        if items:
            rect_id = items[0]
            self.board[by][bx] = not self.board[by][bx]
            self.canvas.itemconfigure(rect_id, fill=self.color(by, bx))

    def color(self, y, x):
        fill = {True: 'brown', False: 'white'}
        color = fill[self.board[y][x]]
        return color

    def exit(self):
        """ exit the game """
        answer = mb.askquestion('Exit Life Counter', 'Do you really want to quit?')
        if answer == 'yes':
            self.start_flag = False
            self.quit()

    def start(self):
        if not self.start_flag:
            self.board_btn["text"] = "Stop"
            self.start_flag = True
            self.clear_btn.configure(state='disabled')
            while self.start_flag:
                self.board_update()
                sleep(self.time)
                self.canvas.update()
        else:
            self.board_btn["text"] = "Start"
            self.start_flag = False
            self.clear_btn.configure(state='normal')

    def board_update(self):
        self.life_counter()
        for y, row in enumerate(self.board):
            for x, field in enumerate(row):
                rect_id = y * len(row) + x + 1
                self.canvas.itemconfigure(rect_id, fill=self.color(y, x))

    def life_counter(self):
        """ update board to next turn """
        rows, columns = len(self.board), len(self.board[0])
        n = lambda y, x: {((y + i) % rows, (x + j) % columns) for i in (-1, 0, 1) for j in (-1, 0, 1) if
                          not i == j == 0}

        life = {(y, x) for y in range(rows) for x in range(columns) if self.board[y][x]}
        life_next, possible = set(), set()

        for y, x in life:
            if sum([self.board[i][j] for i, j in n(y, x)]) in (2, 3):
                life_next |= {(y, x)}
            possible |= n(y, x)
        possible -= life

        for y, x in possible:
            if sum([self.board[i][j] for i, j in n(y, x)]) == 3:
                life_next |= {(y, x)}
        self.board = [[True if (y, x) in life_next else False for x in range(columns)] for y in range(rows)]


if __name__ == '__main__':
    app = GameOfLife()
    app.title("Start")
    app.mainloop()
