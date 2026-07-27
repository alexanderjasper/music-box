// Music Box — single-speaker enclosure
// ====================================
// Parts: shell (body, Pi + breadboard mounts), faceplate (controls, PN532, card
// magnet), card (NTAG215 + magnet). Controls per hardware/BOM.md: room toggle
// (DSQ14 latching), 3 momentary transport buttons, KY-040 encoder, KY-006 buzzer.
//
// Print: 0.2 mm layers, 3 perimeters, PLA/PETG, no supports, one part at a time.
// Shell floor-down. Faceplate and card print TOP FACE DOWN — both are already
// flipped for the bed. Nothing metal-filled: the PN532 reads through the plate.
// A filament change at 0.6 mm colours only the engraved icons.
//
// Assembly: brass inserts into the shell posts. Magnet up the plate's blind bore
// until it stops, then glue (every card's magnet faces the opposite pole).
// Switches in from the top, nuts from inside; encoder from below, nut on top;
// PN532 on its two posts with M3x8, buzzer taped
// into its pocket, Pi onto the floor pegs. Wire per hardware/WIRING.md with
// ~10 cm slack so the plate lifts off with its controls. 6x M3x12 from the top.
//
// Dimensions marked (verify) come from listings, not from parts in hand — print
// part = "testfit" first and check them.

// What to render. Set it here, or override it from the command line with
//   OpenSCAD -o knob.stl -D 'part="knob"' musicbox_single.scad
// Deliberately NOT annotated for the Customizer: with that panel open, it takes
// ownership of these values and quietly renders its own instead of the file's.
part = "knob";   // assembly | shell | faceplate | card | knob | testfit

explode   = 0;       // assembly view: lift the stack apart, mm
section   = false;   // cut away everything right of section_x
section_x = 48;

$fa = 2;
$fs = 0.4;

/* ---------------------------------------------------------------- box ---- */
// Width and depth are set by the 830-point breadboard (165 x 55) with the Pi
// behind it. The plate is as thin as the magnet bore and the card groove allow,
// which also leaves the controls' bushings enough thread and their nuts in the
// open — no pockets needed anywhere.

W          = 185;
D          = 118;
H          = 54;
corner_r   = 6;
chamfer    = 1.0;
wall       = 2.4;
floor_t    = 2.4;
plate_t    = 4.0;

shell_h    = H - plate_t;

lip_w      = 1.6;   // plate's locating lip
lip_h      = 3.0;
lip_clear  = 0.4;   // per side; 0.25 is too tight across 185 mm

/* ------------------------------------------------------------- screws ---- */
// M3 flat-head from the top into M3 brass heat-set inserts in the posts.

post_r        = 5.0;
post_inset    = wall + lip_w + post_r;   // keeps the lip ring clear of the posts
insert_hole_d = 4.6;   // for the M3 x 5 x 5.0 OD inserts on hand
insert_depth  = 5.5;
screw_hole_d  = 3.4;
screw_head_d  = 5.0;
screw_cb_deep = 2.0;   // 3 mm head, so it stands 1 mm proud; 0 = on the surface

/* ------------------------------------------------------------ buttons ---- */
// The switches mount from the front: square bezel on the top face, ø11.6 barrel
// through the hole, nut and washer tightened from inside. The encoder is the other
// way round — 12x12 base inside, nut on top. Bushings measure 7.5 and 7.0 long,
// threaded end to end, so a 4 mm plate leaves 3.5 and 3.0 mm — exactly nut (2) +
// washer (1.5) on the switches.

btn_hole_d = 11.8;   // ø11.6 bushing + 0.2
btn_barrel = 13.0;   // round body behind the plate, keep-out for the preview
btn_body_h = 30.0;   // bezel back to the terminals, wires included


/* ------------------------------------------------------------ encoder ---- */
// KY-040 breakout, EC11 with a bare 6 mm knurled shaft. Its 12x12 base sits flat
// against the plate's underside; the nut does the holding. The bushing measures
// ø6.8, not the nominal M7.

