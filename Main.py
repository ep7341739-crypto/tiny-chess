
#!/usr/bin/env python3
import sys
from collections import namedtuple
from itertools import count
A1,H1,A8,H8=91,98,21,28
N,E,S,W=-10,1,10,-1
D={'P':(N,N+N,N+W,N+E),'N':(N+N+E,E+N+E,E+S+E,S+S+E,S+S+W,W+S+W,W+N+W,N+N+W),'B':(N+E,S+E,S+W,N+W),'R':(N,E,S,W),'Q':(N,E,S,W,N+E,S+E,S+W,N+W),'K':(N,E,S,W,N+E,S+E,S+W,N+W)}
P={'P':[0]*20+[90]*8+[0,30,30,40,70,70,40,30,30,0,30,30,40,60,60,40,30,30,0,20,20,30,40,40,30,20,20,0,20,20,20,20,20,20,20,20,0,10,20,20,0,0,20,20,10,0,20,30,10,0,0,10,30,20]+[0]*20}
MATE=10000
Move=namedtuple('Move','i j prom')
Entry=namedtuple('Entry','lower upper')
class Pos(namedtuple('Pos','board score wc bc ep kp')):
 def gen(self):
  for i,p in enumerate(self.board):
   if p not in'PNBRQK':continue
   for d in D[p]:
    for j in count(i+d,d):
     q=self.board[j]
     if q.isspace()or q.isupper():break
     if p=='P':
      if d in(N,N+N)and q!='.':break
      if d==N+N and(i<A1+N or self.board[i+N]!='.'):break
      if d in(N+W,N+E)and q=='.'and j!=self.ep and abs(j-self.kp)>1:break
      if A8<=j<=H8:
       for r in'NBRQ':yield Move(i,j,r)
       break
     yield Move(i,j,'')
     if p in'PNK'or q.islower():break
     if i in(A1,H1)and self.board[j+(E if i==A1 else W)]=='K'and self.wc[i==H1]:
      yield Move(j+(E if i==A1 else W),j+(W if i==A1 else E),'')
 def rot(self):
  return Pos(self.board[::-1].swapcase(),-self.score,self.bc,self.wc,119-self.ep if self.ep else 0,119-self.kp if self.kp else 0)
 def move(self,m):
  i,j,r=m;p,q=self.board[i],self.board[j]
  put=lambda b,i,p:b[:i]+p+b[i+1:]
  b=put(put(self.board,j,p),i,'.')
  s=self.score+P.get(p,[0]*100)[j]-P.get(p,[0]*100)[i]
  if q!='.':s+=P.get(q.upper(),[0]*100)[119-j]
  if p=='P':
   if A8<=j<=H8:b=put(b,j,r)
   if j==self.ep:b=put(b,j+S,'.')
  wc=list(self.wc)
  if p=='K':
   wc=[0,0]
   if abs(j-i)==2:b=put(put(b,(i+j)//2,'R'),A1 if j<i else H1,'.')
  if i==A1:wc[0]=0
  if i==H1:wc[1]=0
  return Pos(b,s,wc,self.bc,j if p=='P'and abs(j-i)==20 else 0,j if p=='K' else 0).rot()
class S:
 def __init__(s):s.tp,s.tm,s.n={}, {},0
 def bound(s,pos,g,d):
  s.n+=1
  e=s.tp.get((pos,d),Entry(-MATE,MATE))
  if e.lower>=g:return e.lower
  if e.upper<g:return e.upper
  best=-MATE
  k=s.tm.get(pos)
  ms=[k]if k else[]
  for m in pos.gen():
   if m!=k:ms.append(m)
  for m in ms:
   p1=pos.move(m)
   sc=-s.bound(p1,1-g,d-1)if d else p1.score
   if sc>best:best=sc
   if best>=g:
    s.tm[pos]=m
    break
  s.tp[pos,d]=Entry(best,e.upper)if best>=g else Entry(e.lower,best)
  return best
 def search(s,h,md=3):
  s.n=0
  for d in range(1,md+1):s.bound(h[-1],0,d)
  return s.tm.get(h[-1])
def parse(c):return A1+(ord(c[0])-97)+(ord(c[1])-49)*10
def render(i):return chr(i%10+96)+str(i//10-1)
def main():
 h=[Pos('         \n'*2+' rnbqkbnr\n pppppppp\n ........\n ........\n ........\n ........\n PPPPPPPP\n RNBQKBNR\n'+'         \n'*2,0,[1,1],[1,1],0,0)]
 s=S()
 while 1:
  l=sys.stdin.readline()
  if not l:break
  if l.startswith('uci'):print('id name TinyChess\nid author make.fun\nuciok')
  elif l.startswith('isready'):print('readyok')
  elif l.startswith('ucinewgame'):h=[h[0]]
  elif l.startswith('position'):
   p=l.split();h=[h[0]]
   if'moves'in p:
    for m in p[p.index('moves')+1:]:h.append(h[-1].move(Move(parse(m[:2]),parse(m[2:4]),m[4:]if len(m)>4 else'')))
  elif l.startswith('go'):
   m=s.search(h)
   print(f'bestmove {render(m.i)}{render(m.j)}{m.prom}'if m else'bestmove 0000')
  sys.stdout.flush()
if __name__=='__main__':main()
