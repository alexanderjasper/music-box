// The card storage box: a one-card-wide trough, square outside, sloped within.
include <params.scad>
include <util.scad>

// Interior length at height z. The trough narrows towards the floor, so the
// stack can fan back against the ends.
function box_inner(z) = box_len - 2 * box_wall - 2 * (box_h - z) * tan(box_slope);

module card_box() {
    module slice(z) {
        l = box_inner(z);
        translate([(box_len - l) / 2, box_wall, z])
            rbox(l, box_w - 2 * box_wall, 0.01, max(0.5, box_r - box_wall));
    }

    difference() {
        // chamfered top and bottom both: one box for each, intersected
        intersection() {
            rbox_ch(box_len, box_w, box_h, box_r, box_ch, up = false);
            rbox_ch(box_len, box_w, box_h, box_r, box_ch, up = true);
        }

        // open at the top, so the slope runs on past the rim
        hull() { slice(box_floor); slice(box_h + 12); }
    }
}