enc_hole_d   = 7.0;   // ø6.8 bushing + 0.2
enc_board    = [19, 26];   // keep-out for the preview
enc_board_h  = 20;

// A printed knob presses onto the shaft. Prints top-face down, so the bore and
// the nut recess open upward and nothing overhangs.
knob_d        = 18;     // over the ridges; the nut recess sets the lower limit
knob_ch       = 1.0;    // top-edge chamfer
knob_gap      = 0.5;    // knob underside to plate
knob_top      = 1.2;    // skin over the end of the shaft
knob_nut_d    = 12.5;   // recess that swallows the encoder's nut (verify: across
                        // corners, ~11.5 for a 10 mm across-flats nut)
knob_nut_min  = 3.5;    // depth the nut alone needs
knob_flutes   = 14;
knob_flute_d  = 2.4;

// Measured shaft: ø6, standing 15.5 above the plate, with the flat cut over the
// top 10 mm only. The bore can only grip where that flat is, so the nut recess is
// deepened to clear the round stretch and the D starts at the recess floor.
knob_shaft_up   = 15.5;
knob_shaft_d    = 6.0;
knob_shaft_flat = 4.5;   // thickness across the flat; 0 = a plain round shaft
knob_shaft_flat_len = 10;
knob_flat_margin = 0.5;  // start the D this far below where the flat should begin,
                         // so a slightly longer round stretch can't jam the knob
knob_bore_fit = 0.0;    // press fit, no glue: printed holes come out undersize
                        // anyway. Raise to 0.1 if it will not go on.

knob_bore_h  = knob_shaft_up - knob_gap;   // the shaft is fully swallowed
// The shaft is round below its flat, so the bore can't grip there. Rather than a
// useless round step in front of the D, the nut recess is deepened to clear that
// stretch — so the flat starts right at the recess floor.
knob_round_h = max(0, knob_bore_h - knob_shaft_flat_len);
knob_flat_z  = knob_round_h > 0 ? knob_round_h + knob_flat_margin : 0;
knob_nut_h   = max(knob_nut_min, knob_flat_z);
knob_h       = knob_bore_h + knob_top;

vol_mark_off  = 14;   // as engraved on the first plate — don't move it
if (knob_d / 2 > vol_mark_off - 3.0)
    echo(str("WARNING: a ø", knob_d, " knob overlaps the volume marks at ",
             vol_mark_off, " — max is ø", 2 * (vol_mark_off - 3.0)));
// the flutes are centred on the rim, so they cut half their diameter deep
knob_valley_r = knob_d / 2 - knob_flute_d / 2;
if (knob_valley_r - knob_nut_d / 2 < 1.2)
    echo(str("WARNING: only ", knob_valley_r - knob_nut_d / 2,
             " mm of wall between the flute valleys and the nut recess"));

/* --------------------------------------------------------- card / NFC ---- */
// The card's rim drops into a groove in the plate: it keeps a written title
// square, marks the spot when empty, and bridges in ~4 mm so the plate can print
// face down. The magnet holds the card down. The plate is NOT thinned here — PLA
// is transparent at 13.56 MHz, so only distance matters, and the tag ends up
// plate_t + pn532_standoff = 9 mm from the coil, well inside a PN532's range.

// If the rim ends up tight in the groove, shrink card_size rather than opening up
// the groove — the card is the cheap part to reprint.
card_seat_clear = 0.4;    // around the rim, per side
card_seat_h     = 2.2;    // groove depth
card_rim_w      = 3.0;
card_rim_h      = 2.0;

magnet_d      = 6.06;
magnet_h      = 2.04;
magnet_fit    = 0.25;
magnet_cover  = 1.2;      // plastic between magnet and top face

