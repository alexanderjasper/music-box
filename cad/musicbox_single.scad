// Music Box — single-speaker enclosure
// =====================================
// One room slot only: room toggle (latching), volume encoder, and
// previous / play-pause / next momentary buttons. Plus the NFC card spot,
// the piezo, the Pi Zero and the 830-point breadboard inside.
//
// Two printed parts, screwed together with M3 into brass heat-set inserts:
//   shell     — body + floor, standoffs for the Pi, corner screw posts
//   faceplate — top plate with all panel holes, hangs the PN532 under the
//               card spot, holds the card-holding magnet, engraved icons
//   card      — printed NFC tile: NTAG215 recess + magnet, prints top-face down
// No knob for now — the encoder's 6 mm knurled shaft is used bare.
//
// Parts match hardware/BOM.md:
//   Pi Zero WH · PN532 NFC module (V3) · KY-040 rotary encoder ·
//   DSQ14 14x14 latching switch (12 mm panel hole) ·
//   14x14 momentary push-buttons (12 mm panel hole) · KY-006 passive buzzer
//
// Inspecting it: open Window > Customizer for a dropdown of parts, an "explode"
// slider that lifts the stack apart, and a section cut. From the CLI, e.g.
//   OpenSCAD -o out.png -D 'part="assembly"' -D 'explode=45' musicbox_single.scad
//
// Dimensions marked (verify) are from datasheets/listings — measure your
// actual parts with calipers before printing the final version. Print the
// TEST FIT plate first (part = "testfit").
//
// Printing (Prusa Core One, 0.4 mm nozzle):
//   0.2 mm layers, 3 perimeters, 15–20 % infill, PLA/PETG.
//   One part at a time — each fits the bed on its own (rotate 90 deg), not side
//   by side. The shell prints floor-down.
//   Faceplate prints TOP FACE DOWN (part = "faceplate" is already flipped for
//   the bed): the visible face comes off the build plate glass-smooth, the NFC
//   membrane lands on the bed, and every pocket opens upward. That is why the
//   card seat is a ~4 mm groove rather than a full tray — it bridges cleanly,
//   whereas a tray's 71 mm floor would not. Card prints top-face down too.
//   Nothing conductive/metal-filled — the PN532 has to read through the plate.
//
// Assembly order: heat the six brass inserts into the shell's posts. Push the
// 6 x 2 mm magnet up the plate's blind bore until it stops, then glue it (watch
// the polarity — every card's magnet must face the opposite pole). Nuts on the
// buttons and encoder from the top, PN532 onto its two posts, buzzer taped behind
// its grille, Pi dropped onto the floor pegs, then wire per hardware/WIRING.md
// (single room slot) leaving ~10 cm of slack so the plate can be lifted off with
// its controls still attached. Finally 6x M3x12 up through the plate.
// The Pi needs no screws: it drops onto printed pegs and three snap clips
// (pi_mount = "pegs"); "screws" (M2.5) and "ziptie" are the alternatives.
// The card is located by a rim on its underside that drops into a matching
// groove in the 6 mm plate, and held down by the magnet (card_seat = "groove";
// "tray", "pocket" and "none" are alternatives — see the card seat section).
// The microSD is reached by unscrewing the faceplate — no side slot.

/* [View] */
// which part to render (Window > Customizer turns these into a dropdown/sliders)
part = "assembly";  // [assembly, shell, faceplate, card, print_all, testfit]
// assembly view: pull the stack apart to inspect it, mm (0 = closed up)
explode = 80;        // [0:1:80]
// cut everything to the right of section_x away, to look inside
section = false;    // [true, false]
// where the cut plane sits in x — 48 runs through the card spot and the magnet
section_x = 48;     // [0:1:185]

/* [Hidden] */
$fa = 2;
$fs = 0.4;

/* ---------------------------------------------------------------- box ---- */

// Sized so the 830-point breadboard (165 x 55 x 9.5) lies flat on the floor
// with the Pi behind it — see the "breadboard" section.
W          = 185;   // outer width  (x)
D          = 118;   // outer depth  (y)
H          = 48;    // outer height (z), incl. faceplate — +3 with the thicker
                    // plate, so the interior clearances stay as before
corner_r   = 6;     // outer corner radius
chamfer    = 1.0;   // chamfer on the plate's top edge and the shell's bottom edge
wall       = 2.4;   // side wall thickness
floor_t    = 2.4;   // floor thickness
// The plate is deliberately thick: the card's rim drops into a groove cut into it
// (see "card seat"), and the controls get local reliefs on the underside so their
// short bushings still reach through — see ctrl_plate_t.
plate_t    = 6.0;   // faceplate thickness

