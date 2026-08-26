// The printed NFC card: tag recess and the rim that drops into the faceplate's
// groove.
include <params.scad>
include <util.scad>

module card() {
    difference() {
        union() {
            // bottom face at z = 0; flipped for the bed in the part switch
            rbox_ch(card_size[0], card_size[1], card_t, card_r, card_ch);
            // rim, into the plate's groove. Both bottom edges are rounded over,
            // so the surface that meets the label of the card below is tangent to
            // the label's own plane — there is no arris anywhere to dig under it.
            translate([0, 0, -card_rim_h]) difference() {
                f  = card_rim_r;
                iw = card_size[0] - 2 * card_rim_w;
                id = card_size[1] - 2 * card_rim_w;
                ir = max(0.5, card_r - card_rim_w);
                union() {
                    rbox_profile(card_size[0], card_size[1], card_r, fillet_prof(f));
                    translate([0, 0, f])
                        rbox(card_size[0], card_size[1], card_rim_h - f, card_r);
                }
                translate([card_rim_w, card_rim_w, 0]) union() {
                    translate([-f, -f, -0.5]) rbox(iw + 2 * f, id + 2 * f, 0.5, ir + f);
                    rbox_profile(iw, id, ir, fillet_prof(f, sign = -1));
                    translate([0, 0, f]) rbox(iw, id, card_rim_h + 0.5 - f, ir);
                }
            }
        }
        translate([card_size[0] / 2, card_size[1] / 2, -0.5])
            cylinder(d = tag_d, h = tag_recess + 0.5);
    }
}
