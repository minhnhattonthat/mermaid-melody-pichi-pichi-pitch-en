from PIL import Image
import sys
v=open(sys.argv[1],'rb').read()
rows=[]
for k in range(16):
  base=0x35AC+k*0x600
  if base+0x580>0x40000: break
  img=Image.new('L',(8*22,16))
  for t in range(44):
    col,row=t//2,t%2
    for y in range(8):
      for x in range(8):
        b=v[base+t*32+y*4+x//2]; p=(b>>4) if x&1 else b&15
        img.putpixel((col*8+x,row*8+y),p*17)
  rows.append(img)
m=Image.new('L',(8*22*3,16*3*len(rows)))
for i,r in enumerate(rows): m.paste(r.resize((r.width*3,48)),(0,i*48))
m.save(sys.argv[2])