shell_h    = H - plate_t;

lip_w      = 1.6;   // faceplate locating lip: wall thickness
lip_h      = 3.0;   //                         how far it drops into the shell
lip_clear  = 0.4;   //  fit clearance per side — 0.25 is too tight across 185 mm

/* ------------------------------------------------------------- screws ---- */

// M3 flat-head screws up through the plate into M3 brass heat-set inserts in
// the posts. Flat heads, so the plate gets a straight counterbore — no conical
// seat. (For M4 inserts raise post_r to 6 and insert_hole_d to 5.6/depth 8.1.)
post_r        = 5.0;   // corner screw post radius (3 mm of wall around a M3 insert)
post_inset    = wall + lip_w + post_r;   // keeps the lip ring clear of the posts
insert_hole_d = 4.0;   // M3 heat-set insert bore (Ruthex/McMaster M3: 4.0 x 5.8)
insert_depth  = 6.0;
screw_hole_d  = 3.4;   // M3 clearance through the plate
screw_head_d  = 6.0;   // flat/pan head OD (verify yours)
screw_cb_deep = 1.2;   // straight counterbore, head sits nearly flush; 0 = none

/* ------------------------------------------------------------ buttons ---- */
// DSQ14 latching + 14x14 momentary share the same 12 mm threaded bushing.

btn_hole_d   = 12.0;  // panel hole for the 14x14 switches' bushing
btn_body     = 15.0;  // 14x14 body + clearance, for internal keep-out checks
btn_body_h   = 16.0;  // depth behind the panel incl. solder tails (verify)

// Their threaded bushings are only ~4.5 mm long, so the plate is milled back to
// ctrl_plate_t from underneath at every control. The relief is square and a
// touch larger than the switch body, so the body seats against that face and
// the nut still gets 1.5-2 mm of thread on the top side.
ctrl_plate_t = 2.6;   // plate left at the controls (verify against your bushings)
btn_relief   = 15.6;  // square relief for the 14x14 switch bodies
enc_relief   = 14.0;  // ditto for the EC11's 12.4 body

/* ------------------------------------------------------------ encoder ---- */
// KY-040 breakout carrying an EC11: M7 threaded bushing, 6 mm knurled D-shaft.

enc_hole_d      = 8.0;   // panel hole for the M7 bushing
// No dish on the top face any more — the underside relief (enc_relief) gives the
// nut its thread, so the plate stays clean around the bare shaft.
enc_recess_d    = 12;
enc_recess_deep = 0;
enc_board       = [19, 26];  // breakout PCB footprint, shaft roughly centred
enc_board_h     = 20;        // PCB + pin header depth behind the panel
// Most EC11s have a small locating lug on the mounting face; without a home for
// it the body can't sit flush. This pocket is cut in the relief floor, so it
// never shows on the top face — harmless if your encoder has no lug.
enc_locator       = true;
enc_locator_d     = 2.2;
enc_locator_off   = 5.6;     // lug centre distance from the shaft axis (verify)
enc_locator_angle = 90;      // which way it points (deg from +x) (verify)
enc_locator_deep  = 2.0;

/* --------------------------------------------------------- card / NFC ---- */

// The plate is hollowed from *underneath* so the PN532 reads through a thin
// membrane, leaving the top face free of any read-through feature. An engraved
// ring can mark the spot (card_ring_d), but the card seat below does that job.
card_ring_d    = 0;     // engraved "place card here" ring, outer dia (0 = none)
card_ring_w    = 1.6;   // ring line width

// ...instead the card drops into a seat cut into the plate, which keeps it
// square (a single round magnet alone lets the card spin) with nothing standing
// proud of the surface:
//   "groove" only the card's OUTLINE is cut, as a narrow channel that a matching
//            rim on the card's underside drops into. Bridges in ~4 mm, so the
//            plate can print FACE DOWN; the channel is also the spot marker
//   "tray"   full recess with flared walls — nicest to use, but its 71 mm floor
//            is a huge bridge, so the plate must print face UP
//   "pocket" same recess with straight walls
//   "none"   bare flat plate, card free to slide and rotate
card_seat       = "groove";  // [groove, tray, pocket, none]
card_seat_clear = 0.4;       // gap around the card, per side
card_seat_h     = 2.2;       // groove depth / how deep the card sinks in a tray
card_seat_flare = 2.0;       // tray only: how much wider the mouth is, per side
card_rim_w      = 3.0;       // "groove": width of the card's locating rim
card_rim_h      = 2.0;       // "groove": how far that rim stands proud
card_pocket_d  = 42;    // underside pocket over the PN532 antenna coil
card_membrane  = 1.2;   // plate left above the pocket — the NFC read path

