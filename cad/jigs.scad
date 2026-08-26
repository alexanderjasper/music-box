// Printing aids: the fit-test coupon and the label placement tray.
include <params.scad>
include <util.scad>
include <icons.scad>

// gauge the real ones. Stations: switch, encoder, insert boss, icon.

module testfit() {
    tf = [82, 32];
    y  = tf[1] / 2;
    difference() {
        union() {
            rbox_ch(tf[0], tf[1], plate_t, 5, chamfer);
            translate([74, y, -6]) cylinder(d = 2 * post_r, h = 6);
        }
        btn_hole([13, y]);

        translate([33, y, -1]) cylinder(d = enc_hole_d, h = plate_t + 2);

        // insert bore, in a boss of the same wall as the shell's posts
        translate([74, y, -6.01]) cylinder(d = insert_hole_d, h = insert_depth);

        engrave([20, tf[1] - 7]) icon_power(icon_size);
    }
}

/* ------------------------------------------------------------ label tray -- */

module label_tray() {
    cw = card_size[0] + 2 * tray_card_fit;
    cd = card_size[1] + 2 * tray_card_fit;
    lw = label_size[0] + 2 * tray_label_fit;
    ld = label_size[1] + 2 * tray_label_fit;
    ow = cw + 2 * tray_margin;
    od = cd + 2 * tray_margin;
    h  = tray_floor + tray_label_deep + tray_card_deep;
    difference() {
        rbox_ch(ow, od, h, corner_r, chamfer, up = false);

        // pocket the card drops into, guiding it square
        translate([(ow - cw) / 2, (od - cd) / 2, h - tray_card_deep])
            rbox(cw, cd, tray_card_deep + 1, card_r + tray_card_fit);

        // the sticker's own recess in that pocket's floor. Cut runs on up into
        // the pocket, which is already void — coincident faces render as a
        // membrane in preview.
        translate([(ow - lw) / 2, (od - ld) / 2, tray_floor])
            rbox(lw, ld, tray_label_deep + 0.5, 2);

        // fingernail slot through the pocket wall to the sticker's edge
        translate([(ow - tray_notch) / 2, (od - ld) / 2 - tray_margin - 1, tray_floor])
            cube([tray_notch, tray_margin + 2, h]);
    }
}