// Two mounting holes on a diagonal 38 mm apart, symmetric about the card spot so
// the antenna stays centred. If the diagonal isn't 45 deg, measure dx/dy between
// the holes and set the angle to atan2(dy, dx).
pn532_pcb        = [43, 41];   // (verify)
pn532_hole_span  = 37.5;
pn532_hole_angle = 45;
// Posts sized for an M3x8 self-tapping into PLA: 1.6 through the PCB leaves 6.4,
// and the pilot runs 1 mm into the plate so the tip can't bottom out. 2.8 pilot —
// 2.5 needs more torque than a printed post will take.
pn532_hole_d     = 2.8;
pn532_hole_deep  = 1.0;   // how far the pilot runs on into the plate
pn532_standoff   = 6.0;
pn532_post_r     = 3.5;

/* -------------------------------------------------------------- buzzer --- */
// The can drops into a pocket so its output sits right behind the grille, leaving
// 1 mm of plate for the holes. Two fences flank the PCB; tape or glue it.

buzz_pcb          = [19.2, 15.2];
buzz_can_d        = 13.4;         // ø13 can + fit
buzz_can_h        = 8.3;
buzz_can_deep     = 3.0;          // how far the can sinks into the plate
buzz_grille_d     = 1.8;
buzz_grille_pitch = 4.0;
buzz_grille_n     = 3;
buzz_fence        = [2, 12];

/* ---------------------------------------------------------------- feet --- */

foot_d     = 12;
foot_deep  = 0.5;
foot_inset = 16;

/* ----------------------------------------------------------- breadboard -- */
// Lies flat on the floor across the front, located by four corner ribs; it comes
// out again when the build moves to soldered wiring.

bb         = [165, 55, 9.5];
bb_pos     = [W / 2, 45];
bb_clear   = 0.6;
bb_rib_h   = 4.0;
bb_rib_t   = 2.0;
bb_rib_l   = 14;

/* ------------------------------------------------------------------ Pi --- */
// Drops onto printed pegs through its own mounting holes, with three snap clips.
// No hardware: M3 will not pass through the Pi's 2.75 mm holes. The clips flex
// 0.6 mm over ~7 mm, so they stay thin or PLA cracks. microSD needs the plate off.

pi_pcb        = [65, 30];
pi_holes      = [58, 23];
pi_pcb_t      = 1.6;
pi_standoff_h = 4.0;
pi_post_r     = 3.0;
pi_peg_d      = 2.5;   // Pi hole is 2.75; sand if it prints tight
pi_peg_h      = 3.2;
pi_clip_t     = 1.2;
pi_clip_w     = 9;
pi_clip_hook  = 0.6;
pi_clip_gap   = 0.4;
pi_pos        = [51, 95];   // rear left, behind the breadboard

port_slot_w   = 58;    // covers 4.5-62.5 mm along the Pi's rear edge
port_slot_h   = 12;
port_slot_x   = pi_pos[0] + 1;
port_slot_z   = floor_t + pi_standoff_h - 1.0;

/* --------------------------------------------------------------- cards --- */
// NTAG215 sticker in a recess on the underside, magnet buried below it, flat top
// face to write on. Both pockets load from the same side.

card_size    = [70, 70];
card_t       = 3.6;
card_r       = 8;
card_ch      = 0.8;
tag_d        = 25.5;   // 25 mm sticker + fit
tag_recess   = 0.4;    // 0.3 sticker + fit
card_mag_gap = 0.9;    // plastic over the card's magnet

/* -------------------------------------------------------------- layout --- */
// From the box's front-left corner.

toggle_pos = [106, 82];
enc_pos    = [156, 82];
prev_pos   = [106, 34];
play_pos   = [131, 34];
next_pos   = [156, 34];
card_pos   = [48, 62];
buzz_pos   = [48, 14];

engrave_d    = 0.6;
icon_size    = 9;
icon_tri_gap = 1.2;   // between the two triangles in << and >>
icon_offset  = 6.5;   // icon centre above the button's hole edge

// the switches hang deepest; they must clear the breadboard and its wiring
btn_clear   = (shell_h - btn_body_h) - (floor_t + bb[2]);
if (btn_clear < 5)
    echo(str("WARNING: only ", btn_clear,
             " mm between the switch backs and the breadboard — raise H by ",
             ceil(5 - btn_clear)));