// A neodymium disc sits in the plate's centre, inside both antenna coils, so a
// card with a matching magnet snaps down onto the spot. It lives in a blind bore
// from the underside — nothing shows on the top face.
magnet_d       = 6;      // disc diameter
magnet_h       = 2;      // disc thickness
magnet_fit     = 0.25;   // pocket clearance per diameter (press fit + a drop of CA)
magnet_cover   = 1.2;    // plastic left between the magnet and the tray floor —
                         // push the disc up the bore until it stops, then glue
magnet_boss_d  = magnet_d + 8;   // solid centre column through the NFC relief
magnet_boss_h  = 0;      // only needed if you thin the plate below ~4 mm

// The module has just TWO mounting holes, on a diagonal, 38 mm apart. Both posts
// sit symmetrically about the card spot, so the antenna stays centred on it. If
// the diagonal isn't at 45 deg on your board, measure dx/dy between the holes and
// set the angle to atan2(dy, dx).
pn532_pcb        = [43, 41];   // module outline (verify)
pn532_hole_span  = 38;         // centre-to-centre between the two holes
pn532_hole_angle = 45;         // direction of that diagonal, deg from +x
pn532_hole_d     = 2.5;        // pilot for an M3 self-tapper; use 2.2 for M2.5
                               // (check the board's own holes clear the screw)
pn532_standoff   = 3.0;        // gap between plate underside and the PCB
pn532_post_r     = 3.0;

/* --------------------------------------------------------------- buzzer -- */

// Grille in the plate ahead of the transport row. A pocket behind it takes the
// depth out of the holes (6 mm of ø1.8 hole would muffle the buzzer badly) and
// gives the KY-006 module a nest to be taped into.
buzz_grille_d     = 1.8;
buzz_grille_pitch = 4.0;
buzz_grille_nx    = 5;
buzz_grille_ny    = 2;
buzz_relief       = [24, 11];   // pocket behind the grille (keeps clear of the seat)
buzz_grille_t     = 2.0;        // plate left for the holes to pass through

/* --------------------------------------------------------------- feet ----- */
// Shallow recesses on the underside for stick-on rubber feet, so the box does not
// slide and the floor vents stay clear of the table.
feet       = true;
foot_d     = 12;
foot_deep  = 0.5;
foot_inset = 16;

/* ----------------------------------------------------------- breadboard --- */
// 830-point breadboard, lying flat on the floor across the front. Four L-shaped
// corner ribs locate it (its adhesive backing is optional — it comes out again
// when the build moves to soldered wiring).

bb          = [165, 55, 9.5];
bb_pos      = [W / 2, 45];     // outline centre in plan
bb_clear    = 0.6;             // slip fit inside the ribs
bb_rib_h    = 4.0;
bb_rib_t    = 2.0;
bb_rib_l    = 14;              // rib leg length
bb_ribs_on  = true;

/* ------------------------------------------------------------------ Pi --- */
// Pi Zero: 65 x 30 PCB, mounting holes 58 x 23 apart, ports along the rear
// long edge. microSD is reached by unscrewing the faceplate — no side slot.

// pi_mount picks how the board is held:
//   "pegs"   printed pegs through the Pi's mounting holes + 3 snap clips.
//            No hardware at all — the default, nothing to order.
//   "screws" plain standoffs with a pilot hole for M2.5 screws (the Pi's holes
//            are only 2.75 mm, so M3 will NOT pass — this needs M2.5).
//   "ziptie" plain standoffs + two pairs of floor slots for a cable tie.
pi_mount      = "pegs";

pi_pcb        = [65, 30];
pi_holes      = [58, 23];
pi_hole_d     = 2.2;      // "screws": pilot for M2.5 self-tapping
pi_standoff_h = 4.0;
pi_post_r     = 3.0;
pi_pcb_t      = 1.6;

pi_peg_d      = 2.5;      // Pi hole is 2.75 — sand the peg if it prints tight
pi_peg_h      = 3.2;      // above the standoff face: 1.6 PCB + 1.6 sticking out
// The clips are short cantilevers, so they have to flex 0.6 mm over ~7 mm of
// length — thin and with a small hook, or PLA cracks on the first insertion.
// The pegs alone already locate the board; set pi_clips = false to leave them off.
pi_clips      = true;
pi_clip_t     = 1.2;      // snap-clip cantilever thickness
pi_clip_w     = 9;        // width along the PCB edge
pi_clip_hook  = 0.6;      // how far the hook reaches in over the PCB
pi_clip_gap   = 0.4;      // clearance between clip and PCB edge
pi_pos        = [51, 95];  // PCB centre in plan — rear left, behind the breadboard

