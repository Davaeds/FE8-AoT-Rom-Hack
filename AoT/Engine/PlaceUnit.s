@ ASMC AoT_ASMC_PlaceUnit
@
@ Event slot 2: character ID. Slot B: position (x in the low half, y in the
@ high half). Puts the unit on that tile even if its class could not walk
@ there. Unit loads always slide a unit to the nearest tile it can stand on,
@ so this is how Carla ends up under the collapsed house and the Colossal
@ Titan in the gateway.
@
@ Assembled with tools/asm.py (keystone). The build includes PlaceUnit.dmp.

.thumb

.equ gEventSlots,          0x030004B8
.equ GetUnitByCharId,      0x0801829D
.equ RefreshEntityBmMaps,  0x0801A1F5
.equ RefreshUnitSprites,   0x080271A1

.equ SLOT_2, 0x08
.equ SLOT_B, 0x2C
.equ UNIT_X, 0x10
.equ UNIT_Y, 0x11

AoT_ASMC_PlaceUnit:
    push {lr}

    ldr  r0, =gEventSlots
    ldr  r0, [r0, #SLOT_2]
    ldr  r3, =GetUnitByCharId
    bl   call_r3
    cmp  r0, #0
    beq  done

    ldr  r1, =gEventSlots
    ldrh r2, [r1, #SLOT_B]
    strb r2, [r0, #UNIT_X]
    ldrh r2, [r1, #SLOT_B + 2]
    strb r2, [r0, #UNIT_Y]

    ldr  r3, =RefreshEntityBmMaps
    bl   call_r3
    ldr  r3, =RefreshUnitSprites
    bl   call_r3

done:
    pop  {r0}
    bx   r0

call_r3:
    bx   r3

.ltorg
