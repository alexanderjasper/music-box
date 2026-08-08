// The printed NFC card: tag recess, buried magnet, and the rim that drops into
// the faceplate's groove.
include <params.scad>
include <util.scad>

module card() {
    difference() {
        union() {
            // bottom face at z = 0; flipped for the bed in the part switch
            rbox_ch(card_size[0], card_size[1], card_t, card_r, card_ch);
            // rim, into the plate's groove — chamfered on both bottom edges so it
            // rides over the label of the card below instead of catching it
            translate([0, 0, -card_rim_h]) difference() {
                rbox_ch(card_size[0], card_size[1], card_rim_h, card_r,
                        card_rim_ch, up = false);
                iw = card_size[0] - 2 * card_rim_w;
                id = card_size[1] - 2 * card_rim_w;
                ir = max(0.5, card_r - card_rim_w);
                ch = card_rim_ch;
                union() {
                    // widened at the very bottom and hulled to a *thin* slice at
                    // the top of the chamfer band — hull to the full-height wall
                    // instead and the convex hull tapers the entire rim
                    hull() {
                        translate([card_rim_w - ch, card_rim_w - ch, -0.5])
                            rbox(iw + 2 * ch, id + 2 * ch, 0.5, ir + ch);
                        translate([card_rim_w, card_rim_w, ch])
                            rbox(iw, id, 0.01, ir);
                    }
                    translate([card_rim_w, card_rim_w, ch])
                        rbox(iw, id, card_rim_h + 0.5 - ch, ir);
                }
            }
        }
        translate([card_size[0] / 2, card_size[1] / 2, -0.5])
            cylinder(d = tag_d, h = tag_recess + 0.5);
        translate([card_size[0] / 2, card_size[1] / 2, tag_recess])
            cylinder(d = magnet_d + magnet_fit, h = card_t - tag_recess - card_mag_gap);
    }
}
