# Splatterhouse PC port - Phase 1 notes (6809 map)

## ROM image in the PC port (SPLATTER.EXE FUN_00408750, Ns1MemFactory slot 2)
- 1 MB buffer; files loaded PRG7..PRG0, each 64 KB loaded TWICE consecutively.
  PRG7 @0x00000/0x10000, PRG6 @0x20000/0x30000, PRG5 @0x40000, PRG4 @0x60000,
  PRG3 @0x80000, PRG2 @0xA0000, PRG1 @0xC0000, PRG0 @0xE0000/0xF0000.
- Namco System 1 banking (same numbers as MAME namcos1). 8 windows of 8 KB, window = (addr>>13)&7.
- ROM banks 0x200-0x3FF: k=bank-0x200; buffer off = 0xE0000 - 0x20000*(k>>6) + (k&15)*0x2000
  (128 KB chunk mirrored 4x). Helper: scripts\mkrom.py bank_off().
- Non-ROM banks: 0x170-0x172 palette RAM; 0x173 display-control/sprite regs (type 1, NOT ROM);
  0x178-0x17B video RAM; 0x17C, 0x17E (type 3/4); 0x17F I/O + key chip (0x3000); 0x180-0x183 RAM;
  0x160, 0x171 also used.
- Bank register: writes $E000-$EFFF, window=(addr>>9)&7. Even addr: latch=(data&3)<<8.
  Odd addr: bank=(data&0xFF)|latch. Code uses LDD #bank; STD $E?00.
- Main CPU writes $FC00/$FC01 = sub CPU's E000 bank; $F000 releases sub CPU; $F200 IRQ ack/watchdog;
  $F400, $F600 other control.
- Both CPUs reset with window 7 = bank 0x3FF (buffer 0x1E000, tail of PRG7), shown at E000-FFFF.
- Sub CPU E000 bank set to 0x377 (buffer 0x4E000, tail of PRG5).
- DLL6809 only exposes Reset/AttachMemoryEmulator/Create/Destroy/Execute/RequestInterrupt; vectors are read
  through the memory callbacks. Mapping lives in the EXE, not the DLL. Sound CPU replaced (pre-rendered WAV).
- PC patch: SplatterCpu1RomCorrectFilter returns 0x21 for ROM offsets 0x29B3E/0x39B3E (PRG6+0x9B3E).

## Vectors (main, bank 0x3FF)
FFEC=E00A (game start), FFEE=DD4E, FFF0=DD60, IRQ FFF8=E0DF, RESET=E000, others E000.
Sub (bank 0x377): all E000 except IRQ=E0A1.
E000 stub: window 6 = bank 0x3B4, A=0 (main)/1 (sub), JMP $C000.

## Kernel (bank 0x3B4 = PRG6+0x8000, at C000)
A==1 -> D9E9 sub start; A==2 -> C12A IRQ service; else boot (C00E..C2BB), ends LDD $FFEC; TFR D,PC.
Only ROM bank loaded via immediate constant in the main code is 0x3B4; other ROM banks come from tables/computed.

## Main loop
game_start E00A: DP=0, S=$1F00, window0=RAM 0x180 zeroed, JSR E0A8/E06D/CD5B/F5B7, set sub bank, release sub,
wait IRQ handshake DP$06, enable IRQ.
main_loop E05D: DP$02=1; STA $F200 until IRQ clears; JSR E17C; repeat.
irq E0DF: ack, A=2 JSR C000 (C12A), window 6 = 0x173 copy, restore bank from DP$15, BSR E124, E150, RTI.
frame_update E17C: ++DP$00 frame counter; skip if DP$41|DP$43; state = DP$2A; JSR [E1BB+2*state];
then JSR CCDF, CD67, CD86, E378.
State table E1BB: E1C7 E1F1 EF30 EE00 E273 E339 (all in fixed bank).

## Gameplay banks (Phase 2, CONFIRMED by emulating the boot with scripts\shmach.py/shrun.py)
After boot the window map is: 0=RAM 0x180, 1=I/O 0x17F, 2=shared 0x17C, 3=ROM 0x230 (6000), 4=ROM 0x3B1 (8000),
5=ROM 0x3FD (A000), 6=ROM 0x3FE (C000), 7=ROM 0x3FF (E000). Bank 0x3B4 (kernel) is only boot + IRQ service.
Other banks are set temporarily from code: 0x3B5/0x3B6/0x3B0 into windows 2/3 (C958, C994, C9E7), etc.
Image of the gameplay map: work\game_6000.bin (built from those 5 banks). Ghidra program: game_6000.bin (base 0x6000).
scripts\reach.py = recursive descent + jump-table expansion over that image; 574 entry points found, fed to MkFns.