magnet_bore = plate_t - magnet_cover;
if (magnet_bore < magnet_h)
    echo(str("WARNING: magnet bore is only ", magnet_bore, " mm for a ",
             magnet_h, " mm magnet"));

/* ================================================================ util === */

module rbox(w, d, h, r) {
    hull() for (x = [r, w - r], y = [r, d - r])
        translate([x, y, 0]) cylinder(r = r, h = h);
}

// rbox chamfered on its top (up = true) or bottom face
module rbox_ch(w, d, h, r, ch, up = true) {
    c = min(ch, h / 2);
    if (up) hull() {
        rbox(w, d, h - c, r);
        translate([c, c, h - c]) rbox(w - 2 * c, d - 2 * c, c, max(0.5, r - c));
    } else hull() {
        translate([c, c, 0]) rbox(w - 2 * c, d - 2 * c, c, max(0.5, r - c));
        translate([0, 0, c]) rbox(w, d, h - c, r);
    }
}

// four corners plus two mid-edge posts, so a wide plate can't bow
function post_pts() = concat([
    [post_inset,     post_inset],
    [W - post_inset, post_inset],
    [post_inset,     D - post_inset],
    [W - post_inset, D - post_inset],
], W > 150 ? [[W / 2, post_inset], [W / 2, D - post_inset]] : []);

function pi_hole_pts() = [
    for (dx = [-1, 1], dy = [-1, 1])
        [pi_pos[0] + dx * pi_holes[0] / 2, pi_pos[1] + dy * pi_holes[1] / 2]
];

function pn532_hole_pts() = [
    for (sgn = [-1, 1])
        [card_pos[0] + sgn * pn532_hole_span / 2 * cos(pn532_hole_angle),
         card_pos[1] + sgn * pn532_hole_span / 2 * sin(pn532_hole_angle)]
];

module bb_ribs() {
    x0 = bb_pos[0] - bb[0] / 2 - bb_clear;
    x1 = bb_pos[0] + bb[0] / 2 + bb_clear;
    y0 = bb_pos[1] - bb[1] / 2 - bb_clear;
    y1 = bb_pos[1] + bb[1] / 2 + bb_clear;
    for (sx = [0, 1], sy = [0, 1]) {
        translate([sx ? x1 - bb_rib_l : x0, sy ? y1 : y0 - bb_rib_t, floor_t - 0.01])
            cube([bb_rib_l, bb_rib_t, bb_rib_h]);
        translate([sx ? x1 : x0 - bb_rib_t, sy ? y1 - bb_rib_l : y0, floor_t - 0.01])
            cube([bb_rib_t, bb_rib_l, bb_rib_h]);
    }
}

/* =============================================================== shell === */

module shell() {
    difference() {
        rbox_ch(W, D, shell_h, corner_r, chamfer, up = false);

        translate([wall, wall, floor_t])
            rbox(W - 2 * wall, D - 2 * wall, shell_h, corner_r - wall);

        translate([port_slot_x - port_slot_w / 2, D - wall - 1, port_slot_z])
            cube([port_slot_w, wall + 2, port_slot_h]);

        // stick-on feet
        for (x = [foot_inset, W - foot_inset], y = [foot_inset, D - foot_inset])
            translate([x, y, -0.5]) cylinder(d = foot_d, h = foot_deep + 0.5);

        // floor vents, ahead of the breadboard
        for (dx = [-62, -48, -34, 34, 48, 62])
            translate([W / 2 + dx, 4.5, -1]) cube([3, 9, floor_t + 2]);
    }

    for (p = post_pts()) translate([p[0], p[1], floor_t]) difference() {
        union() {
            cylinder(r = post_r, h = shell_h - floor_t);
            cylinder(r1 = post_r + 2, r2 = post_r, h = 3);   // base fillet
        }
        translate([0, 0, shell_h - floor_t - insert_depth])
            cylinder(d = insert_hole_d, h = insert_depth + 0.1);
        translate([0, 0, shell_h - floor_t - insert_depth - 6])
            cylinder(d = screw_hole_d, h = 6.1);
    }

