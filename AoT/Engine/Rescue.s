@ ASMC AoT_ASMC_Rescue
@
@ Event slot 2: character ID of the carrier. Slot 3: character ID of the unit
@ to pick up. The carrier ends up carrying the other unit exactly as if it had
@ used the Rescue command. Does nothing if either unit is missing.
@
@ Assembled with tools/asm.py (keystone). The build includes Rescue.dmp.

.thumb

.equ gEventSlots,          0x030004B8
.equ GetUnitByCharId,      0x0801829D
.equ UnitRescue,           0x0801834D
.equ RefreshEntityBmMaps,  0x0801A1F5
.equ RefreshUnitSprites,   0x080271A1

.equ SLOT_2, 0x08
.equ SLOT_3, 0x0C

AoT_ASMC_Rescue:
    push {r4, lr}

    ldr  r0, =gEventSlots
    ldr  r0, [r0, #SLOT_2]
    ldr  r3, =GetUnitByCharId
    bl   call_r3
    mov  r4, r0
    cmp  r4, #0
    beq  done

    ldr  r0, =gEventSlots
    ldr  r0, [r0, #SLOT_3]
    ldr  r3, =GetUnitByCharId
    bl   call_r3
    cmp  r0, #0
    beq  done

    mov  r1, r0
    mov  r0, r4
    ldr  r3, =UnitRescue
    bl   call_r3

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