## Frame flow (CONFIRMED)
IRQ (E0xx): E124 reads $3026 -> DP FA..FD (P1: held, newly pressed, inverted, prev) and $3027 -> DP 102..105 (P2);
E150 reads $3028/9. Main loop E05D: wait IRQ flag, JSR E17C. E17C: JSR [DP2A*2+E1BB] (6 states), then JSR CCDF
(object loop), then CD67, CD86, E378. State 4 (E273) is the attract scene (static objects types 6,7 appear when forced).
F208 (called from the state handler chain): E3BF, B479 (players), EC7B, E480, CD9A, AE09, C4DE, D5D7.

## Object table (CONFIRMED)
CCDF: 32 slots x 32 bytes at 0x0F9D, byte0 active, byte9 type, JSR [type*2+0x8000] in bank 0x3B1 (obj_update_table, 25 words).
Distinct handlers: types 0,12-15 stub 8788/8789; 1=804E (sub-dispatch on byte4, table 8057); 2=80E7; 3,4=8151; 5=8255; 6=82C4;
7=8342; 8=8343; 9=8373; 10=8490; 11=84C3; 16=8800; 17=84F1; 18=8504; 19=8561; 20=8562; 21=8578; 22=85CB; 23=865D; 24=8728.
Init table at 0x8032 (CD03 JSR [B*2+8032]): only type 1 (809A) is real so far. Secondary 16-slot array at 0x099D,
table 8831 (4 entries: 8839, 88E6, 88BC...). Roles of types are NOT yet known (names are obj_update_typeN).

## Player (Rick) update B479 (CONFIRMED structure, GUESSED meanings)
2 player structs at RAM 0x011D, stride 0x40 (P1, P2). C964 loads DP F7=held, F8=newly-pressed input for each.
Held nibble -> direction code 0..8 (table C982): code 3 and 7 = the left/right pair (bits 0,1), 1 and 5 = the other
axis (bits 3,2). Per state (obj+4) pointer table B501 -> 9 direction handlers + 4 button handlers (F8 bits 7..4).
Buttons (CONFIRMED by code): F8 bit5 = jump (B748: vy=0xFB80, state 0x0F), F8 bit4 = attack (D0FE); bit7 = start.
Held F7 bit5 in air lowers gravity per frame (variable jump height); F7 bit2 held changes attack (D0FE).
Fields: +0 active, +2 airborne (guess), +4 state, +5 anim frame, +10/11 vx (16 bit, accel 0x40 walking, 0x10 in air,
cap table B7E2), +14/15 vy, +16 bit5 = facing (0 right, 1 left), +19/20 and +25/26 position words (x/y not told apart),
+38 pointer to nearby/held object (weapon dispatch via table D11F by its type), +58 demo-script flag, +59/60 script counter.
States seen: 1 stand/walk, 0x0F jump, 3 and 4 other ground moves (guess crouch/walk), 5 6 9 10 attack variants (guess).
Health/hitboxes/knockback: now found, see Phase 3 below.

## Ghidra (C:\re\splatterhouse\ghidra, project SH)
Program game_6000.bin: 567 functions, 13658 of 40960 bytes disassembled (33%) after seeding; descent in python reaches
~31 KB. Older programs: bank_3ff.bin (fixed bank + overlay b3b4_C000), main_6000.bin (superseded). names.txt applied (63 names).

## Uncertain / next
- Emulator never reaches real gameplay (stalls at DP2A=0,2B=1; credit/start path not found), so player RAM values at runtime unseen.
- Phase 3 closed damage/health/boxes. Open: per-type enemy health, default health DIP, slide attack, hit effects 2-11, state 8 trigger.
- Sub CPU (bank 0x377) and 0x29B3E patch reason not analysed.

