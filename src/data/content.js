// BMW R 12 (1935–1942), civilní verze s jedním karburátorem SUM. Data pro interaktivní 3D manuál.
// Zdroje: fact sheet BMW Group Archive (BMW-R-12.pdf) a Instruction Book R 12 / R 17 (M 1089, 1936).
// Texty jsou vlastními slovy, čísla jsou fakta se zdrojem. Prameny: CREDITS.md
// Čísla z příručky ověřena okem proti vyrenderovaným stránkám 22. 10. 2026. `unverified` drží jen rozpory mezi zdroji.

import { DE_PARTS, DE_LUBE, DE_SPECS, DE_ABOUT } from './de.js';

const FS = 'Fact sheet BMW Group Archive';
const IB = 'Instruction Book R 12/R 17 (M 1089, 1936)';

export const SYSTEMS = [
  { id: 'engine', cz: 'Motor', en: 'Engine', de: 'Motor' },
  { id: 'drivetrain', cz: 'Převodovka a pohon', en: 'Gearbox & drive', de: 'Getriebe und Antrieb' },
  { id: 'chassis', cz: 'Podvozek', en: 'Chassis', de: 'Fahrwerk' },
  { id: 'controls', cz: 'Ovládání', en: 'Controls', de: 'Bedienung' },
  { id: 'electrics', cz: 'Elektro', en: 'Electrics', de: 'Elektrik' },
];

