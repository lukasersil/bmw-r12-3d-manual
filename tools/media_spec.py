# Crops for the period sources shown on the part cards.
# Handbook: BMW Instruction Book R 12 / R 17 (Munich 1936), page images from the PDF ("pg-NNN" = PDF page index
# from 0, printed page = index - 4; Fig. 1 and 2 are unnumbered fold-outs). Boxes are in page pixels.
# Commons: photos of surviving machines with author and licence; boxes in pixels of the downloaded file.
HB = 'Instruction Book R 12 / R 17, BMW 1936'
FIGS = {
  'f01': ('pg-008', (30, 190, 1570, 1060), 'Fig. 1', None, 'R 12 two-carburetter machine viewed from the off-side with lubrication chart'),
  'f03': ('pg-011', (120, 770, 835, 1140), 'Fig. 3', 7, 'Right end of handlebars (throttle twist grip)'),
  'f04': ('pg-012', (150, 110, 745, 1110), 'Fig. 4', 8, 'The controls on the BMW motor cycle'),
  'f05': ('pg-013', (150, 460, 735, 820), 'Fig. 5', 9, 'Left end of handlebars (ignition twist grip)'),
  'f06': ('pg-014', (120, 110, 748, 645), 'Fig. 6', 10, 'Gear change lever'),
  'f07': ('pg-020', (170, 105, 822, 605), 'Fig. 7', 16, 'Front wheel brake'),
  'f08': ('pg-020', (170, 665, 822, 1125), 'Fig. 8', 16, 'Rear wheel brake'),
  'f10': ('pg-023', (60, 100, 760, 740), 'Fig. 10', 19, 'Contact breaker of the lighting and ignition magneto'),
  'f11': ('pg-025', (140, 760, 640, 1130), 'Fig. 11', 21, 'Adjustment of the valve clearance of the touring machine'),
  'f14': ('pg-030', (80, 100, 830, 730), 'Fig. 14', 26, 'Sum carburetter for R 12 single carburetter engine'),
  'f17': ('pg-035', (230, 95, 765, 650), 'Fig. 17', 31, 'Two-plate friction clutch'),
  'f18': ('pg-037', (50, 90, 720, 1110), 'Fig. 18', 33, 'Power transmission'),
  'f19': ('pg-039', (150, 100, 805, 690), 'Fig. 19', 35, 'Headlight from above showing positions of the switch-key'),
  'f20': ('pg-040', (55, 90, 770, 635), 'Fig. 20', 36, 'Touring engine with partial cross section through the middle of the cylinder'),
  'f23': ('pg-044', (100, 95, 720, 590), 'Fig. 23', 40, 'Dismantling the front-wheel'),
  'f24': ('pg-045', (120, 95, 740, 590), 'Fig. 24', 41, 'Dismantling the rear wheel with solo machines'),
  'f25': ('pg-045', (80, 620, 720, 1115), 'Fig. 25', 41, 'Dismantling the rear wheel with sidecar machines'),
}
LS = ('Lothar Spurzem', 'CC BY-SA 2.0 DE', 'https://commons.wikimedia.org/wiki/File:BMW_R_12,_Baujahr_1940,_2006-07-16.jpg')
LS_M = ('Lothar Spurzem', 'CC BY-SA 2.0 DE', 'https://commons.wikimedia.org/wiki/File:2006-07-16_BMW_R_12_-_Motor.JPG')
TUX = ('Tux-Man', 'CC0', 'https://commons.wikimedia.org/wiki/File:BMW_R12.jpg')
ADD = ('Addvisor', 'CC BY-SA 4.0', 'https://commons.wikimedia.org/wiki/File:BMW_R12_(1940).jpg')
NIK = ('Nightflyer', 'CC BY-SA 4.0', 'https://commons.wikimedia.org/wiki/File:Schleswig-Holstein,_Wilster,_Zehnte_Internationale_VFV_ADAC_Zwei-Tage-Motorrad-Veteranen-Fahrt-Norddeutschland_und_33te_Int-Windmill-Rally_NIK_4083.jpg')
STK = ('Stahlkocher', 'CC BY-SA 3.0', 'https://commons.wikimedia.org/wiki/File:BMW_R_12_1936.jpg')
AKA = ('André Karwath (Aka)', 'CC BY-SA 2.5', 'https://commons.wikimedia.org/wiki/File:BMW_R_12_fork_(circa_1937).jpg')
BA = ('Bundesarchiv, Bild 183-H08684', 'CC BY-SA 3.0 DE', 'https://commons.wikimedia.org/wiki/File:Bundesarchiv_Bild_183-H08684,_Berlin,_Gesch%C3%A4ftsschluss.jpg')
PHOTOS = {
  # id: (file in the download folder, box or None, credit)
  'p_head': ('c7h.jpg', (1300, 950, 2150, 2080), NIK),
  'p_left': ('c0h.jpg', (980, 380, 1720, 960), TUX),
  'p_side': ('c0h.jpg', (0, 0, 2552, 1240), TUX),
  'p_tail': ('c0h.jpg', (1650, 700, 2552, 1130), TUX),
  'p_front': ('c1h.jpg', (0, 600, 1750, 2307), ADD),
  'p_tank': ('c3h.jpg', (1300, 250, 2900, 1300), LS),
  'p_rear': ('c3h.jpg', (0, 350, 1500, 1500), LS),
  'p_drive': ('c3h.jpg', (0, 1000, 1350, 2176), LS),
  'p_engine': ('r04.jpg', (900, 450, 3300, 2304), LS_M),
  'p_1936': ('r12_1936.jpg', None, STK),
  'p_fork': ('fork1937.jpg', None, AKA),
}