## Phase 3: combat (CONFIRMED-FROM-CODE unless marked; nothing seen in RAM, emulator attract stall not attempted)
Units: 60 fps, 8.8 fixed point, +y down. Tools: scripts\dis2.py (bank windows), dis6000.py; dumps work\p3\dis_*.txt.
Struct (players 0x011D/0x015D, enemies 32 @0x019D, stride 0x40): +0 active (1 normal, 2 hurt/invuln), +1 invuln timer,
+2 airborne, +4 state, +5 state timer (counts down), +6 already-hit flag, +9 type, +10/11 vx, +12/13 vz, +14/15 vy,
+16 facing (0x20=left), +19..21 x, +22/23 z (depth), +25/26 y, +28 health, +32/33 16-bit timer, +38 held obj, +61 hitbox frame.
Frame chain F208: B479 players, EC7B scroll script, E480 camera, CD9A secondary objs, AE09 enemy loop (table 0x6000, bank 3F9).
### Hit pipeline
- Boxes: 32-byte records in bank 0x3B5 (0x4000-0x5FFF). [0..2] offsets (x mirrored by facing), [3] damage, [16] x ext,
  [18] z ext, [20] y ext, [22] head threshold, [27] hit-effect id. Tables: player attack 0x400E, player defender 0x4006,
  enemy defender 0x4026, enemy attack 0x41A6 (index = B in `LDB #n; JSR CEAC`). Frame lists overlap; only frame 0 matters.
- Overlap D483/D4A3, per axis (x,z,y): |centre diff| - attacker ext < 0, then also < defender ext; defender centre = its position.
  Builders D424/D439, record lookups D415/D474/D4FB/D512. Enemy-vs-player: CEAC, damage CFB9.
- Player attack: D0FE dispatch by held weapon (D11F/D108); punch D135 -> D13D/D142/D145; low attack D064-D076; sweep D185;
  nearest-enemy search D1D7; weapon swing D2BA-D2CC; throw D33C/D344; dive D38A/D394.
- Enemy hit: D529 subtracts record[3] from +28, sets +6 so one swing hits once; D590/D5A6 pick reaction (banks 3B2/3B3,
  index type*4, +2 if dead). Type 3: hit -> state 0x12, vx 2.0, vy -4.0; dead -> state 0x13, 48 f timer.
- Player hurt: B84B (active=2, knockback), invuln countdown B97D with table B4FB, death B86D, respawn/lives B8A5. Lives 3.
  Start health from config table E0A8/E0D9; enemy health from spawn record C3CE/C432. Exact damage numbers and invuln frames
  sit in record[3] / table B4FB and were not tabulated.
- Physics C52D: gravity +0x40/f (0.25 px/f^2), terminal vy 8 px/f, jump vy -4.5 px/f (0xFB80), walk accel 0.25, air accel 1/16.
### Basic melee enemy (bank 3FA 83D9; types 2, 0x98, 0x9A, 0xA5)
- Per frame: state jump table 83EA, attack box via `LDB #2; JSR CEAC` (skipped for 98/9A/A5), physics C52D, check 8578.
- State 1 walk (84F2): speed table 84E8: type2 0.5, 0x98 0.375, 0x9A 0.5, 0xA5 0.75, default 0.5 px/f. Timer +32 = 128 f (2.1 s).
- Expiry -> 844E picks by distance (threshold 0xB0 = 176 px) and random (CA89 &0x0E) from tables 8485 near / 847D far:
  mostly re-walk 84B3 (128 f) or windup 8503.
- Windup 8503: state 4, 64 f (1.07 s); then 8515 lunge: vx 1.75, vy -5.0 (type 2: vx 0, vy -7.0), state 0x0F; landing 8539.
- Cooldown is effectively the next 128 f walk. Contact damage = enemy attack box index 2.

## For the Goobi brawler
| mechanic | Splatterhouse value | status |
|---|---|---|
| frame rate / numbers | ~60 fps, 8.8 fixed point | confirmed |
| gravity / terminal fall | 0.25 px/f^2 / 8 px/f | confirmed |
| jump launch | -4.25 px/f MEASURED (code read said -4.5); held gravity 5/32, released 0.25; airtime 56 f held / 36 f tap; apex ~60 / ~40 px | measured |
| walk accel | 0.125 px/f^2 to cap 1.375 px/f MEASURED (code read said 0.25); air 1/16 | measured |
| hit detection | 3-axis box overlap (x, depth, height), per-frame attack box vs defender box | confirmed |
| attack box data | offset, ext xyz, damage, effect id; mirrored by facing | confirmed |
| one hit per swing | already-hit flag (+6) | confirmed |
| hit reaction | per-type table: state, knockback vx/vy, timer (type 3: vx 2.0, vy -4.0, death 48 f) | confirmed |
| player hurt | -1 hp of 4; 16 f knockback (vx 1.0 away, hop -2.0); then 60 f invulnerable | measured |
| lives | 3 | confirmed |
| melee enemy | walk 0.4-0.75 px/f, 128 f wander, 64 f windup, lunge 1.75 px/f with -5 px/f hop | confirmed |
| enemy action choice | random, split by 176 px distance | confirmed |
| damage / health totals | player 4 hp, contact = 1; round-1 enemies die to 1 punch | measured |
| punch | 20 f, roots player | measured |
| enemy walk speeds (round 1) | 1.25 / 0.875 / 0.75 px/f by type | measured |
| slide / jump-kick reach | not measured | guessed |