export const PARTS = {
  // ───────── MOTOR ─────────
  cylinders: {
    system: 'engine',
    term: 'Zylinder und Zylinderköpfe',
    cz: {
      title: 'Válce a hlavy',
      text: 'Dva protilehlé válce vyčnívají do stran z klikové skříně. Ventily jsou boční, uzavřené a ovládané zdvihátky od vačkového hřídele. Olej, který by u zdvihátek unikal, vede odpadní otvor zpět do skříně. Proto motor zvenku nepotí. Písty jsou z lehké slitiny a mají tři kroužky, ten nejspodnější stírá olej.',
      data: [
        ['Uspořádání', 'dvouválec boxer'],
        ['Vrtání × zdvih', '78 × 78 mm'],
        ['Zdvihový objem', '745 cm³'],
        ['Kompresní poměr', '5,2 : 1'],
        ['Výkon', '18 k při 3400 ot/min'],
      ],
      care: 'Mezeru ventilů kontrolujte jen za studena, má být zhruba 0,1 mm. Na ventilovou skříňku se dostanete sejmutím krytu. Matice hlav a sání dotahujte hlavně v prvních kilometrech.',
    },
    en: {
      title: 'Cylinders and heads',
      text: 'Two opposed cylinders stick out sideways from the crankcase. The valves are side-mounted, fully enclosed and driven by tappets from the camshaft. Oil that creeps past the tappets drains back into the case through a return bore, which keeps the engine clean on the outside. The pistons are light alloy with three rings, the lowest one scrapes oil.',
      data: [
        ['Layout', 'flat twin'],
        ['Bore × stroke', '78 × 78 mm (3.07 × 3.07 in)'],
        ['Displacement', '745 cc'],
        ['Compression ratio', '5.2 : 1'],
        ['Output', '18 hp at 3400 rpm'],
      ],
      care: 'Check valve clearance on a cold engine only, about 0.1 mm (0.004 in). Remove the valve chamber cover to get at it. Keep cylinder head and intake nuts tight, especially early on.',
    },
    sources: [FS, `${IB}, p. 21 (valve clearance), p. 23 (valves, pistons)`],
    unverified: [],
  },

  carburettor: {
    system: 'engine',
    term: 'Vergaser (SUM)',
    cz: {
      title: 'Karburátor SUM',
      text: 'Tahle R 12 má jeden karburátor SUM se třemi tryskami. Dvě jsou hlavní, třetí je pro volnoběh. Bovden od pravé rukojeti tahá za škrticí šoupátko. Pro studený start slouží startovací píst, který vytáhnete a pootočíte. Po zahřátí ho musíte zavřít, jinak motor žere a svíčky zanáší.',
      data: [
        ['Typ', 'SUM, jeden karburátor'],
        ['Trysky', '3 (2 hlavní, 1 volnoběžná)'],
      ],
      care: 'Čistí se sítko v pokličce plovákové komory, trysky a jehlový ventil. Plovákovou komoru vyplachujte benzínem zhruba po 3 200 až 4 000 km. Trysky nikdy nečistěte špendlíkem.',
    },
    en: {
      title: 'SUM carburettor',
      text: 'The single-carburettor R 12 runs a SUM carburettor with three jets: two main jets and one idling jet. A twist grip works the throttle slide through a Bowden cable. For a cold start you pull out and turn the starting piston. Once the engine warms up it has to be closed again, otherwise fuel consumption jumps and the plugs soot up.',
      data: [
        ['Type', 'SUM, single carburettor'],
        ['Jets', '3 (2 main, 1 idling)'],
      ],
      care: 'Clean the fuel screen in the float chamber cover, the jets and the needle valve. Rinse the float chamber with petrol about every 2000–2500 miles. Never poke jets with a pin.',
    },
    sources: [FS, `${IB}, p. 20–21 (cleaning), p. 25–26 (SUM carburettor), p. 39 (idle adjustment)`],
    unverified: [],
  },

  intake: {
    system: 'engine',
    term: 'Ansaugrohr und Luftfilter',
    cz: {
      title: 'Sání a vzduchový filtr',
      text: 'Sací potrubí je vyhřívané výfukovými plyny, takže se směs dobře tvoří i v zimě. Na karburátoru je našroubovaný vzduchový filtr. Měděná vata ve větracích zátkách vidlice se čistí stejně jako tyto filtry.',
      data: [],
      care: 'Filtr občas vypláchněte v benzínu, pak ho namočte do ohřátého oleje a přebytek důkladně vyklepejte. Matice sacího potrubí patří k prvním, které se mají dotahovat.',
    },
    en: {
      title: 'Intake and air filter',
      text: 'The intake pipe is heated by exhaust gas, so the mixture forms well even in cold weather. An air filter screws onto the carburettor. The copper-wool breather plugs on the fork are cleaned the same way as these filters.',
      data: [],
      care: 'Rinse the filter in petrol now and then, dip it in warmed oil and shake the excess out thoroughly. Intake pipe nuts are among those to retighten early on.',
    },
    sources: [`${IB}, p. 25 (heated suction piping), p. 21 (air filters), p. 14 (fork breather plugs)`],
    unverified: [],
  },

  exhaust: {
    system: 'engine',
    term: 'Auspuffrohre',
    cz: {
      title: 'Výfuk',
      text: 'Trubka vede z čela hlavy dolů před válcem a pod stupačkou dozadu do tlumiče, který končí plochým rybím ocasem. Výfukové plyny cestou ohřívají sací potrubí, takže se směs dobře tvoří i v zimě. Při demontáži válců jdou trubky dolů spolu s karburátorem.',
      data: [],
      care: null,
    },
    en: {
      title: 'Exhaust',
      text: 'The pipe runs from the front of the head down in front of the cylinder and back under the footboard into the silencer, which ends in a flat fishtail. On its way out, exhaust gas heats the intake pipe, so the mixture forms well even in cold weather. When the cylinders come off, the pipes come off with the carburettor.',
      data: [],
      care: null,
    },
    sources: [`${IB}, p. 25 (exhaust heating), p. 42 (dismantling the engine body)`, `${IB}, Fig. 1 (shape)`],
    unverified: [],
  },

  crankcase: {
    system: 'engine',
    term: 'Kurbelgehäuse',
    cz: {
      title: 'Klikový hřídel a skříň',
      text: 'Kliková skříň je zároveň olejová nádrž. Ocelový hřídel s kalenými čepy běží u R 12 v kuličkových ložiskách. Zubové čerpadlo ve spodní části nasává olej přes filtr a žene ho vrtáním k ložiskám. Vačkový hřídel nad klikovým pohání tichý řetěz. Odvzdušnění klikové skříně řeší rotační šoupátko, které udržuje lehký přetlak a drží olej uvnitř.',
      data: [
        ['Mazání', 'tlakové, zubové čerpadlo'],
        ['Objem oleje', '3¾ pinty (přibl. 2,1 l)'],
      ],
      care: 'Filtr čistěte jen speciálním proplachovacím olejem, nikdy benzínem.',
    },
    en: {
      title: 'Crankshaft and crankcase',
      text: 'The crankcase doubles as the oil tank. On the R 12 the crankshaft, steel with hardened pins, runs in ball bearings. A gear pump in the lower case pulls oil through a filter and forces it through drilled passages to the bearings. A silent chain drives the camshaft above the crankshaft. A rotary slide valve breathes the case, which keeps a slight overpressure and holds the oil in.',
      data: [
        ['Lubrication', 'forced feed, gear pump'],
        ['Oil capacity', '3¾ pints (about 2.1 L)'],
      ],
      care: 'Rinse the filter with rinsing oil, never with petrol.',
    },
    sources: [FS, `${IB}, p. 14–15 (oil change, pump), p. 23–25 (crankshaft, breather, lubrication), Fig. 2, p. 6 (oil capacity)`],
    unverified: [
      { cz: 'interval olejového filtru: text příručky s. 14 uvádí 7500–10 000 mil, obr. 2 7500–9000 mil', en: 'oil filter interval: manual text p. 14 says 7,500–10,000 miles, Fig. 2 says 7,500–9,000' },
    ],
  },

  ignition: {
    system: 'engine',
    term: 'Zündmagnet mit Unterbrecher',
    cz: {
      title: 'Zapalování (magneto)',
      text: 'Jednokarburátorová R 12 má kombinované magneto pro zapalování a světlo. Dodává zvlášť proud pro jiskru a zvlášť pro osvětlení. Přerušovač a rozdělovač vysokého napětí jsou v téže jednotce. Předstih se nastavuje otočnou rukojetí na levé straně řidítek. Magneto pohání z vačkového hřídele řetěz.',
      data: [
        ['Mezera kontaktů', '0,3–0,4 mm'],
        ['Seřízení kontaktů', 'po zhruba 4 800 km'],
      ],
      care: 'Kontakty čistěte čistým hadříkem, nikdy smirkem, a hlídejte, aby se na ně nedostal olej. Magneto se při mytí musí zakrýt. Při ročním servisu ho nechte prohlédnout v servisu Bosch.',
    },
    en: {
      title: 'Ignition (magneto)',
      text: 'The single-carburettor R 12 has a combined lighting and ignition magneto. It supplies spark current and lighting current separately. The contact breaker and the high-tension distributor sit in the same unit. Timing is set by the twist grip on the left of the handlebars. A chain from the camshaft drives the magneto.',
      data: [
        ['Contact gap', '0.3–0.4 mm (0.012–0.016 in)'],
        ['Contact adjustment', 'about every 3000 miles'],
      ],
      care: 'Clean the points with a clean rag, never emery, and keep oil off them. Cover the magneto when hosing the bike down. Have a Bosch depot inspect it at the yearly overhaul.',
    },
    sources: [FS, `${IB}, p. 18 (contact breaker, magneto), p. 29–30 (ignition description)`],
    unverified: [],
  },

  generator: {
    system: 'engine',
    term: 'Lichtmaschine (Dynamo)',
    cz: {
      title: 'Dynamo',
      text: 'Dynamo je součást stejné jednotky jako magneto a vyrábí proud pro světla. Díky rychlému regulátoru uvnitř dokáže motocykl jet i s odpojenou baterií. Baterie slouží jen pro stání, když motor neběží.',
      data: [
        ['Typ (fact sheet)', 'Bosch D 2 BRS 170'],
      ],
      care: 'Dynamo ani magneto nestříkejte vodou. Mazivo v ložiscích a převodu má měnit servis Bosch při generální opravě.',
    },
    en: {
      title: 'Dynamo',
      text: 'The dynamo shares a housing with the magneto and makes the current for the lights. A quick regulator inside lets the bike run even with the battery disconnected. The battery only covers the lights when the engine is standing.',
      data: [
        ['Type (fact sheet)', 'Bosch D 2 BRS 170'],
      ],
      care: 'Keep water off the dynamo and magneto. Bearing and gear grease should be renewed by a Bosch depot during a general overhaul.',
    },
    sources: [FS, `${IB}, p. 29–30 (lighting and ignition magneto), p. 15 (cleaning)`],
    unverified: [
      { cz: 'fact sheet uvádí Bosch D 2 BRS 170 jako „Alternator“ a neříká, ke které verzi (magneto, nebo baterie) patří', en: 'the fact sheet lists a Bosch D 2 BRS 170 ‘alternator’ without saying which version (magneto or battery) it belongs to' },
    ],
  },

  sparkplugs: {
    system: 'engine',
    term: 'Zündkerzen',
    cz: {
      title: 'Zapalovací svíčky',
      text: 'Každý válec má jednu svíčku. Příručka je výslovně omezuje na schválené typy, které nezpůsobují žhavé zapalování ani při velkém zatížení. Zanesená svíčka je typický následek zapomenutého startovacího pístu.',
      data: [
        ['Typ (příručka)', 'Bosch DM 175/1'],
        ['Typ (fact sheet)', 'Bosch M 175 T1 nebo W 175 T1'],
      ],
      care: 'Používejte jen předepsané svíčky. Dva zdroje se v označení liší, proto si typ ověřte podle stroje.',
    },
    en: {
      title: 'Spark plugs',
      text: 'Each cylinder has one plug. The manual limits you to approved types that avoid glow ignition even under heavy load. Sooty plugs are a typical result of a starting piston left open.',
      data: [
        ['Type (manual)', 'Bosch DM 175/1'],
        ['Type (fact sheet)', 'Bosch M 175 T1 or W 175 T1'],
      ],
      care: 'Use only the prescribed plugs. The two sources name them differently, so confirm the type against the bike.',
    },
    sources: [FS, `${IB}, p. 19 (sparking plugs), p. 11 (sooted plugs)`],
    unverified: [
      { cz: 'příručka s. 19 uvádí Bosch DM 175/1, fact sheet Bosch M 175 T1 nebo W 175 T1', en: 'manual p. 19 gives Bosch DM 175/1, the fact sheet Bosch M 175 T1 or W 175 T1' },
    ],
  },

  kickstarter: {
    system: 'engine',
    term: 'Kickstarter',
    cz: {
      title: 'Kickstarter',
      text: 'Pedál je za levou stupačkou. Hřídel startéru vede podél motorky stejně jako hřídele převodovky, takže páka trčí do strany a šlape se dolů napříč strojem, rýhovaný pedál přitom míří dozadu. Šlápnutím se otočí segment a dvě čelní kola, a ta roztočí hlavní hřídel převodovky přes spojku. V klidové poloze kolík uvolní vnitřní ozubení, takže se kolo točí naprázdno. Startuje se s neutrálem v převodovce.',
      data: [],
      care: 'Před šlápnutím otevřete benzínový kohout a zapněte klíčkem zapalování na světlometu. Šlapejte rychle a plným zdvihem.',
    },
    en: {
      title: 'Kickstarter',
      text: 'The pedal sits behind the left footboard. The kick shaft runs fore and aft like the gearbox shafts, so the lever sticks out sideways and is kicked down across the machine, with the ribbed pedal pointing backwards. Pressing it turns a segment and two spur wheels, which spin the gearbox main shaft through the clutch. At rest a dog frees the internal teeth, so the wheel idles. You start in neutral.',
      data: [],
      care: 'Open the fuel tap and push the switch key in on the headlamp first. Kick quickly and with a full stroke.',
    },
    sources: [`${IB}, p. 7 (position), Fig. 4 (lever and pedal from above), p. 11 (starting), p. 32 (mechanism)`],
    unverified: [],
  },

  // ───────── PŘEVODOVKA A POHON ─────────
  clutch: {
    system: 'drivetrain',
    term: 'Zweischeiben-Trockenkupplung',
    cz: {
      title: 'Spojka',
      text: 'Suchá dvoudisková spojka sedí na setrvačníku. Šest pružin tlačí přítlačný kotouč na lamely s obložením z obou stran a mezi nimi je unášecí disk. Páčka na levé straně řidítek tahá bovdenem za páku na převodovce a odtlačí přítlačný kotouč pryč od lamel.',
      data: [
        ['Typ', 'dva kotouče, suchá'],
        ['Pružiny', '6'],
      ],
      care: 'Při seřizování brzd zkontrolujte i lanko spojky. Páčka musí mít vůli, jinak se obložení zbytečně opotřebuje.',
    },
    en: {
      title: 'Clutch',
      text: 'A dry two-plate clutch sits on the flywheel. Six springs press a thrust plate against friction plates lined on both sides, with a driving disc in between. The lever on the left handlebar pulls a Bowden cable to a lever on the gearbox, which lifts the thrust plate off the plates.',
      data: [
        ['Type', 'two plates, dry'],
        ['Springs', '6'],
      ],
      care: 'When adjusting the brakes, check the clutch cable too. The lever needs free play, otherwise the lining wears for nothing.',
    },
    sources: [FS, `${IB}, p. 31 (two-plate clutch), p. 17 (adjustment)`],
    unverified: [],
  },

  gearbox: {
    system: 'drivetrain',
    term: 'Vierganggetriebe',
    cz: {
      title: 'Čtyřstupňová převodovka',
      text: 'Převodovka je ručně řazená se čtyřmi rychlostmi. Kola na hlavním hřídeli jsou v trvalém záběru s volnými koly na výstupním hřídeli. Rychlost vybírají přesuvné objímky s čelními zuby. Převodovka je spojená s motorem do jednoho bloku. V odlitku je schránka na nářadí.',
      data: [
        ['1. stupeň', '3,18 : 1'],
        ['2. stupeň', '2,06 : 1'],
        ['3. stupeň', '1,42 : 1'],
        ['4. stupeň', '1,09 : 1'],
      ],
      care: 'Opravy převodovky přenechte odborníkovi.',
    },
    en: {
      title: 'Four-speed gearbox',
      text: 'A manual four-speed box. The gears on the main shaft are always meshed with loose gears on the output shaft. Sliding sleeves with dogs pick the ratio. The box is built into one unit with the engine, and a tool container is cast into its housing.',
      data: [
        ['1st gear', '3.18 : 1'],
        ['2nd gear', '2.06 : 1'],
        ['3rd gear', '1.42 : 1'],
        ['4th gear', '1.09 : 1'],
      ],
      care: 'Leave gearbox repairs to an expert.',
    },
    sources: [FS, `${IB}, p. 6 (gear ratios), p. 31–32 (gearbox), p. 35 (tool container), p. 14 (oil)`],
    unverified: [],
  },

  gearlever: {
    system: 'drivetrain',
    term: 'Schalthebel',
    cz: {
      title: 'Řadicí páka',
      text: 'Páka je vedená v kulise, která zároveň tvoří pravou kolenní opěrku. Řadí se ručně. Při řazení nahoru stáhněte spojku a snižte plyn, při řazení dolů dejte přibližně polovinu plynu. Přeskakování stupňů se nedoporučuje.',
      data: [],
      care: 'První stupeň je jen pro rozjezd. Za jízdy v hustém městském provozu stačí druhý nebo třetí.',
    },
    en: {
      title: 'Gear lever',
      text: 'The lever runs in a gate that doubles as the right knee grip. Shifting is manual. For upshifts you declutch and ease the throttle, for downshifts you give about half throttle. Skipping gears is discouraged.',
      data: [],
      care: 'First gear is for moving off only. In dense town traffic, second or third is enough.',
    },
    sources: [`${IB}, p. 9–10 (gear lever)`],
    unverified: [],
  },

  driveshaft: {
    system: 'drivetrain',
    term: 'Kardanwelle',
    cz: {
      title: 'Kardanová hřídel',
      text: 'Výkon jde z převodovky přes pružnou gumovou spojku na kardan. Zubová spojka za ním vyrovná podélné posuvy. Hřídel pak předává výkon dvojici kuželových kol.',
      data: [],
      care: null,
    },
    en: {
      title: 'Driveshaft',
      text: 'Power goes from the gearbox through a flexible rubber coupling to the cardan shaft. A tooth coupling behind it takes up lengthwise movement. The shaft then feeds the pair of bevel gears.',
      data: [],
      care: null,
    },
    sources: [`${IB}, p. 32 (power transmission)`],
    unverified: [],
  },

  reardrive: {
    system: 'drivetrain',
    term: 'Hinterachsantrieb (Kegelradsatz)',
    cz: {
      title: 'Zadní náhon',
      text: 'Dvojice kuželových kol se šikmým ozubením pohání zadní kolo přes drážkový spoj a běží téměř neslyšně. Spodek skříně slouží zároveň jako olejová nádrž. Hladinu hlídá měrka s šestihrannou hlavou na levé straně.',
      data: [
        ['Převod zadní osy', '1 : 4,07'],
        ['Kuželové / talířové kolo', '14 / 57 zubů'],
      ],
      care: 'Olej doplňujte po spodní závity, nikdy nad horní rysku.',
    },
    en: {
      title: 'Rear drive',
      text: 'A pair of helical-toothed bevel gears drives the rear wheel through a splined joint and runs almost silently. The bottom of the casing is the oil tank. A dipstick with a hex head on the left side shows the level.',
      data: [
        ['Rear axle ratio', '1 : 4.07'],
        ['Pinion / crown wheel', '14 / 57 teeth'],
      ],
      care: 'Top up to the lower thread, never above the upper ring.',
    },
    sources: [FS, `${IB}, p. 14 (rear drive oil), p. 32 (bevel gears)`],
    unverified: [],
  },

  // ───────── PODVOZEK ─────────
  frame: {
    system: 'chassis',
    term: 'Preßstahlrahmen',
    cz: {
      title: 'Lisovaný rám',
      text: 'Rám je z lisované oceli a byl největší novinkou R 12 proti předchůdci R 11, od kterého motor zůstal. Je to dvojitý rám z ocelových výlisků s průřezem do U, vyztužený jako příhradový trojúhelník. Obě boční poloviny vepředu obepínají hlavu řízení půlkruhem a vzadu je spojují lisované úhelníky. Spodní nosník vede pod motorem a převodovkou rovně a před zadní osou se ohýbá nahoru do oblouku, který přechází v horní nosník. Před zadním kolem je ztužuje oblouková vzpěra lisovaná z jednoho kusu, tvarovaná podle blatníku. Motor s převodovkou tvoří jeden blok zavěšený v rámu. Zadní odpružení není, zadní kolo je pevné.',
      data: [
        ['Rozvor', '1380 mm'],
        ['Zadní odpružení', 'žádné (pevný rám)'],
      ],
      care: 'Všechny matice a šrouby kontrolujte hlavně v prvních kilometrech, třeba u zadního blatníku a nosiče.',
    },
    en: {
      title: 'Pressed-steel frame',
      text: 'The frame is pressed steel and was the big change from the R 11, whose engine carried over. It is a double frame of U-section steel pressings, braced as a triangulated truss. At the front the two halves wrap round the steering head in a half circle and are tied behind it by pressed gusset angles. The lower member runs straight under engine and gearbox and turns up in a curve in front of the rear axle into the top member. In front of the rear wheel a one-piece pressed strut, curved to follow the mudguard, braces both sides. Engine and gearbox form one block mounted in the frame. There is no rear suspension, the rear end is rigid.',
      data: [
        ['Wheelbase', '1380 mm'],
        ['Rear suspension', 'none (rigid)'],
      ],
      care: 'Check all nuts and bolts at short intervals early on, including the rear mudguard and luggage carrier.',
    },
    sources: [FS, `${IB}, p. 5 (preface), p. 13 (general instructions)`, 'BMW Betriebsanleitung R 12 / R 17 (German), p. 49–50 (frame)', 'Ersatzteilliste R 12 / R 17, 1938, plate 1 (bare frame)'],
    unverified: [],
  },

  fork: {
    system: 'chassis',
    term: 'Teleskopgabel mit Öldämpfung',
    cz: {
      title: 'Teleskopická vidlice',
      text: 'BMW ji představilo jako první na světě: trubky zasunuté do sebe, uvnitř šroubové pružiny a nastavitelné ventily olejového tlumiče. Rázy tak zachycuje měkce a skoro bez tření a zpětné rázy tlumí. Oleje se do ní plní jen při opravě, horní zátky slouží zároveň jako odvzdušnění.',
      data: [
        ['Typ', 'teleskopická, hydraulický tlumič'],
      ],
      care: 'Po opravě se do každé nohy plní asi ¼ pinty (přibl. 0,14 l) oleje do tlumičů. Zátky s vatou čistěte jako vzduchové filtry. Při ročním servisu namažte ložiska řízení.',
    },
    en: {
      title: 'Telescopic fork',
      text: 'BMW presented it as the first of its kind in the world: tubes sliding into each other, coil springs inside and adjustable oil damper valves. It absorbs shocks softly and with almost no friction and checks rebound. Oil is filled only for repairs, and the top plugs double as breathers.',
      data: [
        ['Type', 'telescopic, hydraulic damping'],
      ],
      care: 'After a repair about ¼ pint (0.14 L) of shock absorber oil goes into each leg. Clean the copper-wool plugs like the air filters. Regrease the steering head bearings at the yearly overhaul.',
    },
    sources: [FS, `${IB}, p. 34 (front fork), p. 14 (fork oil)`],
    unverified: [],
  },

  steeringdamper: {
    system: 'chassis',
    term: 'Lenkungsdämpfer',
    cz: {
      title: 'Tlumič řízení',
      text: 'Uprostřed řidítek je velká křídlová matice, kterou řízení přitáhnete nebo povolíte podle stavu silnice.',
      data: [],
      care: 'Utažením řízení ztuhne, povolením změkne.',
    },
    en: {
      title: 'Steering damper',
      text: 'A large wing nut in the middle of the handlebars stiffens or loosens the steering to suit the road.',
      data: [],
      care: 'Tightening stiffens the steering, loosening softens it.',
    },
    sources: [`${IB}, p. 10 (steering damper)`],
    unverified: [],
  },

  frontwheel: {
    system: 'chassis',
    term: 'Vorderrad',
    cz: {
      title: 'Přední kolo',
      text: 'Ráfek 3 × 19 palce s dvojitými koncovými dráty. Kolo drží vyklepávací osa, která se vyšroubuje po povolení svorky na levé noze vidlice. Přední, zadní a případně sajdkárové kolo jsou zaměnitelná. Bubnová brzda je uvnitř.',
      data: [
        ['Ráfek', '3 × 19 palce'],
        ['Pneumatika', '3,5 × 19'],
      ],
      care: 'Tlak v pneumatice pro stroj bez sajdkáry je asi 1,0 bar.',
    },
    en: {
      title: 'Front wheel',
      text: 'A 3 × 19 inch rim with double-thick end spokes. A knock-out axle holds the wheel, unscrewed after loosening the clamp on the left fork leg. Front, rear and, with a sidecar, the third wheel are interchangeable. The drum brake is inside.',
      data: [
        ['Rim', '3 × 19 in'],
        ['Tyre', '3.5 × 19'],
      ],
      care: 'Solo tyre pressure is 15 lb/sq in (about 1.0 bar).',
    },
    sources: [FS, `${IB}, p. 34 (wheels), p. 22 (tyre pressure), p. 40 (dismantling front wheel), Fig. 2 (hub nipple)`],
    unverified: [
      { cz: 'pneumatiky: fact sheet 3,5 × 19, příručka s. 6 a 34 uvádí 26 × 3,50 palce', en: 'tyres: fact sheet 3.5 × 19, manual pp. 6 and 34 give 26 × 3.50 in' },
    ],
  },

  rearwheel: {
    system: 'chassis',
    term: 'Hinterrad',
    cz: {
      title: 'Zadní kolo',
      text: 'Stejné jako přední, jen se pohání drážkami z kuželového soukolí. Zadní část blatníku se dá sundat, takže kolo vyjmete bez naklánění stroje. Vyklepávací osa se u sólo stroje vyšroubuje otáčením doprava.',
      data: [
        ['Ráfek', '3 × 19 palce'],
        ['Pneumatika', '3,5 × 19'],
      ],
      care: 'Při výměně pláště nenechte do drážek dostat nečistotu a kolo nasazujte jen na čisté drážky. Tlak sólo asi 1,45 bar.',
    },
    en: {
      title: 'Rear wheel',
      text: 'The same as the front, except it is driven through splines from the bevel gears. The rear end of the mudguard can be removed, so the wheel comes out without tilting the bike. On a solo machine the knock-out axle is unscrewed by turning it to the right.',
      data: [
        ['Rim', '3 × 19 in'],
        ['Tyre', '3.5 × 19'],
      ],
      care: 'When changing tyres keep dirt out of the splines and refit the wheel only on perfectly clean splines. Solo pressure is 21 lb/sq in (about 1.45 bar).',
    },
    sources: [FS, `${IB}, p. 34 (wheels, mudguards), p. 22 (tyre pressure), p. 40–41 (dismantling)`],
    unverified: [],
  },

  brakes: {
    system: 'chassis',
    term: 'Innenbackenbremsen',
    cz: {
      title: 'Bubnové brzdy',
      text: 'Obě brzdy jsou vnitřní čelisťové a plně zakryté proti vodě a špíně. Přední se ovládá pravou pákou, zadní nožním pedálem. Příručka radí brzdit oběma současně, v zatáčce jen zadní a při dlouhém klesání střídat ruční a nožní.',
      data: [
        ['Průměr bubnu', '200 mm (přední i zadní)'],
      ],
      care: 'Přední brzdu seřídíte křídlovým šroubem na krytu, zadní křídlovou maticí na tyči. Nechte vždy trochu vůle v pákách. Při seřizování zkontrolujte i lanko spojky.',
    },
    en: {
      title: 'Drum brakes',
      text: 'Both brakes are internal expanding and fully enclosed against water and dirt. The front is worked by the right lever, the rear by the foot pedal. The manual says to apply both together, use only the rear in bends and alternate hand and foot brake on long descents.',
      data: [
        ['Drum diameter', '200 mm (front and rear)'],
      ],
      care: 'Adjust the front brake with the wing screw on the brake case, the rear with the wing nut on the tension rod. Keep a little play in the levers. Check the clutch cable at the same time.',
    },
    sources: [FS, `${IB}, p. 10 (use), p. 15–17 (adjustment), p. 34 (brakes)`],
    unverified: [],
  },

  fenders: {
    system: 'chassis',
    term: 'Kotflügel',
    cz: {
      title: 'Blatníky',
      text: 'Zadní blatník má odnímatelnou zadní část. Díky tomu se zadní kolo vyndá bez naklánění a zvedání stroje, což ocení hlavně sajdkáristé. U stroje se sajdkárou je potřeba nejdřív odšroubovat zadní svítilnu.',
      data: [],
      care: 'Upevnění blatníků a nosiče kontrolujte v prvních kilometrech.',
    },
    en: {
      title: 'Mudguards',
      text: 'The rear mudguard has a detachable back end. That lets you take the rear wheel off without tilting or lifting the bike, which sidecar riders appreciate most. On a sidecar machine the tail light has to be unscrewed first.',
      data: [],
      care: 'Check the mudguard and carrier fixings in the early miles.',
    },
    sources: [`${IB}, p. 34 (mudguards), p. 40 (sidecar dismantling), p. 13`],
    unverified: [],
  },

  stand: {
    system: 'chassis',
    term: 'Klappständer',
    cz: {
      title: 'Stojan',
      text: 'Každý stroj má pod rámem dva sklopné stojany. Nahoře je drží pružiny. Na stojanech se zvedne celý motocykl a kola se pak snadno snímají.',
      data: [
        ['Počet', '2 (přední a zadní)'],
      ],
      care: null,
    },
    en: {
      title: 'Stands',
      text: 'Every machine carries two hinged stands under the frame, held up by springs. Putting the bike on them lifts it enough that the wheels come off easily.',
      data: [
        ['Count', '2 (front and rear)'],
      ],
      care: null,
    },
    sources: [`${IB}, p. 34 (hinged stands), p. 40 (rear stand for wheel removal)`],
    unverified: [],
  },

  saddle: {
    system: 'chassis',
    term: 'Sattel',
    cz: {
      title: 'Sedlo',
      text: 'Sedlo je 70 cm nad zemí. Kožené sedlo na lisované misce má hluboké boční lemy s řadou nýtů a zvednutý zadní okraj. Vpředu se otáčí na čepu na rámu, vzadu z rohu misky vede na každé straně jedna tyč svisle dolů do vinuté pružiny, která visí pod okem na horním nosníku rámu.',
      data: [
        ['Výška sedla', '0,70 m'],
      ],
      care: null,
    },
    en: {
      title: 'Saddle',
      text: 'The saddle sits 70 cm (2 ft 3½ in) above the ground. A leather-covered pressed pan with deep side skirts, a row of rivets and a raised rear edge. It pivots on the frame at the nose; at the rear one rod on each side drops straight down from the corner of the pan into a coil spring hung below a lug on the top frame member.',
      data: [
        ['Saddle height', '0.70 m (2 ft 3½ in)'],
      ],
      care: null,
    },
    sources: [`${IB}, p. 6 (data table, saddle height)`, `${IB}, Fig. 1 (springs)`, 'Ersatzteilliste R 12 / R 17, 1938, plate 2 (saddle, springs), photo p. 4'],
    unverified: [],
  },

  tank: {
    system: 'chassis',
    term: 'Kraftstoffbehälter',
    cz: {
      title: 'Palivová nádrž',
      text: 'Nádrž pojme 14 litrů. Dole má kohout se zachycovačem vody a sítkem. Doporučená směs je benzín a benzol půl na půl a při záběhu se do paliva přimíchává olej na mazání horní části válců. Spotřeba je 3,5 až 4 litry na 100 km.',
      data: [
        ['Objem nádrže', '14 l'],
        ['Spotřeba paliva', '3,5–4 l / 100 km'],
        ['Spotřeba oleje', '1–2 l / 1000 km'],
      ],
      care: 'Před startem otevřete kohout, po vypnutí motoru ho zavřete. Vodní lapač a sítko v kohoutu občas vyčistěte.',
    },
    en: {
      title: 'Fuel tank',
      text: 'The tank holds 14 litres. A fuel tap at the bottom carries a water trap and a screen. The recommended fuel is petrol and benzol in equal parts, with an upper-cylinder lubricant mixed in during running in. Consumption is 3.5 to 4 litres per 100 km.',
      data: [
        ['Tank capacity', '14 L'],
        ['Fuel consumption', '3.5–4 L / 100 km'],
        ['Oil consumption', '1–2 L / 1000 km'],
      ],
      care: 'Open the tap before starting and close it after the engine is stopped. Clean the water trap and screen in the tap now and then.',
    },
    sources: [FS, `${IB}, p. 6 (tank capacity), p. 11–12 (fuel, tap), p. 21 (fuel cock cleaning)`],
    unverified: [],
  },

  // ───────── OVLÁDÁNÍ ─────────
  handlebar: {
    system: 'controls',
    term: 'Lenker',
    cz: {
      title: 'Řidítka',
      text: 'Většina ovládání je na řidítkách. Vpravo je plyn, tlačítko klaksonu, přepínač dálkových a tlumených světel a páka přední brzdy. Vlevo je páka spojky, rukojeť předstihu a tlačítko pro zkrat. Uprostřed je matice tlumiče řízení.',
      data: [],
      care: 'Lanka a kabely na řidítkách kontrolujte po zhruba 3 200 km, jestli se někde neprodřely.',
    },
    en: {
      title: 'Handlebars',
      text: 'Most controls are on the handlebars. On the right are the throttle, horn button, headlamp dimmer and front brake lever. On the left are the clutch lever, the ignition twist grip and the short-circuit button. The steering damper nut is in the middle.',
      data: [],
      care: 'Check cables and wiring at the handlebars about every 2000 miles for chafing.',
    },
    sources: [`${IB}, p. 7 (arrangement of controls), p. 20 (cables)`],
    unverified: [],
  },

  throttle: {
    system: 'controls',
    term: 'Drehgriff Gas',
    cz: {
      title: 'Plynová rukojeť',
      text: 'Pravá otočná rukojeť ovládá bovdenem šoupátko karburátoru. Otočením dozadu (k sobě) plyn přidáte, otočením dopředu ho zavřete. Bovden má na šoupátku nastavitelnou vůli.',
      data: [],
      care: 'Při seřizování volnoběhu povolte bovden a po nastavení vůli zase vyberte.',
    },
    en: {
      title: 'Throttle twist grip',
      text: 'The right twist grip works the carburettor slide through a Bowden cable. Turn it backwards to open, forwards to close. The cable has an adjustable set screw at the slide.',
      data: [],
      care: 'Loosen the cable when adjusting idle and take the end play out again afterwards.',
    },
    sources: [`${IB}, p. 7 (throttle twist grip), p. 39 (idle adjustment)`],
    unverified: [],
  },

  advance: {
    system: 'controls',
    term: 'Zündverstellung (Drehgriff links)',
    cz: {
      title: 'Předstih',
      text: 'Levá otočná rukojeť přes bovden natáčí přerušovač. Otočením od jezdce (ven) přidáte předstih, k jezdci (dovnitř) ho zpozdíte. Na start dejte vždy pozdní zapalování, jinak motor kopne zpět.',
      data: [],
      care: 'Když motor klepe, hlavně do kopce, ubírejte předstih, dokud klepání nepřestane. Při plné rychlosti po rovině jezděte s plným předstihem.',
    },
    en: {
      title: 'Ignition advance',
      text: 'The left twist grip turns the contact breaker through a Bowden cable. Twist it outward, away from the rider, to advance, inward to retard. Always start with the ignition retarded, otherwise the engine can kick back.',
      data: [],
      care: 'If the engine knocks, especially uphill, retard until it stops. At full cruising speed on the flat run fully advanced.',
    },
    sources: [`${IB}, p. 9 (ignition twist grip), p. 11 (starting)`],
    unverified: [],
  },

  footbrake: {
    system: 'controls',
    term: 'Fußbremshebel',
    cz: {
      title: 'Nožní brzda',
      text: 'Pedál leží za pravou stupačkou a ovládá zadní bubnovou brzdu. V zatáčkách má brzdit jen on. Při dlouhém klesání se střídá s ruční brzdou, aby se obě nezahřály zároveň.',
      data: [],
      care: 'Zadní brzdu seřídíte křídlovou maticí na brzdové tyči. Kloubové body tyčí mažte po zhruba 320 až 480 km.',
    },
    en: {
      title: 'Foot brake',
      text: 'The pedal sits behind the right footboard and works the rear drum brake. In bends use it alone. On long descents alternate it with the hand brake so the two do not heat up together.',
      data: [],
      care: 'Adjust the rear brake with the wing nut on the brake rod. Oil the rod joints every 200–300 miles.',
    },
    sources: [`${IB}, p. 10 (brakes), p. 17 (adjustment), Fig. 1 (oiling points)`],
    unverified: [],
  },

  killbutton: {
    system: 'controls',
    term: 'Kurzschlußknopf',
    cz: {
      title: 'Zkratové tlačítko',
      text: 'Jednokarburátorová R 12 má na levé straně řidítek tlačítko, které zkratuje zapalování. Zastavuje se jím motor na konci jízdy a rychle se zpomalí v zatáčce nebo při náhlé překážce.',
      data: [],
      care: 'Motor se dá zastavit i klíčkem na světlometu. Po zastavení nezapomeňte zavřít benzínový kohout.',
    },
    en: {
      title: 'Short-circuit button',
      text: 'The single-carburettor R 12 has a button on the left side of the handlebars that shorts the ignition. It stops the engine at the end of a ride and cuts speed quickly in a bend or when an obstacle appears.',
      data: [],
      care: 'The engine can also be stopped with the switch key on the headlamp. Remember to close the fuel tap after stopping.',
    },
    sources: [`${IB}, p. 10 (short-circuit push button), p. 12 (stopping)`],
    unverified: [],
  },

  // ───────── ELEKTRO ─────────
  headlamp: {
    system: 'electrics',
    term: 'Scheinwerfer',
    cz: {
      title: 'Světlomet',
      text: 'Ve světlometu je dvouvláknová žárovka pro dálková a tlumená světla a pomocná parkovací žárovka. Klíček nahoře zapíná zapalování a světla, červená kontrolka svítí, když je zapalování zapnuté. Tachometr je ve světlometu a pohání ho šnek z převodovky.',
      data: [],
      care: 'Nenechávejte červenou kontrolku svítit při delším stání, vybíjí se tím baterie přes dynamo.',
    },
    en: {
      title: 'Headlamp',
      text: 'The headlamp holds a two-filament bulb for main and dipped beam and an auxiliary parking bulb. The key on top switches ignition and lights, and a red check lamp glows with the ignition on. The speedometer sits in the headlamp, driven by a worm from the gearbox.',
      data: [],
      care: 'Do not leave the red check lamp burning during long stops, it drains the battery through the dynamo.',
    },
    sources: [`${IB}, p. 11 (switch key), p. 34–35 (headlamp, Fig. 19)`],
    unverified: [],
  },

  battery: {
    system: 'electrics',
    term: 'Batterie',
    cz: {
      title: 'Baterie',
      text: 'Baterie stojí za převodovkou na levé spodní vzpěře rámu, hned před zadní pneumatikou. U jednokarburátorového stroje baterie pohání světla jen ve stoje. Zapalování a jízdní osvětlení zajišťuje magneto s dynamem, takže motocykl jede i s odpojenou baterií.',
      data: [],
      care: 'Baterii zkontrolujte každé 4 až 6 týdnů, ať se jezdí, nebo ne. Nabíjení a ošetření podle pokynů Bosch.',
    },
    en: {
      title: 'Battery',
      text: 'The battery stands behind the gearbox on the left lower frame member, just ahead of the rear tyre. On the single-carburettor machine it only feeds the lights at a standstill. Ignition and running lights come from the magneto and dynamo, so the bike runs even with the battery disconnected.',
      data: [],
      care: 'Check the battery every 4 to 6 weeks, whether the bike is used or not. Charging and care follow the Bosch instructions.',
    },
    sources: [`${IB}, p. 19 (battery service), p. 29–30 (ignition)`, 'Photo of the unrestored machine, Wikimedia Commons (Tux-Man, CC0), position'],
    unverified: [],
  },

  taillight: {
    system: 'electrics',
    term: 'Schlußlicht',
    cz: {
      title: 'Zadní světlo',
      text: 'U stroje se sajdkárou se zadní svítilna musí odšroubovat dřív, než sundáte zadní část blatníku.',
      data: [],
      care: null,
    },
    en: {
      title: 'Tail light',
      text: 'On a sidecar machine the tail light has to be unscrewed before the rear part of the mudguard comes off.',
      data: [],
      care: null,
    },
    sources: [`${IB}, p. 40 (dismantling rear wheel, sidecar machines)`],
    unverified: [],
  },

  horn: {
    system: 'electrics',
    term: 'Hupe',
    cz: {
      title: 'Klakson',
      text: 'Klakson sedí vpředu mezi bočnicemi rámu pod panelem se znakem, čelem po směru jízdy. Tlačítko je na pravé rukojeti řidítek.',
      data: [],
      care: null,
    },
    en: {
      title: 'Horn',
      text: 'The horn sits at the front between the two frame members, below the badge panel, facing forward. Its button is on the right grip of the handlebars.',
      data: [],
      care: null,
    },
    sources: [`${IB}, p. 7 (arrangement of controls)`, `${IB}, Fig. 1 (position)`],
    unverified: [],
  },
};

