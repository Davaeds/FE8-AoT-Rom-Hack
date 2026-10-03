@ ASMC AoT_ASMC_ClearPlayers
@
@ Deletes every player unit (the blue unit array), so a chapter can load its
@ squad fresh: chapter 2 jumps three years ahead and the children come back
@ as cadets with new classes, levels and gear. A normal unit load keeps a
@ unit that already exists instead of replacing it.
@
@ Assembled with tools/asm.py (keystone). The build includes ClearPlayers.dmp.

.thumb

.equ gUnitArrayBlue,       0x0202BE4C
.equ ClearUnit,            0x080177F5
.equ RefreshEntityBmMaps,  0x0801A1F5
.equ RefreshUnitSprites,   0x080271A1

.equ UNIT_SIZE,  0x48
.equ UNIT_COUNT, 62

AoT_ASMC_ClearPlayers:
    push {r4, r5, lr}
    ldr  r4, =gUnitArrayBlue
    movs r5, #UNIT_COUNT

loop:
    ldr  r0, [r4]
    cmp  r0, #0
    beq  next
    mov  r0, r4
    ldr  r3, =ClearUnit
    bl   call_r3
next:
    adds r4, #UNIT_SIZE
    subs r5, #1
    bne  loop

    ldr  r3, =RefreshEntityBmMaps
    bl   call_r3
    ldr  r3, =RefreshUnitSprites
    bl   call_r3

    pop  {r4, r5}
    pop  {r0}
    bx   r0

call_r3:
    bx   r3

.ltorg