## Phase 4: numbers (CONFIRMED-FROM-CODE/ROM data, 10-10)
- Player hurt (CFB9): health -= enemy attack record[3]; reaction record D000: hurt = state 0x12, 16 f, vx 1.0 (away), vy -2.0;
  dead (health 0) = state 0x13, 80 f, no velocity (record D008). Then active=2.
- Hurt end B85E: when timer runs out -> state 1 and invuln timer +1 = 0x3C = 60 f. Countdown B97D (via table B4FB by active
  0/1/2 -> BA79,BA79,B97D) pauses in states 0x12-0x14, then active=1.
- Death B888/B8A5: 90 f wait (0x5A), lives +50 -= 1 (start 3, EE48); respawn health = 4 hard-coded (B8BD), state 0x14 for 0x70 f.
- Start health = $147A from config table E0D9 indexed by setting byte C000+0xC (bank 0x173): pairs ($147C,$147A) =
  (1,4), (0,6), (2,2) -> health 4 / 6 / 2. Default setting assumed 0 -> 4.
- Enemy health = byte 9 of the type's frame-0 DEFENDER record (table 0x4026, bank 3B5), set in C3CE; bytes 12/13 = start
  state/timer. Full list work\p3\hp.txt (hp.py). 144 of 192 types have 1 hp; basic melee 02/98/9A/A5 = 1 hp; type 03 = 2;
  bigger: 1E,36,A0 = 8; 37 = 16; 53,5F = 20; 0E,21,6F = 32; 57 = 40; 39 = 64; 6E = 127 (prop/invulnerable?).
- Enemy contact damage (attack record[3]) = 1 for almost all types; 39 = 64 (instant kill hazard).
- Player attack damage (records via 0x400E by index, or fixed): punch idx 0 = 1 dmg (box 24 fwd, 16 wide), active while
  state timer < 16; sweep 44D8 = 1; idx 3 (D262, jump attack from state timer 0x12, vy -4/f... guess) = 2 with 128 wide box;
  dive 4518 = 2; weapon swings use held object type as index (2..8) = 2 dmg each.

