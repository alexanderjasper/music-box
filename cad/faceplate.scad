// The top plate: panel holes, the card groove, the PN532 posts, the buzzer
// pocket and fences, the screw counterbores and the engraved icons.
include <params.scad>
include <util.scad>
include <icons.scad>

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
