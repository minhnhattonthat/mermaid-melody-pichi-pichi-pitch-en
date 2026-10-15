"""VWF replacement for the mode-0 glyph renderer 0x080174BC (Thumb, assembled with keystone).

vwf(r0=code, r1=x (<0: -pixel, else cell), r2=map row, r3=flags; caller [sp]=layer, [sp+4]=alloc param)
 - map row base: layer<=1 ? 0x03002CE0+layer*0x500 : [0x03002950+0xC]; + row*64
 - every 8-px column the glyph advance touches gets a tile pair (alloc 0x08017054(2,param)) if its map entry
   is <=5, filled with the background (0x11111111 if flags&15<=4 else 0); flags&0x20/0x40: top/bottom rule
 - pixels with 2bpp value v!=0 get LUT[flags&15][v] low nibble; value 0 leaves the pixel alone
 - returns the advance (width table) in r0; caller 0x08017D16 adds r0 to the pen x.
"""
import struct
from keystone import Ks, KS_ARCH_ARM, KS_MODE_THUMB, KS_MODE_ARM

ASM = r"""
vwf:
    push {r4-r7, lr}
    mov r4, r8
    mov r5, r9
    mov r6, r10
    mov r7, r11
    push {r4-r7}
    sub sp, #32
    str r0, [sp, #0]
    str r3, [sp, #20]
    cmp r1, #0
    bge xpos
    rsbs r1, r1, #0
    b xok
xpos:
    lsls r1, r1, #3
xok:
    str r1, [sp, #4]
    ldr r4, [sp, #68]
    cmp r4, #1
    bgt layerptr
    ldr r5, lit_mapbuf
    movs r6, #0xA0
    lsls r6, r6, #3
    muls r6, r4, r6
    adds r5, r5, r6
    b mbok
layerptr:
    ldr r5, lit_ctx
    ldr r5, [r5, #12]
mbok:
    lsls r2, r2, #6
    adds r5, r5, r2
    str r5, [sp, #8]
    movs r4, #15
    ands r4, r3
    movs r6, #0xE0
    lsls r6, r6, #8
    cmp r4, #8
    ble palok
    movs r6, #0xF0
    lsls r6, r6, #8
palok:
    str r6, [sp, #12]
    movs r6, #0
    cmp r4, #4
    bgt bgok
    ldr r6, lit_1111
bgok:
    str r6, [sp, #16]
    ldr r5, lit_lut
    lsls r6, r4, #9
    adds r5, r5, r6
    movs r7, #15
    ldrh r6, [r5, #2]
    ands r6, r7
    mov r8, r6
    ldrh r6, [r5, #4]
    ands r6, r7
    mov r9, r6
    ldrh r6, [r5, #6]
    ands r6, r7
    mov r10, r6
    ldr r0, [sp, #0]
    ldr r5, lit_info
    lsls r6, r0, #1
    ldrh r6, [r5, r6]
    movs r7, #0x40
    lsls r7, r7, #8
    tst r6, r7
    beq gnormal
    movs r7, #0xFF
    ands r6, r7
    movs r7, #36
    muls r6, r7, r6
    ldr r5, lit_alt
    adds r5, r5, r6
    b gpok
gnormal:
    movs r7, #36
    movs r6, r0
    muls r6, r7, r6
    ldr r5, lit_font
    adds r5, r5, r6
gpok:
    str r5, [sp, #28]
    ldr r5, lit_width
    ldrb r6, [r5, r0]
    str r6, [sp, #24]
    cmp r6, #0
    beq done
    ldr r4, [sp, #4]
    lsrs r4, r4, #3
    ldr r7, [sp, #4]
    adds r7, r7, r6
    subs r7, #1
    lsrs r7, r7, #3
aloop:
    ldr r5, [sp, #8]
    lsls r0, r4, #1
    adds r5, r5, r0
    lsls r0, r4, #3
    ldr r1, [sp, #4]
    cmp r0, r1
    bge afresh
    ldrh r0, [r5]
    ldr r1, lit_3ff
    ands r0, r1
    cmp r0, #5
    bhi ahave
afresh:
    movs r0, #2
    ldr r1, [sp, #72]
    ldr r2, lit_alloc
    bl callr2
    ldr r1, [sp, #12]
    adds r1, r1, r0
    adds r1, #0x40
    strh r1, [r5]
    adds r1, #1
    movs r2, #0x40
    strh r1, [r5, r2]
    lsls r0, r0, #5
    ldr r1, lit_vram
    adds r0, r0, r1
    ldr r1, [sp, #16]
    movs r2, #16
afill:
    str r1, [r0]
    adds r0, #4
    subs r2, #1
    bne afill
    ldr r2, [sp, #20]
    ldr r1, lit_2222
    movs r3, #0x20
    tst r2, r3
    beq anotop
    subs r0, #64
    str r1, [r0]
    adds r0, #64
anotop:
    movs r3, #0x40
    tst r2, r3
    beq ahave
    subs r0, #4
    str r1, [r0]
ahave:
    adds r4, #1
    cmp r4, r7
    ble aloop
    ldr r0, [sp, #0]
    cmp r0, #0
    beq done
    movs r6, #0
yloop:
    ldr r5, [sp, #28]
    movs r0, #3
    muls r0, r6, r0
    adds r5, r5, r0
    ldrb r0, [r5]
    ldrb r1, [r5, #1]
    lsls r1, r1, #8
    orrs r0, r1
    ldrb r1, [r5, #2]
    lsls r1, r1, #16
    orrs r0, r1
    mov r11, r0
    movs r4, #0
xloop:
    mov r1, r11
    lsls r0, r4, #1
    lsrs r1, r0
    movs r0, #3
    ands r1, r0
    beq xnext
    cmp r1, #1
    bne xc2
    mov r1, r8
    b xcok
xc2:
    cmp r1, #2
    bne xc3
    mov r1, r9
    b xcok
xc3:
    mov r1, r10
xcok:
    ldr r2, [sp, #4]
    adds r2, r2, r4
    lsrs r3, r2, #3
    lsls r3, r3, #1
    ldr r0, [sp, #8]
    adds r0, r0, r3
    ldrh r0, [r0]
    ldr r3, lit_3ff
    ands r0, r3
    lsls r0, r0, #5
    movs r3, #0xC0
    lsls r3, r3, #19
    adds r0, r0, r3
    adds r3, r6, #2
    lsls r3, r3, #2
    adds r0, r0, r3
    movs r3, #4
    ands r3, r2
    lsrs r3, r3, #1
    adds r0, r0, r3
    movs r3, #3
    ands r3, r2
    lsls r3, r3, #2
    ldrh r2, [r0]
    movs r7, #15
    lsls r7, r3
    bics r2, r7
    lsls r1, r3
    orrs r2, r1
    strh r2, [r0]
xnext:
    adds r4, #1
    cmp r4, #12
    blt xloop
    adds r6, #1
    cmp r6, #12
    blt yloop
done:
    ldr r0, [sp, #24]
    add sp, #32
    pop {r4-r7}
    mov r8, r4
    mov r9, r5
    mov r10, r6
    mov r11, r7
    pop {r4-r7}
    pop {r1}
    bx r1
callr2:
    bx r2
    .align 2
lit_mapbuf: .word 0x03002CE0
lit_ctx:    .word 0x03002950
lit_1111:   .word 0x11111111
lit_2222:   .word 0x22222222
lit_lut:    .word 0x08D739F0
lit_info:   .word 0x08D7ECAC
lit_alt:    .word 0x08D7D1AC
lit_font:   .word 0x08D74FF0
lit_width:  .word WIDTH
lit_3ff:    .word 0x3FF
lit_alloc:  .word 0x08017055
lit_vram:   .word 0x06000800
"""