export const LUBE = [
  {
    part: 'crankcase',
    cz: 'Motor, hladina oleje (měrka)',
    en: 'Engine oil level (dipstick)',
    every_cz: 'kontrola po 400 km, doplnit po horní rysku',
    every_en: 'check every 250 miles, top up to upper ring',
    lubricant_cz: 'Gargoyle Mobiloil BB, v zimě Arctic, v horku D',
    lubricant_en: 'Gargoyle Mobiloil BB, Arctic in winter, D in hot weather',
    source: 'Fig. 2 and p. 14 (lubrication), p. 12 (lubricants)',
  },
  {
    part: 'crankcase',
    cz: 'Motor, výměna oleje',
    en: 'Engine oil change',
    every_cz: 'po 1 900 km (za záběhu po 480 km), filtr po 12 000–16 000 km',
    every_en: 'every 1200 miles (every 300 miles during running in), filter every 7500–10 000 miles',
    lubricant_cz: 'Gargoyle Mobiloil BB',
    lubricant_en: 'Gargoyle Mobiloil BB',
    source: 'Fig. 2 and p. 14 (text 7500–10 000 miles, figure 7500–9000)',
  },
  {
    part: 'gearbox',
    cz: 'Plnicí otvor převodovky',
    en: 'Gearbox oil filler',
    every_cz: 'kontrola po 970 km, doplnit po spodní závity; po záběhu olej vyměnit',
    every_en: 'check every 600 miles, top up to lower threads; renew after running in',
    lubricant_cz: 'Gargoyle Mobiloil BB',
    lubricant_en: 'Gargoyle Mobiloil BB',
    source: 'Fig. 1 and p. 14',
  },
  {
    part: 'reardrive',
    cz: 'Zadní náhon (skříň kuželového soukolí)',
    en: 'Rear drive casing',
    every_cz: 'kontrola po 970 km, výměna po záběhu a pak asi po 16 000 km',
    every_en: 'check every 600 miles, renew after running in and about every 10 000 miles',
    lubricant_cz: 'Gargoyle Mobiloil D',
    lubricant_en: 'Gargoyle Mobiloil D',
    source: 'Fig. 1 and p. 14',
  },
  {
    part: 'ignition',
    cz: 'Magneto, mazničky s klapkou',
    en: 'Magneto flap lubricators',
    every_cz: 'po 1 900 km, olej dolévat do vytečení z druhé maznice',
    every_en: 'every 1200 miles, add oil until it runs out of the other lubricator',
    lubricant_cz: 'motorový olej jako pro motor',
    lubricant_en: 'same engine oil',
    source: 'p. 15',
  },
  {
    part: 'frontwheel',
    cz: 'Maznice v náboji kol',
    en: 'Wheel hub nipples',
    every_cz: 'po 970 km tlakovou maznicí',
    every_en: 'every 600 miles with the grease gun',
    lubricant_cz: 'Gargoyle Mobilgrease č. 4, nikdy běžná vazelína',
    lubricant_en: 'Gargoyle Mobilgrease No. 4, never ordinary grease',
    source: 'Fig. 2, p. 12',
  },
  {
    part: 'brakes',
    cz: 'Tyče brzd a bovdeny',
    en: 'Brake rods and Bowden cables',
    every_cz: 'po 320–480 km',
    every_en: 'every 200–300 miles',
    lubricant_cz: 'olej',
    lubricant_en: 'oil',
    source: 'Fig. 1',
  },
  {
    part: 'fork',
    cz: 'Olejové tlumiče vidlice',
    en: 'Fork shock absorber oil',
    every_cz: 'bez pravidelného mazání, doplnit jen uniklý olej, při opravě vyměnit',
    every_en: 'no regular lubrication, replace only leaked oil, renew for repairs',
    lubricant_cz: 'olej do tlumičů',
    lubricant_en: 'shock absorber oil',
    source: 'Fig. 1 and p. 14',
  },
];