port_slot_w   = 54;       // one slot covering mini-HDMI + USB + PWR
port_slot_h   = 12;      // tall enough for a chunky micro-USB overmould
port_slot_x   = pi_pos[0] + 1;   // slot centre in x (ports sit 12–54 mm along the edge)
port_slot_z   = floor_t + pi_standoff_h - 1.0;

/* -------------------------------------------------------------- cards ---- */
// A printed tile: NTAG215 sticker in a recess on the underside, magnet buried
// below it, flat top face for a label / multi-material print. Everything loads
// from the same side, so print it TOP-FACE DOWN (part = "card" is already
// flipped for the bed).

card_size    = [70, 70];   // flat top face — room to write two lines of title
card_t       = 3.6;
card_r       = 8;          // corner radius
card_ch      = 0.8;        // top-edge chamfer
tag_d        = 25.5;       // NTAG215 sticker, 25 mm + fit
tag_recess   = 0.7;        // sticker + adhesive
card_mag_gap = 0.9;        // plastic between the card magnet and the card's top

/* ------------------------------------------------------------- layout ---- */
// Panel positions, measured from the box's front-left corner.

toggle_pos = [106, 82];
enc_pos    = [156, 82];
prev_pos   = [106, 34];
play_pos   = [131, 34];
next_pos   = [156, 34];
card_pos   = [48, 62];
buzz_pos   = [48, 20];

engrave_d    = 0.6;   // icon engraving depth
icon_size    = 9;     // icon width and height
icon_tri_gap = 1.2;   // gap between the two triangles in the << and >> icons
icon_offset  = 6.5;   // icon centre above its button's edge
// which glyph marks the room toggle:
//   "power"   IEC on/off mark — clearest "this is a toggle"
//   "cast"    dot with arcs fanning out — "send the music to this speaker"
//   "speaker" speaker cone with two waves — names the thing, not the action
//   "text"    engrave the room's name (toggle_text) — unambiguous on a 1-room box
toggle_icon  = "power";   // [power, cast, speaker, text]
toggle_text  = "ALRUM";

// a groove leaves the card sitting on the surface; a tray/pocket sinks it
seat_sink   = (card_seat == "tray" || card_seat == "pocket") ? card_seat_h : 0;
card_rim    = (card_seat == "groove");
magnet_bore = plate_t - seat_sink + magnet_boss_h - magnet_cover;
if (magnet_bore < magnet_h)
    echo(str("WARNING: magnet bore is only ", magnet_bore,
             " mm deep for a ", magnet_h, " mm magnet — thicken the plate, ",
             "reduce magnet_cover, or add magnet_boss_h"));

/* ================================================================ util === */

module rbox(w, d, h, r) {
    hull() for (x = [r, w - r], y = [r, d - r])
        translate([x, y, 0]) cylinder(r = r, h = h);
}

// rbox with a chamfer on the top (up = true) or bottom face.
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

// Screw post centres: four corners, plus two mid-edge posts on a wide plate so
// a 3 mm faceplate can't bow when a button is pressed.
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

// L-shaped ribs at the breadboard's four corners.
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

// Post with a pilot hole, standing on z = base.
module boss(r, h, hole_d, base = 0) {
    translate([0, 0, base]) difference() {
        cylinder(r = r, h = h);
        translate([0, 0, -0.1]) cylinder(d = hole_d, h = h + 0.2);
    }
}

/* =============================================================== shell === */

module shell() {
    difference() {
        rbox_ch(W, D, shell_h, corner_r, chamfer, up = false);

        // interior cavity
        translate([wall, wall, floor_t])
            rbox(W - 2 * wall, D - 2 * wall, shell_h, corner_r - wall);

        // rear wall: Pi port slot
        translate([port_slot_x - port_slot_w / 2, D - wall - 1, port_slot_z])
            cube([port_slot_w, wall + 2, port_slot_h]);

        // recesses for stick-on feet
        if (feet)
            for (x = [foot_inset, W - foot_inset], y = [foot_inset, D - foot_inset])
                translate([x, y, -0.5]) cylinder(d = foot_d, h = foot_deep + 0.5);

        // floor vents
        for (dx = [-62, -48, -34, 34, 48, 62])
            translate([W / 2 + dx, 4.5, -1]) cube([3, 9, floor_t + 2]);

        // cable-tie slots either side of the Pi
        if (pi_mount == "ziptie")
            for (dx = [-1, 1], dy = [-1, 1])
                translate([pi_pos[0] + dx * 24 - 1.5,
                           pi_pos[1] + dy * (pi_pcb[1] / 2 + 3) - 6, -1])
                    cube([3, 12, floor_t + 2]);
    }

