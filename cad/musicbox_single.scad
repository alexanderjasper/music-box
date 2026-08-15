// Music Box — single-speaker enclosure
// ====================================
// Parts: shell (body, Pi + breadboard mounts), faceplate (controls, PN532, card
// magnet), card (NTAG215 + magnet), knob, plus two printing aids — the fit-test
// coupon and the label tray. Controls per hardware/BOM.md: room toggle (DSQ14
// latching), 3 momentary transport buttons, KY-040 encoder, KY-006 buzzer.
//
// This is the only file to open or render. The model is split across:
//   params.scad      every dimension, the derived values and the sanity checks
//   util.scad        rounded boxes and the hole-position tables
//   icons.scad       the engraved panel glyphs
//   shell.scad       faceplate.scad  card.scad  knob.scad  jigs.scad
//   storage.scad     the box the cards live in when they are not on the plate
//
// Print: 0.2 mm layers, 3 perimeters, PLA/PETG, no supports, one part at a time.
// Shell floor-down, tray pockets-up, storage box opening-up (the trough's ends
// lean out 20 degrees, so they carry themselves). Faceplate, card and knob print
// TOP FACE DOWN and come out of the part switch already flipped for the bed.
// Nothing metal-filled: the PN532 reads through the plate. A filament change at
// 0.6 mm colours only the engraved icons.
//
// Assembly: brass inserts into the shell posts. Magnet up the plate's blind bore
// until it stops, then glue (every card's magnet faces the opposite pole).
// Switches in from the top, nuts from inside; encoder from below, nut on top;
// PN532 on its two posts with M3x8; buzzer taped into its pocket; Pi onto the
// floor pegs. Wire per hardware/WIRING.md with ~10 cm slack so the plate lifts
// off with its controls. 6x M3x12 from the top.
//
// Dimensions marked (verify) come from listings, not from parts in hand — print
// part = "testfit" first and check them.

// What to render. Set it here, or override it from the command line with
//   OpenSCAD -o knob.stl -D 'part="knob"' musicbox_single.scad
// Deliberately NOT annotated for the Customizer: with that panel open, it takes
// ownership of these values and quietly renders its own instead of the file's.
part = "card";  // assembly | shell | faceplate | card | knob | testfit | tray | box

explode   = 0;       // assembly view: lift the stack apart, mm
section   = false;   // cut away everything right of section_x
section_x = 48;

$fa = 2;
$fs = 0.4;

include <params.scad>
include <util.scad>
include <icons.scad>
include <shell.scad>
include <faceplate.scad>
include <card.scad>
include <knob.scad>
include <jigs.scad>
include <storage.scad>

/* ============================================================= preview === */

module ghost_shell_parts() {
    color("green", 0.35) {
        translate([pi_pos[0] - pi_pcb[0] / 2, pi_pos[1] - pi_pcb[1] / 2,
                   floor_t + pi_standoff_h])
            cube([pi_pcb[0], pi_pcb[1], pi_pcb_t]);
        translate([pi_pos[0] - pi_pcb[0] / 2, pi_pos[1] + pi_pcb[1] / 2 - 5,
                   floor_t + pi_standoff_h + pi_pcb_t])
            cube([pi_pcb[0], 5, 11.5]);   // 40-pin header
    }
    color("white", 0.35)
        translate([bb_pos[0] - bb[0] / 2, bb_pos[1] - bb[1] / 2, floor_t]) cube(bb);
}

// in plate coordinates, so they travel with it when exploded
module ghost_plate_parts() {
    color("red", 0.35)
        translate([card_pos[0] - pn532_pcb[0] / 2, card_pos[1] - pn532_pcb[1] / 2,
                   -pn532_standoff - 1.6])
            cube([pn532_pcb[0], pn532_pcb[1], 1.6]);
    color("blue", 0.35) {
        for (p = [toggle_pos, prev_pos, play_pos, next_pos])
            translate([p[0], p[1], -btn_body_h])
                cylinder(d = btn_barrel, h = btn_body_h);
        translate([enc_pos[0] - enc_board[0] / 2, enc_pos[1] - enc_board[1] / 2,
                   -enc_board_h])
            cube([enc_board[0], enc_board[1], enc_board_h]);
        translate([buzz_pos[0] - buzz_pcb[0] / 2, buzz_pos[1] - buzz_pcb[1] / 2,
                   -(buzz_can_h - buzz_can_deep) - 1.6])
            cube([buzz_pcb[0], buzz_pcb[1], 1.6]);
    }
}

// The % on the dummies keeps them out of F6 and out of any exported STL.
module assembly() {
    shell();
    %ghost_shell_parts();
    translate([0, 0, shell_h + explode]) {
        faceplate();
        %ghost_plate_parts();
    }
    %translate([card_pos[0] - card_size[0] / 2, card_pos[1] - card_size[1] / 2,
                H + 2 * explode]) card();
    translate([enc_pos[0], enc_pos[1], H + knob_gap + 2 * explode]) knob();
}

module output() {
    if (part == "assembly") assembly();
    else if (part == "shell") shell();
    else if (part == "faceplate")
        translate([0, D, plate_t]) rotate([180, 0, 0]) faceplate();
    else if (part == "card")
        translate([0, card_size[1], card_t]) rotate([180, 0, 0]) card();
    else if (part == "knob")
        translate([0, 0, knob_h]) rotate([180, 0, 0]) knob();
    else if (part == "testfit")
        translate([0, 50, plate_t]) rotate([180, 0, 0]) testfit();
    else if (part == "tray") label_tray();
    else if (part == "box") card_box();
    else echo("unknown part");
}

if (section)
    intersection() {
        output();
        translate([section_x - 400, -200, -200]) cube([400, 400, 400]);
    }
else
    output();