    bb_ribs();
    pi_mount();
}

// clip standing at a PCB edge; rot aims the hook inward
module pi_clip(x, y, rot) {
    zt = pi_standoff_h + pi_pcb_t;
    translate([x, y, floor_t]) rotate([0, 0, rot]) {
        translate([-pi_clip_w / 2, pi_clip_gap, 0])
            cube([pi_clip_w, pi_clip_t, zt + pi_clip_hook]);
        hull() {   // ledge over the PCB, sloping back into the post
            translate([-pi_clip_w / 2, pi_clip_gap - pi_clip_hook, zt])
                cube([pi_clip_w, pi_clip_hook + pi_clip_t, 0.8]);
            translate([-pi_clip_w / 2, pi_clip_gap, zt])
                cube([pi_clip_w, pi_clip_t, pi_clip_hook + 1.2]);
        }
    }
}

module pi_mount() {
    for (p = pi_hole_pts()) translate([p[0], p[1], floor_t - 0.01]) {
        cylinder(r = pi_post_r, h = pi_standoff_h);
        cylinder(d = pi_peg_d, h = pi_standoff_h + pi_peg_h - 0.6);
        translate([0, 0, pi_standoff_h + pi_peg_h - 0.6])
            cylinder(d1 = pi_peg_d, d2 = pi_peg_d - 1.0, h = 0.6);
    }
    // the left short edge stays clear for the microSD
    for (dx = [-20, 20])
        pi_clip(pi_pos[0] + dx, pi_pos[1] - pi_pcb[1] / 2, 180);
    pi_clip(pi_pos[0] + pi_pcb[0] / 2, pi_pos[1], 270);
}

/* =========================================================== faceplate === */

module lip() {
    difference() {
        translate([wall + lip_clear, wall + lip_clear, -lip_h])
            rbox(W - 2 * (wall + lip_clear), D - 2 * (wall + lip_clear),
                 lip_h, max(0.5, corner_r - wall - lip_clear));
        translate([wall + lip_clear + lip_w, wall + lip_clear + lip_w, -lip_h - 1])
            rbox(W - 2 * (wall + lip_clear + lip_w), D - 2 * (wall + lip_clear + lip_w),
                 lip_h + 2, max(0.5, corner_r - wall - lip_clear - lip_w));
        for (p = post_pts()) translate([p[0], p[1], -lip_h - 1])
            cylinder(r = post_r + 0.3, h = lip_h + 2);
    }
}

module btn_hole(pos) {
    translate([pos[0], pos[1], -1]) cylinder(d = btn_hole_d, h = plate_t + 2);
}

module enc_hole(pos) {
    translate([pos[0], pos[1], -1]) cylinder(d = enc_hole_d, h = plate_t + 2);
}

// channel the card's rim drops into
module card_groove() {
    ow = card_size[0] + 2 * card_seat_clear;
    od = card_size[1] + 2 * card_seat_clear;
    iw = card_size[0] - 2 * (card_rim_w + card_seat_clear);
    id = card_size[1] - 2 * (card_rim_w + card_seat_clear);
    translate([0, 0, plate_t - card_seat_h]) difference() {
        translate([card_pos[0] - ow / 2, card_pos[1] - od / 2, 0])
            rbox(ow, od, card_seat_h + 1, card_r + card_seat_clear);
        translate([card_pos[0] - iw / 2, card_pos[1] - id / 2, -0.5])
            rbox(iw, id, card_seat_h + 2,
                 max(0.5, card_r - card_rim_w - card_seat_clear));
    }
}

