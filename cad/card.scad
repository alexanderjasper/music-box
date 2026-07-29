// The printed NFC card: tag recess, buried magnet, and the rim that drops into
// the faceplate's groove.
include <params.scad>
include <util.scad>

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
