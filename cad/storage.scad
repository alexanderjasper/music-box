// The card storage box: a one-card-wide trough with outward-sloping ends.
include <params.scad>
include <util.scad>

// Half-length of the outer wall at height z. The ends lean out, so this grows.
function box_half(z) = box_len / 2 - (box_h - z) * tan(box_slope);

module card_box() {
    // measured perpendicular to the sloping wall, so the end is box_wall thick
    wx = box_wall / cos(box_slope);

    // a horizontal slice of the outline, inset by ix along the box and iy across
    // it (they differ for the walls: the ends lean, the sides don't)
    module slice(z, ix = 0, iy = -1) {
        y = iy < 0 ? ix : iy;
        l = 2 * box_half(z) - 2 * ix;
        translate([box_len / 2 - l / 2, y, z])
            rbox(l, box_w - 2 * y, 0.01, max(0.5, box_r - min(ix, y)));
    }

    difference() {
        // two hulls rather than one: hulling the chamfer slice straight to the
        // rim would blend the chamfer into the whole wall instead of ending it
        union() {
            hull() { slice(0, box_ch); slice(box_ch); }
            hull() { slice(box_ch); slice(box_h); }
        }

        // the trough, its ends parallel to the outside, open at the top
        hull() {
            slice(box_floor, wx, box_wall);
            slice(box_h + 12, wx, box_wall);
        }

        // finger notch in each side, round-bottomed so there is no corner to
        // start a crack and nothing unsupported to print
        r = box_notch_w / 2;
        translate([box_len / 2, -1, box_h - box_notch_d + r]) {
            rotate([-90, 0, 0]) cylinder(r = r, h = box_w + 2);
            translate([-r, 0, 0]) cube([box_notch_w, box_w + 2, box_h]);
        }
    }
}