module faceplate() {
    difference() {
        union() {
            rbox_ch(W, D, plate_t, corner_r, chamfer);
            lip();
            for (p = pn532_hole_pts())
                translate([p[0], p[1], -pn532_standoff])
                    cylinder(r = pn532_post_r, h = pn532_standoff);
            fh = buzz_can_h - buzz_can_deep + 2.6;   // past the PCB
            for (sx = [-1, 1])
                translate([buzz_pos[0] + sx * (buzz_pcb[0] + 0.6 + buzz_fence[0]) / 2
                           - buzz_fence[0] / 2,
                           buzz_pos[1] - buzz_fence[1] / 2, -fh])
                    cube([buzz_fence[0], buzz_fence[1], fh]);
        }

        btn_hole(toggle_pos);
        btn_hole(prev_pos);
        btn_hole(play_pos);
        btn_hole(next_pos);
        enc_hole(enc_pos);

        card_groove();

        translate([card_pos[0], card_pos[1], -0.01])
            cylinder(d = magnet_d + magnet_fit, h = magnet_bore + 0.01);

        for (p = pn532_hole_pts())
            translate([p[0], p[1], -pn532_standoff - 0.01])
                cylinder(d = pn532_hole_d, h = pn532_standoff + pn532_hole_deep);

        translate([buzz_pos[0], buzz_pos[1], -0.5])
            cylinder(d = buzz_can_d, h = buzz_can_deep + 0.5);
        for (i = [0 : buzz_grille_n - 1], j = [0 : buzz_grille_n - 1])
            translate([buzz_pos[0] + (i - (buzz_grille_n - 1) / 2) * buzz_grille_pitch,
                       buzz_pos[1] + (j - (buzz_grille_n - 1) / 2) * buzz_grille_pitch,
                       -1])
                cylinder(d = buzz_grille_d, h = plate_t + 2);

        for (p = post_pts()) translate([p[0], p[1], 0]) {
            translate([0, 0, -1]) cylinder(d = screw_hole_d, h = plate_t + 2);
            if (screw_cb_deep > 0)
                translate([0, 0, plate_t - screw_cb_deep])
                    cylinder(d = screw_head_d + 0.4, h = screw_cb_deep + 1);
        }

        icons();
    }
}

/* =============================================================== icons === */
// Each icon is centred on its own bounding box; s is its width and height.

module tri(w, h) { polygon([[-w / 2, -h / 2], [-w / 2, h / 2], [w / 2, 0]]); }

module icon_next(s) {
    tw = 0.46 * s;
    for (dx = [-0.5, 0.5]) translate([dx * (tw + icon_tri_gap), 0]) tri(tw, s);
}
module icon_prev(s) { mirror([1, 0]) icon_next(s); }

module icon_play_pause(s) {
    tw = 0.46 * s;
    bw = 0.12 * s;
    g1 = 0.18 * s;
    g2 = 0.12 * s;
    x0 = -(tw + g1 + bw + g2 + bw) / 2;
    translate([x0 + tw / 2, 0]) tri(tw, s);
    for (i = [0, 1])
        translate([x0 + tw + g1 + bw / 2 + i * (bw + g2), 0])
            square([bw, s * 0.92], center = true);
}

// IEC power mark: broken circle with a bar through the gap
module icon_power(s) {
    r   = 0.34 * s;
    t   = 0.13 * s;
    top = r + t / 2 + 0.15 * s;   // how far the bar pokes past the circle
    bot = -0.04 * s;
    translate([0, (r + t / 2 - top) / 2]) {
        difference() {
            difference() {
                circle(r = r + t / 2);
                circle(r = r - t / 2);
            }
            translate([0, r]) square([3 * t, 3 * t], center = true);
        }
        translate([0, (bot + top) / 2]) square([t, top - bot], center = true);
    }
}

module icon_minus(s) { square([s, s * 0.22], center = true); }
module icon_plus(s)  { icon_minus(s); square([s * 0.22, s], center = true); }

module engrave(pos) {
    translate([pos[0], pos[1], plate_t - engrave_d])
        linear_extrude(engrave_d + 0.1) children();
}

