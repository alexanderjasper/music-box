// The card storage box: a one-card-wide trough, square outside, sloped within.
include <params.scad>
include <util.scad>

// Interior length at height z. The trough narrows towards the floor, so the
// stack can fan back against the ends.
function box_inner(z) = box_len - 2 * box_wall - 2 * (box_h - z) * tan(box_slope);

module card_box() {
    // a thin horizontal slice of the trough, pulled in by `in` all round
    module slice(z, in = 0) {
        l = box_inner(z) - 2 * in;
        w = box_w - 2 * box_wall - 2 * in;
        translate([(box_len - l) / 2, box_wall + in, z])
            rbox(l, w, 0.01, max(0.5, box_r - box_wall - in));
    }

    // The trough, with the floor fillet cut in as a band of slices that close up
    // towards the floor. Pairwise hulls again — one hull over the lot would chord
    // straight across the curve.
    module trough() {
        hull() { slice(box_floor + box_ifil); slice(box_h + 12); }
        prof = fillet_prof(box_ifil);
        for (i = [0 : len(prof) - 2]) hull() for (j = [i, i + 1])
            slice(box_floor + prof[j][1], prof[j][0]);
    }

    difference() {
        // chamfered top and bottom both: one box for each, intersected
        intersection() {
            rbox_ch(box_len, box_w, box_h, box_r, box_ch, up = false);
            rbox_ch(box_len, box_w, box_h, box_r, box_ch, up = true);
        }

        // open at the top, so the slope runs on past the rim
        trough();
    }
}