def assemble(addr, width_addr):
    ks = Ks(KS_ARCH_ARM, KS_MODE_THUMB)
    enc, _ = ks.asm(ASM.replace("WIDTH", hex(0x08000000 + width_addr)), 0x08000000 + addr)
    return bytes(enc)


HOOK = 0x0174BC        # bx pc ; nop ; (ARM) ldr ip,[pc] ; bx ip ; .word target|1
CALLER_ADV = 0x017D16  # adds r0,r4,#0 ; adds r0,#0x2c ; ldrb r0,[r0]  -> nop x3 (r0 = returned advance)


def install(rom, alloc, width_off):
    code = assemble(0, width_off)  # size probe
    at = alloc.put(b"\0" * (len(code) + 8), align=4)
    code = assemble(at, width_off)
    rom[at:at + len(code)] = code
    arm = Ks(KS_ARCH_ARM, KS_MODE_ARM)
    a, _ = arm.asm("ldr ip, [pc]\nbx ip", 0x08000000 + HOOK + 4)
    hook = bytes.fromhex("7847c046") + bytes(a) + struct.pack("<I", 0x08000000 + at + 1)
    rom[HOOK:HOOK + len(hook)] = hook
    assert rom[CALLER_ADV:CALLER_ADV + 6] == bytes.fromhex("201c2c300078"), rom[CALLER_ADV:CALLER_ADV + 6].hex()
    rom[CALLER_ADV:CALLER_ADV + 6] = bytes.fromhex("c046c046c046")
