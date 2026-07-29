// The volume knob. Presses onto the encoder's D-shaft; prints top-face down.
include <params.scad>

module knob() {
    difference() {
        union() {
            cylinder(d = knob_d, h = knob_h - knob_ch);
            translate([0, 0, knob_h - knob_ch])
                cylinder(d1 = knob_d, d2 = knob_d - 2 * knob_ch, h = knob_ch);
        }
        // finger flutes round the rim
        for (i = [0 : knob_flutes - 1]) rotate([0, 0, i * 360 / knob_flutes])
            translate([knob_d / 2, 0, -1]) cylinder(d = knob_flute_d, h = knob_h + 2);

        // recess that hides the encoder's nut
        translate([0, 0, -0.01]) cylinder(d = knob_nut_d, h = knob_nut_h);

        // Shaft bore: D-shaped the whole way, starting where the shaft's flat does.
        // The flat is what stops the knob slipping.
        bd  = knob_shaft_d + knob_bore_fit;
        off = knob_shaft_flat > 0 ? knob_shaft_flat - bd / 2 : bd;
        // start it inside the recess rather than exactly at its floor: coincident
        // faces render as a membrane in preview and look like a solid floor
        z0 = max(0, knob_flat_z - 1);
        translate([0, 0, z0]) intersection() {
            cylinder(d = bd, h = knob_bore_h - z0);
            translate([-bd, -bd, -0.5])
                cube([2 * bd, bd + off, knob_bore_h - z0 + 1]);
        }

    }
}