    // corner screw posts — the faceplate lands on these
    for (p = post_pts()) translate([p[0], p[1], floor_t]) difference() {
        union() {
            cylinder(r = post_r, h = shell_h - floor_t);
            cylinder(r1 = post_r + 2, r2 = post_r, h = 3);   // base fillet
        }
        // brass insert bore at the top, screw-tip relief below it
        translate([0, 0, shell_h - floor_t - insert_depth])
            cylinder(d = insert_hole_d, h = insert_depth + 0.1);
        translate([0, 0, shell_h - floor_t - insert_depth - 6])
            cylinder(d = screw_hole_d, h = 6.1);
    }

    // breadboard corner ribs
    if (bb_ribs_on) bb_ribs();

    // Pi Zero mount
    pi_mount_parts();
}

/* ============================================================== Pi mount === */

// One snap clip standing at a PCB edge. rot aims the hook inward (+y local).
module pi_clip(x, y, rot) {
    zt = pi_standoff_h + pi_pcb_t;   // PCB top, relative to the floor surface
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

module pi_mount_parts() {
    for (p = pi_hole_pts()) translate([p[0], p[1], floor_t - 0.01]) {
        if (pi_mount == "pegs") {
            cylinder(r = pi_post_r, h = pi_standoff_h);
            cylinder(d = pi_peg_d, h = pi_standoff_h + pi_peg_h - 0.6);
            translate([0, 0, pi_standoff_h + pi_peg_h - 0.6])
                cylinder(d1 = pi_peg_d, d2 = pi_peg_d - 1.0, h = 0.6);
        } else {
            boss(pi_post_r, pi_standoff_h, pi_hole_d);
        }
    }

    if (pi_mount == "pegs" && pi_clips) {
        // two on the front long edge, one on the right short edge
        // (the left short edge stays clear for the microSD card)
        for (dx = [-20, 20])
            pi_clip(pi_pos[0] + dx, pi_pos[1] - pi_pcb[1] / 2, 180);
        pi_clip(pi_pos[0] + pi_pcb[0] / 2, pi_pos[1], 270);
    }
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
        // let the corner posts through
        for (p = post_pts()) translate([p[0], p[1], -lip_h - 1])
            cylinder(r = post_r + 0.3, h = lip_h + 2);
    }
}

module btn_hole(pos) {
    translate([pos[0], pos[1], -1]) cylinder(d = btn_hole_d, h = plate_t + 2);
}

module enc_hole(pos) {
    translate([pos[0], pos[1], -1]) cylinder(d = enc_hole_d, h = plate_t + 2);
    if (enc_recess_deep > 0)
        translate([pos[0], pos[1], plate_t - enc_recess_deep])
            cylinder(d = enc_recess_d, h = enc_recess_deep + 1);
    // blind pocket for the anti-rotation lug, up from the relief floor
    if (enc_locator)
        translate([pos[0] + enc_locator_off * cos(enc_locator_angle),
                   pos[1] + enc_locator_off * sin(enc_locator_angle),
                   plate_t - ctrl_plate_t])
            cylinder(d = enc_locator_d, h = enc_locator_deep);
}