## Phase 4: enemy identities (10-10, checked with state sheets)
Renderers: `work\p4\rtypes.py` -> `types_sheet.png` (frame 0 of the start state, every type); `work\p4\rstates.py <hex,hex..> out.png` -> frame 0 of states 0..19 per type (`st1.png`, `st2.png`). Copies in goobi private\splatterhouse\sheets. Path: sub-CPU F769, class 2 table 0x63C8. Palette = colour>>1 into bank 0x330; some colours are off.
Gotcha: a type's state list has no length, so states past its last real one read the next type's entries (type 32: s7-10 = shutters, s11+ = eye painting). Animation sets repeat across states because many states share one frame list.
| types | evidence | name (confidence) |
|---|---|---|
| 00 01 24 27 2b-2f 75 79 7f 9e 9f b8-bf | brown shambling corpse | Deadman, basic zombie (high) |
| 25 26 | corpse crawling on floor | legless Deadman / crawler (mid) |
| 02 98 9a a5 a6 | every state is a crawling hand (s4 hurt, s15 leap) | crawling severed Hand (high) |
| 30 46 47 90 | red worm | Boreworm (high) |
| 57 hp40 | huge purple hooded sac, few states | Mother Boreworm (mid) |
| 36 a0 hp8, 3a a4, 1d, 37 hp16, 39 hp64, 35 3b 3f | painting with eye, chairs, knife, chandelier, shutters | Poltergeist room boss (high) |
| 0e 21 hp32 | Rick's own moves (punch, kick, crouch, slide, lying) in Rick colours | Mirror Rick boss (high) |
| 0f hp3, 1e hp8 | same Rick moves, grey | Mirror Rick reflections / weaker copies (mid) |
| 77 hp18 | black brute; s11-13 are Jennifer in white dress | Jennifer, transformed (high) |
| 53 5f hp20 | bag head, bloody body, big lunges | Biggy Man (mid-high) |
| 56 hp12 | inverted gold cross; s19 ball | Evil Cross (high) |
| 6f hp32 | dark red winged mass; s18 pink brain, s19 eyed worm; only in round 20 with flesh blobs 61/68 | womb boss, stage 6 (mid-high) |
| ae b2 b5 b6 (b1?) | grave marker with mask (ae s0), burning ground, spotted arms; round 23 only | Hell Chaos, stage 7 (mid-high) |
| 6e hp127 | grey spikes, same in every state | invulnerable boss part / hazard (low) |
| 4c-4e 88-8a | lying corpse -> blood -> its head flies off | corpse that spawns a flying head (high) |
| 52 58-5d | green head with blood trail | flying head (high) |
| 07 12 48 50 | pale ghoul hanging head-down, s18 spits green bile | hanging bile ghoul (mid) |
| 10 | green ghoul rising from water | Waterdead / swamp ghoul (mid) |
| 32 34 | rotting standing zombie | rotting ghoul (mid) |
| 55 | floating blue woman | ghost (mid) |
| 73 hp10 | cloaked figure in pointed hat; s18 cowers | witch / ghoul in hat (mid) |
| 60 61 7b 70 | red toothed flesh blobs, jaw | flesh blobs of the womb/Hell Chaos area (mid) |
| 31 33 | body hanging on chain | hanging corpse (high) |
| 08 4a 94 99 16 | green slime, weeds, vines | slime puddle / weeds (mid) |
| 15 | wooden door | door (high) |
| 62 67 a9 aa ab ac | walls, tentacles, fire strips | scenery hazards (mid) |
| 80-87 | tiny, unclear even across states | small critters (low) |
| 40 41 45 49 8b 8c 8f 1f 20 | tiny / sparks / spears | projectiles and effects (mid) |

## Phase 4: rounds and stages (10-10)
Spawn tables: setup C497 (bank 3fe) maps window 3 to bank 3F8 (C4D5 writes 0x3F8 to $E600). Header = w(w(0x6000 + 8*round)) where round = $65 (per player copy at actor +48; $67 at +49 and $0113 pick identical copies). Header 8 bytes:
[0] scroll list ($010B, C315): (word scroll pos, word -> records), spawns when scroll $9C passes pos, ends at a negative word.
[2] frame list ($010D, C330): (word frame count, word -> records), matched by equality on counter $010F; ends where counts stop rising (0x2000 sentinel).
[4] records spawned at round start (C4C6). [6] -> $0111.
Spawn record 10 bytes (C352/C378): [0] flags (negative = end), [1] type -> actor +9, [2..3] x (+scroll unless B=1), [4..5], [6..7] other coords, [8..9] -> actor +32.
Dumper: `work\p4\spawns.py`; output `work\p4\spawns.txt`. Child enemies (58-5d heads, 57, 30/46/47 worms in boss rooms) are spawned by other actors, not by these lists.
Round flow (from code, 10-10): round-end dispatch A003 jumps through the word table A009[$65] (bank 3fd window 5) to a per-round handler A039..ACC9. Each handler checks the player's x (+19) and fall depth (+25 + +22 >= 0x118 = fell through the floor) and stores the next round in $6F (F276 copies it to actor +48 on round change; round 0x18 = game over/ending). A6E5 = sets actor +58 (room/lock id) and actor state 2. Continue table F36D[round] = round you restart from = first round of the stage:
F36D: 00 01 02 02 02 05 06 06 06 00 01 05 06 0d 0d 0d 0d 0d 0d 0d 14 0d 0d 17. New game starts at round 1 (EE3A); attract demo picks rounds from a table via $147D (EF68).
| round | exits (x = scroll x) | stage, content |
|---|---|---|
| 0 | (demo) | attract demo, same header as round 1 |
| 1 | x>=0x8C8 -> 10 | stage 1 corridor |
| 10 | -> 2 | stage 1 end, Boreworm room (30 46 47 worms, 48/49 hanging ghouls); continue -> 1 |
| 2 | fall through floor after x 0x560 -> 3 | stage 2 hall, hanging corpses |
| 3 | x>=0x518 -> 4 | stage 2 flooded basement: ghoul rising from water 10, splashes 11/13, spikes 6e |
| 4 | -> 5 | stage 2 poltergeist room |
| 5 | x>=0xA30 -> 6; fall before x 0x550 -> 11 | stage 3, Biggy Man |
| 11 | x>=0x390 -> 5 | stage 3 lower path (same water-room set as round 3), climbs back to 5 |
| 6 | x>=0x5B0 -> 7; fall -> 12 | stage 4 start, door |
| 12 | -> 6 | stage 4 pit of Boreworms, back up to 6 |
| 7 | x>=0x570 -> 8 | stage 4 Mirror Rick |
| 8 | -> 13 | stage 4 Evil Cross |
| 13 | -> 14 | stage 5 maze entry |
| 14 | x>=0x7D4 -> 15; fall -> 16 | maze, crawling hands |
| 15 | -> 22, 16 or 18 (x 0x370 / 0x2B0 / fall) | maze |
| 16 | -> 18, 17 or 19 | maze, water-room set again |
| 17 | -> 19 | maze |
| 18 | -> 17; fall -> 21 | maze, witch 73 + zombies 72/74 |
| 21 | -> 19 | maze room (03 24 55 9f) |
| 22 | -> 17 | maze room that re-fights the Mirror Rick set (0e 21 + 0f clones) |
| 19 | -> 20 | stage 5 end, Jennifer 77 |
| 20 | -> 23 | stage 6 womb boss 6f |
| 23 | -> 0x18 (ending) | stage 7 Hell Chaos at the grave |
| 9 | none | unused, empty spawn lists, continue -> 0 |
Exit snippets: `work
ounds_exits.txt`.
7e (blue orb, 2 states, in most rounds) is likely a pickup or effect. Still open: 6e, 80-87, palette per actor.

