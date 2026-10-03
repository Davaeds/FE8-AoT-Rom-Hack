@ ASMC AoT_ASMC_BoardCarried
@
@ When the active unit is carrying someone (Rescue), the carried unit boards the
@ evacuation boat: the carrier's carry state is cleared and the passenger leaves
@ the map the same way the REMU event command hides a unit (hidden and
@ unavailable), so a later REVEAL can bring it back for the ending cutscene.
@ Event slot C gets the passenger's character ID, or 0 if the active unit was
@ not carrying anyone.
@
@ Assembled with tools/asm.py (keystone). The build includes BoardCarried.dmp.

.thumb

.equ gEventSlots,          0x030004B8
.equ gActiveUnit,          0x03004E50
.equ GetUnit,              0x08019431
.equ RefreshEntityBmMaps,  0x0801A1F5
.equ RefreshUnitSprites,   0x080271A1

.equ US_RESCUING, 0x10
.equ US_RESCUED,  0x20
.equ US_REMOVED,  0x04010001   @ US_HIDDEN | US_BIT16 | US_BIT26, as set by REMU
.equ SLOT_C,      0x30
.equ UNIT_STATE,  0x0C
.equ UNIT_RESCUE, 0x1B

AoT_ASMC_BoardCarried:
    push {r4, lr}

    ldr  r0, =gEventSlots
    movs r1, #0
    str  r1, [r0, #SLOT_C]

    ldr  r0, =gActiveUnit
    ldr  r4, [r0]
    cmp  r4, #0
    beq  done

    ldr  r0, [r4, #UNIT_STATE]
    movs r1, #US_RESCUING
    tst  r0, r1
    beq  done

    @ The carrier puts the passenger down.
    bics r0, r1
    str  r0, [r4, #UNIT_STATE]
    ldrb r0, [r4, #UNIT_RESCUE]
    movs r1, #0
    strb r1, [r4, #UNIT_RESCUE]

    ldr  r3, =GetUnit
    bl   call_r3
    cmp  r0, #0
    beq  refresh

    @ The passenger goes aboard: no longer carried, off the map.
    movs r1, #0
    strb r1, [r0, #UNIT_RESCUE]
    ldr  r1, [r0, #UNIT_STATE]
    movs r2, #US_RESCUED
    bics r1, r2
    ldr  r2, =US_REMOVED
    orrs r1, r2
    str  r1, [r0, #UNIT_STATE]

    @ Report who boarded.
    ldr  r1, [r0]
    ldrb r1, [r1, #4]
    ldr  r2, =gEventSlots
    str  r1, [r2, #SLOT_C]

refresh:
    ldr  r3, =RefreshEntityBmMaps
    bl   call_r3
    ldr  r3, =RefreshUnitSprites
    bl   call_r3

done:
    pop  {r4}
    pop  {r0}
    bx   r0

call_r3:
    bx   r3

.ltorg
