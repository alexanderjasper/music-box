// The engraved panel glyphs. Each is centred on its own bounding box, so
// engraving one at a position puts it visually centred there. s = its size.
include <params.scad>

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