## Phase 5: full naming (started 10-10)
Method: unnamed call targets per region (work\p5\targets_*.txt, 512 total on top of 91 named) handed to Sonnet agents with work\p5\BRIEF.md; results in work\p5\names_<region>.txt + notes_<region>.md, merged into names.txt after a check.
- Enemy dispatch (CONFIRMED from code AE17-AE32): bank 3f9 at 6000 holds 4 bytes per type (actor +9): window-4 bank word (written to $E800) + handler. Banks: 3fa (114 type slots, 53 handlers), 3fb (37 slots), 3fc (41 slots). Dump `work\p5\enemy_type_table.txt` (py -I work\p5\etab.py). Slots bd-bf -> 3fa:65a0 (probably past the end).
- Window writes from code: $E400 (w2) 3b5/017c, $E600 (w3) 3f9/3f8/3b6/3b0, $E800 (w4) 3b1 or table, $E200 (w1) 017f/017b/0171, $EC00 (w6) 3b4/0173. No sound-CPU ROM in the port (SOUND\ WAVs replace it).
- Agents running (10-10): regions 8 a1 a2 c e, enemy banks 3fa 3fb 3fc, kernel 3b4, sub CPU 377.
### Phase 5 results (10-10, agent passes; per-region detail in work\p5\notes_<region>.md, names merged into names.txt = 1952 lines)
Code banks (everything else is data): main 3b1 (w4, objects; code ends 8B5A), 3fa/3fb/3fc (w4, enemy AI; 3fb code ends 9CF2, 3fc 9A41, tails are stale copies), 3fd (A000), 3fe (C000; FF from D699), 3ff (E000), kernel 3b4 (C000 boot/IRQ/test); sub CPU 377 only (E000). Data banks: 3f8 spawns, 3f9 type table, 3b0/3b5/3b6, 230; sub maps 170/171/17B/370/230/270/372-376 as data.
Name prefixes: `3fa:0x....` etc. for switched banks; unprefixed = default gameplay map. Unprefixed 0x8xxx = bank 3b1 except the old Phase 3 enemy names (83D9, 8503, 8515, 844E, 84C8) which are 3fa.
- Object arrays (bank 3b1 + C/D): 0x0F9D x32 HUD/sequence objects (types 0-24: life pips, item icon, lives, gauge, round number, bursts); pickups 0x099D x16 (CD9A, table 8831; fly, bounce vy -0x200, lie, despawn 0xB4 f); FX 0x0B9D x32 (D5D7, table 8904). Correction: FX array is 0x0B9D.
- Player: B501 24 states -> 18 arrays B531..B6EB of 13 words (9 directions, 4 buttons; jump B748). Attacks by held item via D11F.
- Enemy helper library AE8B-B471 (~45 fns); AF86 = nearest player (57 callers). Kernel helpers: CA89 random, CAA0 player ptr, CC43 sin/cos, C4F5/C507/C51B step x/z/y.
- Sound: BA7A play_sound(B=id 0..0x8C), table BB16 -> records BC30 -> register lists BF40 (writes 0x31xx I/O pairs); runs only when $2A is 2 or 3.
- Terrain: tile class via thresholds C64B, 5x5 surface table C664 (8 bytes: id, handler, friction); handlers air/ground/push C78C-C79E.
- Score BCD; extra-life tables CB19/CB34. High scores 8x8 at $1430 (defaults F5C8, F5B7 init, F4D9 rank, F51C name entry).
- Per-round tables: music F0BA (4 bytes), continue F36D, stage intro F87E, round->stage EC53. Attract demo rounds EF9D (4 pairs, $147D mod 4).
- Debug: round-select menu F608 (round, lives, power) when $010A & 0x20; 0x10 debug text, 0x40 pause; $010A bit 2 skips round 23 to the ending.
- Rounds (bank 3fd): each handler runs a substate machine on $66. Round 4 poltergeist = scripted waves (A2B0, thrown types 3A/38/36; shake ED2F/ED7F). Round 7 places 3 Mirror Rick clones at random x pairs A564. A6E5 lock player / A6EF unlock / A708 scroll zone.
- Enemy AI: 3fa 31 handlers; types 0x80-0x87 = 8 gib critters (3fa:9F50) spawned by 3fa:9E80 when types 32/34 die (closes the old question). Types 11/13 = reflections copying P1/P2. 3fb: Biggy Man 53 = 5 parts 69-6D posed by 8277 (table 830E); Evil Cross 56 = 6 orbiting heads 58-5D (8B07/8B49, launch 4.0 px/f); witch 73 revives zombies 72/74; womb 6F kills child blobs (90F0); 5E/5F read P2 input $0102/$0103 (GUESS). 3fc: boss 57 (hp 40) spawns tentacles AB/AC/AA (+40 parent), phase table 922B (0x20,0x18,0x10,0x08,0); ghost 55 throws A3 (8F36); state 0x13 = shared dying.
- Kernel 3b4: boot handshake with sub (0x90 RAM test, 0xA0 ok / 0A-0D errors, 0xA6 go), key chip $3000==A6; test menu 5 pages + hidden joystick debug C947; IRQ C12A coins: credits BCD DP15 (kernel DP), counters DP25/26, meters $3039/$303A, lockout $303B; header DD4E (id 0x2222, sub bank 0x77); Japan NOTICE DAFC.
- Sub CPU 377: video CPU. Windows w0 180 w1 171 w2 17B w3 370 w4 230 w5 270 w6 376; sprite pass remaps 17E/372-376. Mailbox $13C9-$13CB + 8 msg slots at $13CC; 3 BG layers streamed from 66 records E647; sprites by depth buckets (F769); palette banks 170/171.
- Open: attract substates (EE6B/EFB2) never advance in our emulator; $2A/$2B/$2C/$41/$43 shared by both CPUs; many GUESS names.