module icons() {
    off = btn_hole_d / 2 + icon_offset;
    engrave([prev_pos[0], prev_pos[1] + off]) icon_prev(icon_size);
    engrave([play_pos[0], play_pos[1] + off]) icon_play_pause(icon_size);
    engrave([next_pos[0], next_pos[1] + off]) icon_next(icon_size);
    engrave([toggle_pos[0], toggle_pos[1] + off]) icon_power(icon_size);
    engrave([enc_pos[0] - vol_mark_off, enc_pos[1]]) icon_minus(5);
    engrave([enc_pos[0] + vol_mark_off, enc_pos[1]]) icon_plus(5);
}

/* ================================================================ knob === */

module knob() {
    difference() {
        union() {
            cylinder(d = knob_d, h = knob_h - knob_ch);
            translate([0, 0, knob_h - knob_ch])
                cylinder(d1 = knob_d, d2 = knob_d - 2 * knob_ch, h = knob_ch);
        }
        // finger flutes round the rim
        for (i = [0 : knob_flutes - 1]) rotate([0, 0, i * 360 / knob_flutes])
            translate([knob_d / 2, 0, -1]) cylinder(d = knob_flute_d, h = knob_h + 2);

        // recess that hides the encoder's nut
        translate([0, 0, -0.01]) cylinder(d = knob_nut_d, h = knob_nut_h);

        // Shaft bore: D-shaped the whole way, starting where the shaft's flat does.
        // The flat is what stops the knob slipping.
        bd  = knob_shaft_d + knob_bore_fit;
        off = knob_shaft_flat > 0 ? knob_shaft_flat - bd / 2 : bd;
        translate([0, 0, knob_flat_z]) intersection() {
            cylinder(d = bd, h = knob_bore_h - knob_flat_z);
            translate([-bd, -bd, -0.5])
                cube([2 * bd, bd + off, knob_bore_h - knob_flat_z + 1]);
        }

    }
}

/* ================================================================ card === */

module card() {
    difference() {
        union() {
            // bottom face at z = 0; flipped for the bed in the part switch
            rbox_ch(card_size[0], card_size[1], card_t, card_r, card_ch);
            difference() {   // rim, into the plate's groove
                translate([0, 0, -card_rim_h])
                    rbox(card_size[0], card_size[1], card_rim_h, card_r);
                translate([card_rim_w, card_rim_w, -card_rim_h - 0.5])
                    rbox(card_size[0] - 2 * card_rim_w, card_size[1] - 2 * card_rim_w,
                         card_rim_h + 1, max(0.5, card_r - card_rim_w));
            }
        }
        translate([card_size[0] / 2, card_size[1] / 2, -0.5])
            cylinder(d = tag_d, h = tag_recess + 0.5);
        translate([card_size[0] / 2, card_size[1] / 2, tag_recess])
            cylinder(d = magnet_d + magnet_fit, h = card_t - tag_recess - card_mag_gap);
    }
}

/* ============================================================= test fit === */
// Minimal coupon, printed in the plate's orientation so its holes and thickness
// gauge the real ones. Stations: switch, encoder, magnet, insert boss, icon.

module testfit() {
    tf = [82, 32];
    y  = tf[1] / 2;
    difference() {
        union() {
            rbox_ch(tf[0], tf[1], plate_t, 5, chamfer);
            translate([74, y, -6]) cylinder(d = 2 * post_r, h = 6);
        }
        btn_hole([13, y]);

        translate([33, y, -1]) cylinder(d = enc_hole_d, h = plate_t + 2);

        translate([55, y, -0.01])
            cylinder(d = magnet_d + magnet_fit, h = magnet_bore + 0.01);

        // insert bore, in a boss of the same wall as the shell's posts
        translate([74, y, -6.01]) cylinder(d = insert_hole_d, h = insert_depth);

        engrave([20, tf[1] - 7]) icon_power(icon_size);
    }
}

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
    else echo("unknown part");
}

if (section)
    intersection() {
        output();
        translate([section_x - 400, -200, -200]) cube([400, 400, 400]);
    }
else
    output();