module faceplate() {
    difference() {
        union() {
            rbox_ch(W, D, plate_t, corner_r, chamfer);
            lip();
            // optional boss under the magnet, for a thinner plate
            if (magnet_boss_h > 0)
                translate([card_pos[0], card_pos[1], -magnet_boss_h])
                    cylinder(d = magnet_boss_d, h = magnet_boss_h + 0.01);
            // PN532 hangs from two posts so it sits right under the card spot
            for (p = pn532_hole_pts()) translate([p[0], p[1], 0])
                mirror([0, 0, 1]) boss(pn532_post_r, pn532_standoff, pn532_hole_d);
        }

        // panel holes
        btn_hole(toggle_pos);
        btn_hole(prev_pos);
        btn_hole(play_pos);
        btn_hole(next_pos);
        enc_hole(enc_pos);

        // card spot: engraved ring on top (purely a marker — the magnet does the
        // locating, so card_ring_d = 0 leaves the top face completely flat)
        if (card_ring_d > 2 * card_ring_w)
            translate([card_pos[0], card_pos[1], plate_t - engrave_d]) difference() {
                cylinder(d = card_ring_d, h = engrave_d + 1);
                translate([0, 0, -0.5])
                    cylinder(d = card_ring_d - 2 * card_ring_w, h = engrave_d + 2);
            }
        if (card_seat == "groove") card_seat_groove();
        if (card_seat == "tray")   card_seat_cut(card_seat_flare);
        if (card_seat == "pocket") card_seat_cut(0);

        // local reliefs on the underside, so the controls' short bushings reach
        for (p = [toggle_pos, prev_pos, play_pos, next_pos])
            translate([p[0] - btn_relief / 2, p[1] - btn_relief / 2, -0.5])
                cube([btn_relief, btn_relief, plate_t - ctrl_plate_t + 0.5]);
        translate([enc_pos[0] - enc_relief / 2, enc_pos[1] - enc_relief / 2, -0.5])
            cube([enc_relief, enc_relief, plate_t - ctrl_plate_t + 0.5]);

        // thinning pocket underneath: a ring, so the centre column stays solid for
        // the magnet, interrupted where the two PN532 posts join the plate
        translate([card_pos[0], card_pos[1], -0.5]) difference() {
            cylinder(d = card_pocket_d,
                     h = max(0.1, plate_t - card_membrane - seat_sink) + 0.5);
            translate([0, 0, -0.5]) cylinder(d = magnet_boss_d, h = plate_t + 2);
            for (p = pn532_hole_pts())
                translate([p[0] - card_pos[0], p[1] - card_pos[1], -0.5])
                    cylinder(r = pn532_post_r + 0.8, h = plate_t + 2);
        }

        // magnet bore, loaded from underneath
        translate([card_pos[0], card_pos[1], -magnet_boss_h - 0.01])
            cylinder(d = magnet_d + magnet_fit, h = magnet_bore + 0.01);

        // pocket behind the grille
        translate([buzz_pos[0] - buzz_relief[0] / 2, buzz_pos[1] - buzz_relief[1] / 2,
                   -0.5])
            cube([buzz_relief[0], buzz_relief[1], plate_t - buzz_grille_t + 0.5]);

        // buzzer grille
        for (i = [0 : buzz_grille_nx - 1], j = [0 : buzz_grille_ny - 1])
            translate([buzz_pos[0] + (i - (buzz_grille_nx - 1) / 2) * buzz_grille_pitch,
                       buzz_pos[1] + (j - (buzz_grille_ny - 1) / 2) * buzz_grille_pitch,
                       -1])
                cylinder(d = buzz_grille_d, h = plate_t + 2);

        // screw holes with a flat counterbore for the flat heads
        for (p = post_pts()) translate([p[0], p[1], 0]) {
            translate([0, 0, -1]) cylinder(d = screw_hole_d, h = plate_t + 2);
            if (screw_cb_deep > 0)
                translate([0, 0, plate_t - screw_cb_deep])
                    cylinder(d = screw_head_d + 0.4, h = screw_cb_deep + 1);
        }

        icons();
    }
}

/* ============================================================ card seat === */