### Ghidra overlays + full C dump (10-10)
- Overlays added once by scripts\ghidra\p5_apply.bat: b3fa/b3fb/b3fc at 0x8000, b3b4 at 0xC000, b377 at 0xE000 (names.txt `bank:0xADDR` -> block b<bank>). Never re-run it (AddBlock fails if blocks exist).
- Re-apply names + re-dump: scripts\ghidra\p5_reapply.bat (ApplySH.java, then DumpAll.java -readOnly).
- Decompiled C: decomp\<block>.c, one file per block, every function with its names.txt description as a comment. First dump: RAM 733 fns (12 failed), b377 114, b3b4 116 (2 failed), b3fa 202, b3fb 278, b3fc 279; 43 FUN_ left (naming pass -> work\p5\names_fun.txt).
- 3fa second pass: +122 names (names.txt 2099 lines). Enemy speeds/timers table for bank 3fa: work\p5\numbers_3fa.md (80BA walk table and 80E4/8102 timers byte-checked; rows marked GUESS not). Fix: 3fa 8643/86AC/86B4 are enemy_c_alt states 1/4/5 (armed table 85BA has 24 entries, alt table 85EA follows it).
- Unnamed-function pass (work\p5\names_fun.txt): of the 43 FUN_, 22 were data (FF padding, sound/tile/player tables, operand bytes) and are now labels (ApplySH removes a function at a "data" line); 20 are mid-function entries named after the parent; F57E = bare RTS. names.txt 2142 lines.
- Final dump (10-10): ApplySH funcs=1801 labels=341; DumpAll ok=1798 failed=3: RAM 692, b377 114, b3b4 116, b3fa 322, b3fb 278, b3fc 279; **0 FUN_ left**. Failures: b3b4 C281 test_menu_step + CBFC test_page_sound_test (computed jump tables), D9E9 kernel_sub_start. Ghidra 6809 "Unable to resolve constructor" at C005, C12A-C1AF (IRQ), E6FC, E8A2, E9AB, F5E9, B3B4: odd opcodes there; read those in the Python disassembly.

