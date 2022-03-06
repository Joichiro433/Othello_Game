from typing import List, Optional, Tuple
import sys
import time
import random
import tkinter as tk
from tkinter import messagebox

import numpy as np
from nptyping import NDArray

SIZE = 8


class OthelloBoard:
    def __init__(self) -> None:
        self.field : NDArray[(SIZE+2, SIZE+2), int] = self._make_field(filed_size=SIZE)
        self.turn_attack : int = 1
        self.turn_target : int = 2

    def count(self) -> Tuple[int, int, int]:
        """石の総数をカウントする"""
        white : int = np.sum(self.field == 1)
        black : int = np.sum(self.field == 2)
        last : int = np.sum(self.field == 0)
        return white, black, last

    def check_stone(self, x: int, y: int) -> List[Tuple[int, int]]:
        """反転できる石を返却する"""
        stone_check_list : List[Tuple[int, int]] = []  # 反転させる石を格納
        if self.field[x, y] == 0:  # 石が存在しない場合
            # 上下左右斜めの8方向を確認
            for i in range(3):
                for j in range(3):
                    if i == 1 and j == 1:
                        continue
                    check_x, check_y = x, y
                    direction = (i-1, j-1)
                    check_x += direction[0]
                    check_y += direction[1]
                    # 裏返し可能かの判断をする
                    if self.field[check_x, check_y] == self.turn_target:  # 相手の石の場合
                        while True:
                            # 同じ方向に進む
                            check_x += direction[0]
                            check_y += direction[1]
                            if self.field[check_x, check_y] == self.turn_target:
                                continue
                            elif self.field[check_x, check_y] == 9:
                                break
                            elif self.field[check_x, check_y] == 0:
                                break
                            else:
                                stone_check_list.append(direction)

        return stone_check_list

    def attack_check(self) -> List[Tuple[int, int]]:
        """裏返すことができる座標を返却"""
        attack_list = []
        for i in range(9):
            for j in range(9):
                if self.check_stone(x=i, y=j):
                    attack_list.append((i, j))
        return attack_list
    
    def put_stone(self, x: int, y: int) -> None:
        """石を置いて裏返す"""
        attack_list = self.attack_check()
        if (x, y) in attack_list:
            direction : List[Tuple[int, int]] = self.check_stone(x, y)
            self.field[x, y] = self.turn_attack  # 石の裏返し
            for d in direction:
                ax, ay = x, y
                while True:
                    ax += d[0]
                    ay += d[1]

                    assert self.field[ax, ay] != 9, 'choice error!'
                    assert self.field[ax, ay] != 0, 'choice error!'

                    if self.field[ax, ay] == self.turn_target:
                        self.field[ax, ay] = self.turn_attack   # 石の裏返し
                        continue
                    else:
                        break

    def _make_field(self, filed_size: int) -> NDArray:
        """盤面を作成する"""
        field : NDArray[(filed_size, filed_size), int] = np.zeros((filed_size, filed_size))
        field = np.pad(field, [1, 1], 'constant', constant_values=(9))
        field[4, 5] = 1
        field[5, 4] = 1
        field[4, 4] = 2
        field[5, 5] = 2
        return field
    

def field_update():
    global btns
    btns = []
    for x in range(8):
        for y in range(8):
            btn_place = str(x) + str(y)
            if board.field[y+1][x+1] == 1:
                btns.append(
                    tk.Button(
                        root, 
                        text='●', 
                        font=('MSゴシック', '30'), 
                        fg='#001100', 
                        anchor='center', 
                        name=btn_place))
            elif board.field[y+1][x+1] == 2:
                btns.append(
                    tk.Button(
                        root, 
                        text='●', 
                        font=('MSゴシック', '30'), 
                        fg='#ffffff', 
                        anchor='center', 
                        name=btn_place))
            else:
                btns.append(
                    tk.Button(
                        root,
                        text='',
                        name=btn_place))

            btns[x*8+y].place(x=x*50+25, y=y*50+100, width=50, height=50)
            btns[x*8+y].configure(bg='#225522')


def judgement(player, ai):
    print(player)
    print(ai)
    field_update()
    if player > ai:
        messagebox.showinfo('AI', 'あなたの勝ちです!!!')
    elif player < ai:
        messagebox.showinfo('AI', 'あなたの負けです......')
    else:
        messagebox.showinfo('AI', '引き分けです')
    root.destroy()
    sys.exit()


def click_btn(btn):
    global board
    select_x, select_y = map(int, list(btn.widget._name))
    user_put = (select_y+1, select_x+1)  # Playerが選んだ座標
    choices = board.attack_check()  # 裏返し可能な座標のリスト
    if user_put in choices:
        board.put_stone(user_put[0], user_put[1])
        field_update()
    else:
        return
    player, ai, last = board.count()
    label_txt = f'YOU: {player} / AI: {ai} / LAST: {last}'
    info_label = tk.Label(root, text=label_txt, font=('MSゴシック', '15', 'bold'))
    info_label.place(x=25, y=35, width=400, height=50)

    if not ai or not last:
        judgement(player, ai)

    board.turn_attack, board.turn_target = board.turn_target, board.turn_attack

    end_flag = False

    while board.turn_attack == 2:
        choices = board.attack_check()
        if choices:
            ai_put = random.choice(choices)
            board.put_stone(ai_put[0], ai_put[1])
            field_update()
        else:
            if end_flag:
                judgement(player, ai)
            end_flag = True
            messagebox.showinfo('AI', 'AIの置ける場所がありません')
            field_update()

        player, ai, last = board.count()
        label_txt = f'YOU: {player} / AI: {ai} / LAST: {last}'
        info_label = tk.Label(root, text=label_txt, font=('MSゴシック', '15', 'bold'))
        info_label.place(x=25, y=35, width=400, height=50)

        if not player or not last:
            judgement(player, ai)
        
        board.turn_attack, board.turn_target = board.turn_target, board.turn_attack

        choices = board.attack_check()
        if not choices:
            if end_flag:
                judgement(player, ai)
            messagebox.showinfo('AI', 'Playerの置ける場所がありません')
            board.turn_attack, board.turn_target = board.turn_target, board.turn_attack


if __name__ == '__main__':
    board : OthelloBoard = OthelloBoard()
    player, ai, last = board.count()

    root : tk.Tk = tk.Tk()
    root.configure(bg='#fcfcfc')
    root.title('Ohello Game')
    root.geometry('450x550')

    field_update()

    label_txt = f'YOU: {player} / AI: {ai} / LAST: {last}'
    info_label = tk.Label(root, text=label_txt, font=('MSゴシック', '15', 'bold'))
    info_label.place(x=25, y=35, width=400, height=50)

    root.bind('<1>', click_btn)
    root.mainloop()