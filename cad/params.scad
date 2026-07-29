// Every dimension for the Music Box, plus the derived values and the sanity
// checks that depend on them. Included by every other file.

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

/* ---------------------------------------------------------------- jigs --- */
// Drop-in tray for sticking labels on cards squarely: the sticker goes in the
// inner recess face-down (adhesive up), then the card is lowered into the outer
// pocket, whose walls guide it. The card is symmetric, so whichever way the
// sticker lands defines which way is up — no orientation to get wrong.
//
// The catch: the recess has to be SHALLOWER than the sticker, or the card lands
// on the tray floor and never touches the adhesive. One printed layer is 0.2, so
// this only works for stickers of about 0.3 mm and up. Measure yours.

label_size      = [60, 60];
label_t         = 0.3;    // sticker thickness incl. adhesive (verify)
tray_label_fit  = 0.3;    // around the sticker, per side
tray_card_fit   = 0.4;    // around the card, per side
tray_card_deep  = 2.5;    // card stands proud of this, so it lifts out by hand
tray_floor      = 1.6;
tray_margin     = 6;      // rim around the card pocket
tray_notch      = 14;     // slot to get a fingernail under a misplaced sticker

tray_label_deep = max(0.2, label_t - 0.1);
if (tray_label_deep >= label_t)
    echo(str("WARNING: label recess ", tray_label_deep, " is not shallower than a ",
             label_t, " mm sticker — the card would land on the tray, not the ",
             "sticker. Use the window-frame jig for stickers this thin."));
