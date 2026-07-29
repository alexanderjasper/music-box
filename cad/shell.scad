// The box body: floor, walls, screw posts, breadboard ribs and the Pi mount.
include <params.scad>
include <util.scad>

module shell() {
    difference() {
        rbox_ch(W, D, shell_h, corner_r, chamfer, up = false);

        translate([wall, wall, floor_t])
            rbox(W - 2 * wall, D - 2 * wall, shell_h, corner_r - wall);

        translate([port_slot_x - port_slot_w / 2, D - wall - 1, port_slot_z])
            cube([port_slot_w, wall + 2, port_slot_h]);

        // stick-on feet
        for (x = [foot_inset, W - foot_inset], y = [foot_inset, D - foot_inset])
            translate([x, y, -0.5]) cylinder(d = foot_d, h = foot_deep + 0.5);

        // floor vents, ahead of the breadboard
        for (dx = [-62, -48, -34, 34, 48, 62])
            translate([W / 2 + dx, 4.5, -1]) cube([3, 9, floor_t + 2]);
    }

    for (p = post_pts()) translate([p[0], p[1], floor_t]) difference() {
        union() {
            cylinder(r = post_r, h = shell_h - floor_t);
            cylinder(r1 = post_r + 2, r2 = post_r, h = 3);   // base fillet
        }
        translate([0, 0, shell_h - floor_t - insert_depth])
            cylinder(d = insert_hole_d, h = insert_depth + 0.1);
        translate([0, 0, shell_h - floor_t - insert_depth - 6])
            cylinder(d = screw_hole_d, h = 6.1);
    }

    bb_ribs();
    pi_mount();
}

// clip standing at a PCB edge; rot aims the hook inward
module pi_clip(x, y, rot) {
    zt = pi_standoff_h + pi_pcb_t;
    translate([x, y, floor_t]) rotate([0, 0, rot]) {
        translate([-pi_clip_w / 2, pi_clip_gap, 0])
            cube([pi_clip_w, pi_clip_t, zt + pi_clip_hook]);
        hull() {   // ledge over the PCB, sloping back into the post
            translate([-pi_clip_w / 2, pi_clip_gap - pi_clip_hook, zt])
                cube([pi_clip_w, pi_clip_hook + pi_clip_t, 0.8]);
            translate([-pi_clip_w / 2, pi_clip_gap, zt])
                cube([pi_clip_w, pi_clip_t, pi_clip_hook + 1.2]);
        }
    }
}

module pi_mount() {
    for (p = pi_hole_pts()) translate([p[0], p[1], floor_t - 0.01]) {
        cylinder(r = pi_post_r, h = pi_standoff_h);
        cylinder(d = pi_peg_d, h = pi_standoff_h + pi_peg_h - 0.6);
        translate([0, 0, pi_standoff_h + pi_peg_h - 0.6])
            cylinder(d1 = pi_peg_d, d2 = pi_peg_d - 1.0, h = 0.6);
    }
    // the left short edge stays clear for the microSD
    for (dx = [-20, 20])
        pi_clip(pi_pos[0] + dx, pi_pos[1] - pi_pcb[1] / 2, 180);
    pi_clip(pi_pos[0] + pi_pcb[0] / 2, pi_pos[1], 270);
}