## Phase 6: emulator past attract (10-10)
- Cause of the old stall: the SUB CPU drives the state machine (it advances shared $2B in RAM bank 0x180 during state 0 / title), and main E17C skips the state handler while $41 or $43 (sub screen effects) are set. Fix: scripts\shdual.py runs main + sub 6809 together (sub starts at 377:E00B, win7=0x377, both Mach share one RAM dict, IRQ to both every 6000 steps). ~19-23 frames/s in Python.
- Inputs: coin/service port $302A (bank 17F off 0x102A): idle 0x18 (other bits active high = test etc; 0xFF blocks boot), pulse 0x08 for 4 frames = 1 credit ($3E=1). P1 port $3026 (0x1026): bit7 start, bit4 attack (active high; FA = raw held).
- Sequence (scripts\p6_play.py / p6_watch.py): state 0 -> title (1,2) at f103; coin f110; start f140 -> state 3 (game) f161; intro substate $2C=39 (F642) waits button or $31 timer (~0x2D0 f); button f300 -> round 1 ($65=1), $2C=10 by f519.
- $2C=10 (F1D7) IS gameplay (F208 chain gated on DP $08==0); enemies spawn by scroll. Save: work\p6/round1.pkl (scripts\p6_mksave.py). P1 port bits (active high): 0 right, 1 left, 2 down, 3 up, 4 attack, 5 jump, 7 start.
- Tools: scripts\p6_trace.py "a-b:hex,..." frames out.csv (P1 per frame); scripts\p6_enemies.py frames out.csv [hold] [punch_from] (all enemy slots per frame). CSVs in work\p6\ (walk_r, jump_tap, jump_hold, punch, walk_far, enemies, enemies_punch).
- Field fix: P1 +0x19..1B is HEIGHT (changes in jumps), +0x16..18 is depth; +0x0E is vertical speed.

### Phase 6 MEASURED values (RAM, round 1, 10-10)
- Walk: accel 0.125 px/f per frame, cap 1.375 px/f (reached after 11 f). Stop: decel 0.125/f.
- Jump: launch vy -4.25 px/f. Held: gravity 0.15625 (5/32) per frame, airtime 56 f, apex ~60 px. Tapped: after release gravity 0.25 per frame, airtime 36 f, apex ~40 px. Landing resets vy to 1.25 (ground value). State 0xF while airborne; anim 0..3 = rise/rise/fall/fall.
- Punch (standing): state 5, 20 f total (+5 counts 20->1), no movement; then idle. One punch kills round-1 enemies (hp 1 -> 0). Hit landed with enemy x ~56 px ahead of P1 x (reach estimate, one sample).
- Player hurt (contact): -1 hp (4 -> 3). State 0x12 for 16 f: knockback vx -1.0 (away), hop vy -2.0 with gravity 0.25 (lands at 16 f). Then 60 f invulnerable (+1 counts 59 -> 0, act=2), can walk meanwhile. Contact again right when invuln ends = next hit.
- Death: hp 0 -> state 0x13 for 363 f, then 0x14 for 293 f, respawn with hp 4 and 60 f invuln.
- Enemies round 1 (+0x1C reads 1 for all): type 159 walks 1.25 px/f (first frame 1.375), type 158 0.875 (first 1.0), type 1 0.75 (first 0.875); types 76/78 sit in state 3 (vx 0, 40 f timer), 40/41 stand (vx 0). Spawn state 4 for 1 f. Death state 0x13 for 71 f then slot freed.
