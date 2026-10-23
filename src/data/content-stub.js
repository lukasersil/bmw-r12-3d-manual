// Fallback data used until data/content.js (full manual texts) is in place.
// Same shape as content.js. Specifications come from the BMW Group Archive fact sheet for the R 12.
export const SYSTEMS = [
  { id: 'engine', cz: 'Motor', en: 'Engine' },
  { id: 'drivetrain', cz: 'Převodovka a pohon', en: 'Gearbox & drive' },
  { id: 'chassis', cz: 'Podvozek', en: 'Chassis' },
  { id: 'controls', cz: 'Ovládání', en: 'Controls' },
  { id: 'electrics', cz: 'Elektro', en: 'Electrics' },
];

const P = (system, term, cz, en) => ({ system, term, cz: { title: cz, text: '', data: [], care: null }, en: { title: en, text: '', data: [], care: null }, sources: [], unverified: [] });

export const PARTS = {
  cylinders: P('engine', 'Zylinder und Zylinderköpfe', 'Válce a hlavy', 'Cylinders and heads'),
  carburettor: P('engine', 'Vergaser', 'Karburátor', 'Carburettor'),
  intake: P('engine', 'Ansaugrohr und Luftfilter', 'Sání a vzduchový filtr', 'Intake and air filter'),
  exhaust: P('engine', 'Auspuff', 'Výfuky', 'Exhaust'),
  crankcase: P('engine', 'Kurbelgehäuse', 'Kliková skříň', 'Crankcase'),
  ignition: P('engine', 'Unterbrecher und Zündkabel', 'Přerušovač a kabely zapalování', 'Contact breaker and HT leads'),
  generator: P('engine', 'Licht-Zünd-Magnet', 'Magneto', 'Lighting and ignition magneto'),
  sparkplugs: P('engine', 'Zündkerzen', 'Zapalovací svíčky', 'Spark plugs'),
  kickstarter: P('engine', 'Kickstarter', 'Nožní startér', 'Kickstarter'),
  clutch: P('drivetrain', 'Kupplung', 'Spojka', 'Clutch'),
  gearbox: P('drivetrain', 'Getriebe', 'Převodovka', 'Gearbox'),
  gearlever: P('drivetrain', 'Schalthebel mit Kulisse', 'Řadicí páka v kulise', 'Gear lever and gate'),
  driveshaft: P('drivetrain', 'Kardanwelle', 'Kardanová hřídel', 'Drive shaft'),
  reardrive: P('drivetrain', 'Hinterradantrieb', 'Zadní převod', 'Rear bevel drive'),
  frame: P('chassis', 'Pressstahlrahmen', 'Lisovaný rám', 'Pressed-steel frame'),
  fork: P('chassis', 'Teleskopgabel', 'Teleskopická vidlice', 'Telescopic fork'),
  steeringdamper: P('chassis', 'Lenkungsdämpfer', 'Tlumič řízení', 'Steering damper'),
  frontwheel: P('chassis', 'Vorderrad', 'Přední kolo', 'Front wheel'),
  rearwheel: P('chassis', 'Hinterrad', 'Zadní kolo', 'Rear wheel'),
  brakes: P('chassis', 'Trommelbremsen', 'Bubnové brzdy', 'Drum brakes'),
  fenders: P('chassis', 'Kotflügel', 'Blatníky', 'Mudguards'),
  stand: P('chassis', 'Klappständer', 'Stojany', 'Stands'),
  saddle: P('chassis', 'Sattel', 'Sedlo', 'Saddle'),
  tank: P('chassis', 'Kraftstoffbehälter', 'Nádrž', 'Fuel tank'),
  handlebar: P('controls', 'Lenker und Hebel', 'Řídítka a páky', 'Handlebar and levers'),
  throttle: P('controls', 'Gasdrehgriff', 'Plynová rukojeť', 'Throttle twist grip'),
  advance: P('controls', 'Zünddrehgriff', 'Rukojeť předstihu', 'Ignition twist grip'),
  footbrake: P('controls', 'Fußbremshebel', 'Nožní brzda', 'Foot brake'),
  killbutton: P('controls', 'Kurzschlussknopf', 'Zkratovací tlačítko', 'Short-circuit button'),
  headlamp: P('electrics', 'Scheinwerfer mit Tachometer', 'Světlomet a tachometr', 'Headlamp and speedometer'),
  battery: P('electrics', 'Batterie', 'Baterie', 'Battery'),
  taillight: P('electrics', 'Schlusslicht', 'Zadní světlo', 'Tail lamp'),
  horn: P('electrics', 'Signalhorn', 'Houkačka', 'Horn'),
};