// The seat the card drops into. flare = 0 gives straight walls ("pocket"), any
// larger value slopes them outwards so the card self-centres on the way in.
// Channel following the card outline, for the card's rim to drop into.
module card_seat_groove() {
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

module card_seat_cut(flare) {
    fw = card_size[0] + 2 * card_seat_clear;   // floor
    fd = card_size[1] + 2 * card_seat_clear;
    fr = card_r + card_seat_clear;
    mw = fw + 2 * flare;                       // mouth
    md = fd + 2 * flare;
    mr = fr + flare;
    hull() {
        translate([card_pos[0] - fw / 2, card_pos[1] - fd / 2, plate_t - card_seat_h])
            rbox(fw, fd, 0.01, fr);
        translate([card_pos[0] - mw / 2, card_pos[1] - md / 2, plate_t])
            rbox(mw, md, 1, mr);
    }
}

/* =============================================================== icons === */

// Every icon is centred on its own bounding box, so engraving it at a position
// puts it visually centred there. s = the icon's nominal width and height.

// right-pointing triangle, centred on its bbox
module tri(w, h) { polygon([[-w / 2, -h / 2], [-w / 2, h / 2], [w / 2, 0]]); }

module icon_next(s) {
    tw = 0.46 * s;   // triangle width; icon_tri_gap separates the pair
    for (dx = [-0.5, 0.5]) translate([dx * (tw + icon_tri_gap), 0]) tri(tw, s);
}
module icon_prev(s) { mirror([1, 0]) icon_next(s); }

module icon_play_pause(s) {
    tw = 0.46 * s;   // triangle width
    bw = 0.12 * s;   // pause bar width
    g1 = 0.18 * s;   // triangle -> first bar
    g2 = 0.12 * s;   // bar -> bar
    total = tw + g1 + bw + g2 + bw;
    x0 = -total / 2;
    translate([x0 + tw / 2, 0]) tri(tw, s);
    for (i = [0, 1])
        translate([x0 + tw + g1 + bw / 2 + i * (bw + g2), 0])
            square([bw, s * 0.92], center = true);
}
// arc of thickness t, centred on the origin, spanning +/- half_angle around +x
module arc2d(r, t, half_angle) {
    intersection() {
        difference() {
            circle(r = r + t / 2);
            circle(r = r - t / 2);
        }
        x = (r + t) * 2;
        polygon([[0, 0], [x, x * tan(half_angle)], [x, -x * tan(half_angle)]]);
    }
}

// "cast": a source dot with arcs fanning out of it
module icon_cast(s) {
    translate([0, -0.38 * s]) {
        circle(d = 0.18 * s);
        for (r = [0.30, 0.52, 0.74]) rotate([0, 0, 90]) arc2d(r * s, 0.11 * s, 46);
    }
}

// speaker cone with two waves
module icon_speaker(s) {
    translate([-0.06 * s, 0]) {
        translate([-0.36 * s, 0]) square([0.28 * s, 0.45 * s], center = true);
        polygon([[-0.25 * s, -0.22 * s], [0.18 * s, -0.5 * s],
                 [ 0.18 * s,  0.5 * s], [-0.25 * s,  0.22 * s]]);
        translate([0.18 * s, 0])
            for (r = [0.28 * s, 0.46 * s]) arc2d(r, 0.1 * s, 42);
    }
}

// the room's name
module icon_label(s, txt) {
    text(txt, size = s * 0.72, halign = "center", valign = "center",
         font = "Liberation Sans:style=Bold");
}

// dispatcher for whichever glyph marks the toggle
module icon_toggle(s) {
    if (toggle_icon == "cast")         icon_cast(s);
    else if (toggle_icon == "speaker") icon_speaker(s);
    else if (toggle_icon == "text")    icon_label(s, toggle_text);
    else                               icon_power(s);
}

// IEC power symbol for the room toggle: broken circle with a bar through the gap
module icon_power(s) {
    r = 0.34 * s;
    t = 0.13 * s;
    bar = r + 0.42 * s;
    translate([0, -0.07 * s]) {
        difference() {
            difference() {
                circle(r = r + t / 2);
                circle(r = r - t / 2);
            }
            translate([0, r]) square([3 * t, 3 * t], center = true);
        }
        translate([0, bar / 2 - 0.05 * s]) square([t, bar], center = true);
    }
}
module icon_minus(s) { square([s, s * 0.22], center = true); }
module icon_plus(s)  { icon_minus(s); square([s * 0.22, s], center = true); }

module engrave(pos) {
    translate([pos[0], pos[1], plate_t - engrave_d])
        linear_extrude(engrave_d + 0.1) children();
}

module icons() {
    lbl = icon_size;
    off = btn_hole_d / 2 + icon_offset;   // icon centre above its button centre

    engrave([prev_pos[0], prev_pos[1] + off]) icon_prev(lbl);
    engrave([play_pos[0], play_pos[1] + off]) icon_play_pause(lbl);
    engrave([next_pos[0], next_pos[1] + off]) icon_next(lbl);
    engrave([toggle_pos[0], toggle_pos[1] + off]) icon_toggle(lbl);