export const SPECS = [
  { cz: 'Rok výroby', en: 'Production years', value_cz: '1935–1942', value_en: '1935–1942', source: FS },
  { cz: 'Vyrobeno kusů', en: 'Units built', value_cz: '36 000', value_en: '36,000', source: FS },
  { cz: 'Zdvihový objem', en: 'Displacement', value_cz: '745 cm³', value_en: '745 cc', source: FS },
  { cz: 'Vrtání × zdvih', en: 'Bore × stroke', value_cz: '78 × 78 mm', value_en: '78 × 78 mm (3.07 in)', source: FS },
  { cz: 'Výkon', en: 'Output', value_cz: '18 k při 3400 ot/min', value_en: '18 hp at 3400 rpm', source: FS },
  { cz: 'Kompresní poměr', en: 'Compression ratio', value_cz: '5,2 : 1', value_en: '5.2 : 1', source: FS },
  { cz: 'Max. rychlost', en: 'Top speed', value_cz: '110 km/h', value_en: '110 km/h (67 mph)', source: FS },
  { cz: 'Převody', en: 'Gear ratios', value_cz: '3,18 / 2,06 / 1,42 / 1,09 : 1', value_en: '3.18 / 2.06 / 1.42 / 1.09 : 1', source: FS },
  { cz: 'Převod zadní osy', en: 'Final drive', value_cz: '1 : 4,07 (14/57)', value_en: '1 : 4.07 (14/57)', source: FS },
  { cz: 'Spojka', en: 'Clutch', value_cz: 'dva kotouče, suchá', value_en: 'two plates, dry', source: FS },
  { cz: 'Brzdy', en: 'Brakes', value_cz: 'bubnové, Ø 200 mm', value_en: 'drum, 200 mm dia.', source: FS },
  { cz: 'Ráfky', en: 'Rims', value_cz: '3 × 19 palce', value_en: '3 × 19 in', source: FS },
  { cz: 'Rozvor', en: 'Wheelbase', value_cz: '1380 mm', value_en: '1380 mm', source: FS },
  { cz: 'Délka × šířka × výška', en: 'Length × width × height', value_cz: '2100 × 900 × 940 mm', value_en: '2100 × 900 × 940 mm', source: FS },
  { cz: 'Objem nádrže', en: 'Tank capacity', value_cz: '14 l', value_en: '14 L', source: FS },
  { cz: 'Pohotovostní hmotnost', en: 'Weight (fuelled)', value_cz: '185 kg (fact sheet), 188 kg (příručka)', value_en: '185 kg (fact sheet), 188 kg / 414 lb (manual)', source: `${FS}; ${IB}, p. 6` },
  { cz: 'Výška sedla', en: 'Saddle height', value_cz: '0,70 m', value_en: '0.70 m (2 ft 3½ in)', source: `${IB}, p. 6` },
  { cz: 'Objem oleje v motoru', en: 'Engine oil capacity', value_cz: '3¾ pinty (přibl. 2,1 l)', value_en: '3¾ pints (about 2.1 L)', source: `${IB}, p. 6` },
  { cz: 'Nosnost', en: 'Load capacity', value_cz: '300 kg (fact sheet), 210 kg (příručka)', value_en: '300 kg (fact sheet), 210 kg / 460 lb (manual)', source: `${FS}; ${IB}, p. 6` },
  { cz: 'Spotřeba paliva', en: 'Fuel consumption', value_cz: '3,5–4 l / 100 km', value_en: '3.5–4 L / 100 km', source: FS },
  { cz: 'Spotřeba oleje', en: 'Oil consumption', value_cz: '1–2 l / 1000 km', value_en: '1–2 L / 1000 km', source: FS },
  { cz: 'Cena nová', en: 'Original price', value_cz: '1 630 RM', value_en: '1,630 RM', source: FS },
];

