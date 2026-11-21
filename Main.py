#!/usr/bin/env python3
import sys
from collections import namedtuple
from itertools import count

A1, H1, A8, H8 = 91, 98, 21, 28
N, E, S, W = -10, 1, 10, -1
directions = {
    'P': (N, N+N, N+W, N+E),
    'N': (N+N+E, E+N+E, E+S+E, S+S+E, S+S+W, W+S+W, W+N+W, N+N+W),
    'B': (N+E, S+E, S+W, N+W),
    'R': (N, E, S, W),
    'Q': (N, E, S, W, N+E, S+E, S+W, N+W),
    'K': (N, E, S, W, N+E, S+E, S+W, N+W)
}

pst = {
    'P': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,90,90,90,90,90,90,90,90,0,
          0,30,30,40,70,70,40,30,30,0,0,30,30,40,60,60,40,30,30,0,
          0,20,20,30,40,40,30,20,20,0,0,20,20,20,20,20,20,20,20,0,
          0,10,20,20,0,0,20,20,10,0,0,20,30,10,0,0,10,30,20,0,
          0,0,0,0,0,0,0,0,0,0],
    'N': [0]*100, 'B': [0]*100, 'R': [0]*100, 'Q': [0]*100, 'K': [0]*100
}

MATE = 10000
Move = namedtuple('Move', 'i j prom')
Entry = namedtuple('Entry', 'lower upper')

class Position(namedtuple('Position', 'board score wc bc ep kp')):
    def gen_moves(self):
        for i, p in enumerate(self.board):
            if p not in 'PNBRQK':
                continue
            for d in directions[p]:
                for j in count(i + d, d):
                    q = self.board[j]
                    if q.isspace() or q.isupper():
                        break
                    if p == 'P':
                        if d in (N, N+N) and q != '.':
                            break
                        if d == N+N and (i < A1 + N or self.board[i + N] != '.'):
                            break
                        if d in (N+W, N+E) and q == '.' and j != self.ep and abs(j - self.kp) > 1:
                            break
                        if A8 <= j <= H8:
                            for prom in 'NBRQ':
                                yield Move(i, j, prom)
                            break
                    yield Move(i, j, '')
                    if p in 'PNK' or q.islower():
                        break
                    if i in (A1, H1) and self.board[j + (E if i == A1 else W)] == 'K' and self.wc[i == H1]:
                        yield Move(j + (E if i == A1 else W), j + (W if i == A1 else E), '')

    def rotate(self):
        return Position(self.board[::-1].swapcase(), -self.score, self.bc, self.wc,
                        119 - self.ep if self.ep else 0, 119 - self.kp if self.kp else 0)

    def move(self, m):
        i, j, prom = m
        p, q = self.board[i], self.board[j]
        put = lambda b, i, p: b[:i] + p + b[i+1:]
        board = put(put(self.board, j, p), i, '.')
        score = self.score + pst.get(p, [0]*100)[j] - pst.get(p, [0]*100)[i]
        if q != '.':
            score += pst.get(q.upper(), [0]*100)[119 - j]
        if p == 'P':
            if A8 <= j <= H8:
                board = put(board, j, prom)
            if j == self.ep:
                board = put(board, j + S, '.')
        wc = list(self.wc)
        if p == 'K':
            wc = [False, False]
            if abs(j - i) == 2:
                board = put(put(board, (i + j)//2, 'R'), A1 if j < i else H1, '.')
        if i == A1: wc[0] = False
        if i == H1: wc[1] = False
        return Position(board, score, wc, self.bc, j if p == 'P' and abs(j - i) == 20 else 0, j if p == 'K' else 0).rotate()

class Searcher:
    def __init__(self):
        self.tp_score = {}
        self.tp_move = {}
        self.nodes = 0

    def bound(self, pos, gamma, depth):
        self.nodes += 1
        entry = self.tp_score.get((pos, depth), Entry(-MATE, MATE))
        if entry.lower >= gamma:
            return entry.lower
        if entry.upper < gamma:
            return entry.upper

        best = -MATE
        killer = self.tp_move.get(pos)
        moves = []
        if killer:
            moves.append(killer)
        for m in pos.gen_moves():
            if m != killer:
                moves.append(m)

        for m in moves:
            pos1 = pos.move(m)
            if depth > 0:
                score = -self.bound(pos1, 1 - gamma, depth - 1)
            else:
                score = pos1.score
            if score > best:
                best = score
            if best >= gamma:
                self.tp_move[pos] = m
                break

        if best >= gamma:
            self.tp_score[pos, depth] = Entry(best, entry.upper)
        else:
            self.tp_score[pos, depth] = Entry(entry.lower, best)
        return best

    def search(self, hist, max_depth=4):
        self.nodes = 0
        for depth in range(1, max_depth + 1):
            self.bound(hist[-1], 0, depth)
        return self.tp_move.get(hist[-1])

def parse(c):
    return A1 + (ord(c[0]) - 97) + (ord(c[1]) - 49) * 10

def render(i):
    return chr((i % 10) + 96) + str(i // 10 - 1)

def main():
    hist = [Position(
        '         \n' * 2 +
        ' rnbqkbnr\n pppppppp\n ........\n ........\n'
        ' ........\n ........\n PPPPPPPP\n RNBQKBNR\n' +
        '         \n' * 2,
        0, [True, True], [True, True], 0, 0
    )]
    searcher = Searcher()

    while True:
        line = sys.stdin.readline()
        if not line:
            break
        if line.startswith('uci'):
            print('id name TinyChess\nid author make.fun\nuciok')
        elif line.startswith('isready'):
            print('readyok')
        elif line.startswith('ucinewgame'):
            hist = [hist[0]]
        elif line.startswith('position'):
            parts = line.split()
            hist = [hist[0]]
            if 'moves' in parts:
                for mv in parts[parts.index('moves') + 1:]:
                    hist.append(hist[-1].move(Move(parse(mv[:2]), parse(mv[2:4]), mv[4:] if len(mv) > 4 else '')))
        elif line.startswith('go'):
            move = searcher.search(hist)
            if move:
                print(f'bestmove {render(move.i)}{render(move.j)}{move.prom}')
            else:
                print('bestmove 0000')
        sys.stdout.flush()

if __name__ == '__main__':
    main()