    // volume direction marks flanking the encoder
    engrave([enc_pos[0] - 14, enc_pos[1]]) icon_minus(5);
    engrave([enc_pos[0] + 14, enc_pos[1]]) icon_plus(5);
}

/* ================================================================ card === */

module card() {
    difference() {
        union() {
            // modelled bottom-face-down; flipped for printing in the part switch
            rbox_ch(card_size[0], card_size[1], card_t, card_r, card_ch);
            // locating rim around the underside, dropping into the plate groove
            if (card_rim) difference() {
                translate([0, 0, -card_rim_h])
                    rbox(card_size[0], card_size[1], card_rim_h, card_r);
                translate([card_rim_w, card_rim_w, -card_rim_h - 0.5])
                    rbox(card_size[0] - 2 * card_rim_w, card_size[1] - 2 * card_rim_w,
                         card_rim_h + 1, max(0.5, card_r - card_rim_w));
            }
        }

        // NTAG215 sticker recess in the underside
        translate([card_size[0] / 2, card_size[1] / 2, -0.5])
            cylinder(d = tag_d, h = tag_recess + 0.5);

        // magnet, buried under the sticker
        translate([card_size[0] / 2, card_size[1] / 2, tag_recess])
            cylinder(d = magnet_d + magnet_fit, h = card_t - tag_recess - card_mag_gap);
    }
}

/* ============================================================= test fit === */
// Print this first (~15 min): it reproduces the plate stack around one button,
// the encoder and the card spot, so you can check that the bushings reach and
// their nuts grab, that the magnet holds a card, and that a tag still reads.

module testfit() {
    tf = [110, 50];
    difference() {
        rbox_ch(tf[0], tf[1], plate_t, 6, chamfer);

        // one switch: hole + underside relief
        translate([22, tf[1] / 2, -1]) cylinder(d = btn_hole_d, h = plate_t + 2);
        translate([22 - btn_relief / 2, (tf[1] - btn_relief) / 2, -0.5])
            cube([btn_relief, btn_relief, plate_t - ctrl_plate_t + 0.5]);

        // the encoder: hole + underside relief
        translate([54, tf[1] / 2, -1]) cylinder(d = enc_hole_d, h = plate_t + 2);
        translate([54 - enc_relief / 2, (tf[1] - enc_relief) / 2, -0.5])
            cube([enc_relief, enc_relief, plate_t - ctrl_plate_t + 0.5]);

        // card spot: a patch of tray floor, the NFC membrane and the magnet bore
        translate([88, tf[1] / 2, plate_t - seat_sink])
            cylinder(d = 34, h = seat_sink + 1);
        translate([88, tf[1] / 2, -0.5]) difference() {
            cylinder(d = 30, h = plate_t - card_membrane - seat_sink + 0.5);
            translate([0, 0, -0.5]) cylinder(d = magnet_boss_d, h = plate_t + 2);
        }
        translate([88, tf[1] / 2, -0.01])
            cylinder(d = magnet_d + magnet_fit, h = magnet_bore + 0.01);
    }
}

/* ============================================================= preview === */

// Components that live in the shell.
module ghost_shell_parts() {
    color("green", 0.35) {  // Pi
        translate([pi_pos[0] - pi_pcb[0] / 2, pi_pos[1] - pi_pcb[1] / 2,
                   floor_t + pi_standoff_h])
            cube([pi_pcb[0], pi_pcb[1], 1.6]);
        translate([pi_pos[0] - pi_pcb[0] / 2, pi_pos[1] + pi_pcb[1] / 2 - 5,
                   floor_t + pi_standoff_h + 1.6])
            cube([pi_pcb[0], 5, 11.5]);   // 40-pin header
    }
    color("white", 0.35)    // breadboard
        translate([bb_pos[0] - bb[0] / 2, bb_pos[1] - bb[1] / 2, floor_t])
            cube(bb);
}

// Components carried by the faceplate — drawn in its own coordinates, so they
// travel with it when the view is exploded.
module ghost_plate_parts() {
    color("red", 0.35)      // PN532
        translate([card_pos[0] - pn532_pcb[0] / 2, card_pos[1] - pn532_pcb[1] / 2,
                   -pn532_standoff - 1.6])
            cube([pn532_pcb[0], pn532_pcb[1], 1.6]);
    color("blue", 0.35) {   // switch bodies + encoder board
        for (p = [toggle_pos, prev_pos, play_pos, next_pos])
            translate([p[0] - btn_body / 2, p[1] - btn_body / 2, -btn_body_h])
                cube([btn_body, btn_body, btn_body_h]);
        translate([enc_pos[0] - enc_board[0] / 2, enc_pos[1] - enc_board[1] / 2,
                   -enc_board_h])
            cube([enc_board[0], enc_board[1], enc_board_h]);
    }
}

module assembly() {
    shell();
    ghost_shell_parts();
    translate([0, 0, shell_h + explode]) {
        faceplate();
        ghost_plate_parts();
    }
    color("orange", 0.5)   // a card resting on the spot
        translate([card_pos[0] - card_size[0] / 2, card_pos[1] - card_size[1] / 2,
                   H - seat_sink + 2 * explode])
            card();
}

module output() {
    if (part == "assembly") {
        assembly();
    } else if (part == "shell") {
        shell();
    } else if (part == "faceplate") {
        // bed-ready: top face down, so it comes off the plate glass-smooth
        translate([0, D, plate_t]) rotate([180, 0, 0]) faceplate();
    } else if (part == "card") {
        translate([0, card_size[1], card_t]) rotate([180, 0, 0]) card();  // print-ready
    } else if (part == "testfit") {
        testfit();
    } else if (part == "print_all") {
        shell();
        translate([0, 2 * D + 8, plate_t]) rotate([180, 0, 0]) faceplate();
        translate([W + 8, 0, card_t]) rotate([180, 0, 0]) card();
    } else {
        echo("unknown part");
    }
}

if (section)
    intersection() {
        output();
        translate([section_x - 400, -200, -200]) cube([400, 400, 400]);
    }
else
    output();
