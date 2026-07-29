// Shared geometry helpers and the hole-position tables.
include <params.scad>

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