export const ABOUT = {
  cz: 'BMW R 12 přišla v roce 1935 jako první motocykl na světě s teleskopickou vidlicí a hydraulickým tlumením. Motor zůstal po modelu R 11, novinkou byl lisovaný ocelový rám a právě vidlice. Do roku 1942 se jich postavilo 36 000, většina šla armádě a úřadům. Díky tomu byla R 12 nejprodávanějším předválečným BMW. Tahle verze je civilní, s jedním karburátorem SUM, 745 cm³ a 18 koňmi. Příručka z roku 1936 ji řadí do nové třídy 750 cm³ jako cestovní model, zatímco R 17 je sportovní.',
  en: 'The BMW R 12 arrived in 1935 as the first motorcycle in the world with a telescopic fork and hydraulic damping. The engine was carried over from the R 11, the news was the pressed-steel frame and that fork. 36,000 were built up to 1942, most of them for the army and government agencies, which made the R 12 the best-selling pre-war BMW. This build is the civilian one with a single SUM carburettor, 745 cc and 18 hp. The 1936 instruction book places it in the new 750 cc class as the touring model, with the R 17 as the sports one.',
  sources: [FS, `${IB}, preface (p. 5)`],
};

export const OPEN_QUESTIONS = [
  'Hmotnost: fact sheet 185 kg, příručka (p. 6, sloupec R 12 1 karb.) 188 kg. Rozpor, v SPECS jsou obě hodnoty.',
  'Nosnost: fact sheet 300 kg, příručka (p. 6) 210 kg. Rozpor, v SPECS jsou obě hodnoty.',
  'Svíčky: příručka Bosch DM 175/1, fact sheet Bosch M 175 T1 nebo W 175 T1. Nesjednocuji, v textu jsou obě.',
  'Dynamo: fact sheet uvádí Bosch D 2 BRS 170 bez vazby na verzi s magnetem nebo baterií.',
  'Pneumatiky: fact sheet 3,5 × 19, příručka 26 × 3,50 palce na ráfku 19 × 3. Pravděpodobně jen jiné značení.',
  'Výměna olejového filtru: text příručky (p. 14) 7500–10 000 mil, obrázek 2 7500–9000 mil. V LUBE jsou obě.',
  'Fact sheet uvádí „magneto or battery ignition“, příručka přiřazuje jednokarburátorové R 12 magneto s baterií jen pro stání. Texty berou verzi s magnetem.',
  'Příručka mazací plán (Fig. 1 a 2) ukazuje na dvoukarburátorové R 12 a R 17. Mazací body platí podle příručky i pro tuto verzi, ale snímek nese jiný stroj.',
  'Sedlo, zadní světlo, klakson, výfuk: příručka je buď nepopisuje, nebo jen okrajově. Texty jsou záměrně krátké.',
  'Tlumič řízení: příručka mluví jednou o křídlové matici (p. 10), jednou o šroubu (p. 7, obr. 4). Princip neuvádí.',
  'Předmluva je datovaná říjen 1936 (p. 5), tiráž říká X. 36. OCR „1956“ byla chyba čtení.',
  'Žádné z 33 id na civilní 1karb. R 12 nesedí. Příručka ale pro 2karb. verzi popisuje jiné díly (dva karburátory Amal, baterie se cívkou a rozdělovačem). Texty berou jen verzi 1 karb.',
];

// German texts live in de.js; attach them here so every record carries cz, en and de
for (const [id, p] of Object.entries(PARTS)) {
  const d = DE_PARTS[id];
  if (!d) continue;
  p.de = { title: d.title, text: d.text, data: d.data, care: d.care };
  if (d.unverified) p.unverified = p.unverified.map((u, i) => (typeof u === 'string' ? u : { ...u, de: d.unverified[i] ?? u.en }));
}
LUBE.forEach((l, i) => { [l.de, l.every_de, l.lubricant_de] = DE_LUBE[i]; });
SPECS.forEach((sp, i) => { [sp.de, sp.value_de] = DE_SPECS[i]; });
ABOUT.de = DE_ABOUT;
