// The card storage box: a one-card-wide trough, square outside, sloped within.
include <params.scad>
include <util.scad>

// Interior length at height z. The trough narrows towards the floor, so the
// stack can fan back against the ends.
function box_inner(z) = box_len - 2 * box_wall - 2 * (box_h - z) * tan(box_slope);

// Flute centres, spaced as evenly as the run allows near box_flute_pitch.
function box_flute_x() =
    let (run = box_len - 2 * box_flute_end,
         n   = floor(run / box_flute_pitch))
    [for (i = [0 : n]) box_flute_end + i * run / n];

module card_box() {
    module slice(z) {
        l = box_inner(z);
        translate([(box_len - l) / 2, box_wall, z])
            rbox(l, box_w - 2 * box_wall, 0.01, max(0.5, box_r - box_wall));
    }

    // a capsule laid against the outside of a long wall, biting box_flute_d in.
    // Rounded ends, so the flute fades out rather than stopping at an edge.
    module flute(x, y) {
        hull() for (z = [box_flute_z, box_h - box_flute_z])
            translate([x, y, z]) sphere(r = box_flute_r);
    }

    difference() {
        // chamfered top and bottom both: one box for each, intersected
        intersection() {
            rbox_ch(box_len, box_w, box_h, box_r, box_ch, up = false);
            rbox_ch(box_len, box_w, box_h, box_r, box_ch, up = true);
        }

        // open at the top, so the slope runs on past the rim
        hull() { slice(box_floor); slice(box_h + 12); }

        off = box_flute_r - box_flute_d;
        for (x = box_flute_x()) {
            flute(x, -off);
            flute(x, box_w + off);
        }
    }
}