export const LUBE = [];

const FS = 'Fact sheet BMW Group Archive';
const S = (cz, en, value_cz, value_en = value_cz) => ({ cz, en, value_cz, value_en, source: FS });
export const SPECS = [
  S('Výroba', 'Built', '1935–1942'),
  S('Vyrobeno', 'Units built', '36 000 ks', '36,000'),
  S('Motor', 'Engine', 'dvouválec boxer', 'flat twin'),
  S('Zdvihový objem', 'Displacement', '745 cm³', '745 cc'),
  S('Vrtání × zdvih', 'Bore × stroke', '78 × 78 mm'),
  S('Kompresní poměr', 'Compression ratio', '5,2 : 1', '5.2 : 1'),
  S('Výkon', 'Output', '18 k při 3400 ot./min', '18 hp at 3,400 rpm'),
  S('Karburátor', 'Carburettor', '1× SUM'),
  S('Mazání', 'Lubrication', 'tlakové, zubové čerpadlo', 'forced feed, gear pump'),
  S('Spojka', 'Clutch', 'dvoulamelová, suchá', 'two plates, dry'),
  S('Převodovka', 'Gearbox', '4 stupně, ruční řazení', '4 speeds, hand change'),
  S('Převodové poměry', 'Gear ratios', '3,18 / 2,06 / 1,42 / 1,09 : 1', '3.18 / 2.06 / 1.42 / 1.09 : 1'),
  S('Zadní převod', 'Final drive', '1 : 4,07 (14/57 zubů)', '1 : 4.07 (14/57 teeth)'),
  S('Vidlice', 'Front suspension', 'teleskopická, hydraulické tlumení', 'telescopic, hydraulic damping'),
  S('Zadní kolo', 'Rear suspension', 'bez odpružení', 'rigid'),
  S('Ráfky a pneu', 'Rims and tyres', '3 × 19", pneu 3,5 × 19"', '3 × 19", tyres 3.5 × 19"'),
  S('Brzdy', 'Brakes', 'bubnové Ø 200 mm vpředu i vzadu', '200 mm drums front and rear'),
  S('Délka × šířka × výška', 'Length × width × height', '2100 × 900 × 940 mm'),
  S('Rozvor', 'Wheelbase', '1380 mm'),
  S('Nádrž', 'Fuel tank', '14 l', '14 L'),
  S('Hmotnost s plnou nádrží', 'Weight, fully fuelled', '185 kg'),
  S('Nejvyšší rychlost', 'Top speed', '110 km/h'),
  S('Spotřeba', 'Fuel consumption', '3,5–4 l/100 km', '3.5–4 L/100 km'),
  S('Cena', 'Price', '1630 RM', 'RM 1,630'),
];

export const ABOUT = {
  cz: 'BMW R 12 se vyráběla v letech 1935 až 1942. Motor převzala z R 11, nový byl podvozek: BMW ji představilo jako první motocykl na světě s teleskopickou vidlicí s hydraulickým tlumením. Vzniklo 36 000 kusů, většinu koupila armáda a státní úřady. Byla to nejvyráběnější BMW před válkou.',
  en: 'BMW built the R 12 from 1935 to 1942. The engine came from the R 11; the running gear was new, and BMW presented it as the world’s first motorcycle with a hydraulically damped telescopic fork. 36,000 were made, most of them for the army and government agencies, which made it the most-produced pre-war BMW.',
  sources: [FS],
};

export const OPEN_QUESTIONS = [];
