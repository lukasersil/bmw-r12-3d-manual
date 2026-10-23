// German texts (DE), merged into content.js and media.js by id or by position. Same facts and sources as the
// Czech and English versions; distances from the English manual converted to km like the Czech ones.

export const DE_PARTS = {
  cylinders: {
    title: 'Zylinder und Zylinderköpfe',
    text: 'Zwei gegenüberliegende Zylinder ragen seitlich aus dem Kurbelgehäuse. Die Ventile sind seitlich angeordnet, vollständig gekapselt und werden über Stößel von der Nockenwelle betätigt. Öl, das an den Stößeln vorbeikriecht, läuft durch eine Rücklaufbohrung ins Gehäuse zurück, deshalb bleibt der Motor außen sauber. Die Kolben sind aus Leichtmetall und haben drei Ringe, der unterste streift das Öl ab.',
    data: [
      ['Bauart', 'Zweizylinder-Boxer'],
      ['Bohrung × Hub', '78 × 78 mm'],
      ['Hubraum', '745 cm³'],
      ['Verdichtung', '5,2 : 1'],
      ['Leistung', '18 PS bei 3400 U/min'],
    ],
    care: 'Das Ventilspiel nur bei kaltem Motor prüfen, es soll etwa 0,1 mm betragen. An die Ventilkammer kommt man nach Abnehmen des Deckels. Die Muttern an Zylinderköpfen und Ansaugrohren vor allem in den ersten Kilometern nachziehen.',
  },
  carburettor: {
    title: 'SUM-Vergaser',
    text: 'Die R 12 mit einem Vergaser hat einen SUM-Vergaser mit drei Düsen: zwei Hauptdüsen und eine Leerlaufdüse. Der rechte Drehgriff zieht über einen Bowdenzug den Gasschieber. Für den Kaltstart wird der Startkolben herausgezogen und verdreht. Sobald der Motor warm ist, muss er wieder geschlossen werden, sonst steigt der Verbrauch und die Kerzen verrußen.',
    data: [
      ['Typ', 'SUM, ein Vergaser'],
      ['Düsen', '3 (2 Haupt-, 1 Leerlaufdüse)'],
    ],
    care: 'Das Sieb im Deckel der Schwimmerkammer, die Düsen und das Nadelventil reinigen. Die Schwimmerkammer etwa alle 3200 bis 4000 km mit Benzin ausspülen. Düsen nie mit einer Nadel durchstechen.',
  },
  intake: {
    title: 'Ansaugrohr und Luftfilter',
    text: 'Das Ansaugrohr wird von den Abgasen beheizt, so bildet sich das Gemisch auch bei Kälte gut. Auf den Vergaser ist ein Luftfilter geschraubt. Die Kupferwolle in den Entlüftungsstopfen der Gabel wird genauso gereinigt wie diese Filter.',
    data: [],
    care: 'Den Filter ab und zu in Benzin auswaschen, in angewärmtes Öl tauchen und das überschüssige Öl gründlich ausschütteln. Die Muttern des Ansaugrohrs gehören zu denen, die man anfangs nachziehen muss.',
  },
  exhaust: {
    title: 'Auspuff',
    text: 'Das Rohr führt von der Stirnseite des Zylinderkopfs vor dem Zylinder nach unten und unter dem Trittbrett nach hinten in den Schalldämpfer, der in einem flachen Fischschwanz endet. Auf dem Weg nach außen heizen die Abgase das Ansaugrohr, so bildet sich das Gemisch auch bei Kälte gut. Werden die Zylinder abgenommen, kommen die Rohre zusammen mit dem Vergaser herunter.',
    data: [],
    care: null,
  },
  crankcase: {
    title: 'Kurbelwelle und Kurbelgehäuse',
    text: 'Das Kurbelgehäuse ist zugleich der Öltank. Die Kurbelwelle aus Stahl mit gehärteten Zapfen läuft bei der R 12 in Kugellagern. Eine Zahnradpumpe im Gehäuseunterteil saugt das Öl durch einen Filter an und drückt es durch Bohrungen zu den Lagern. Eine geräuschlose Kette treibt die Nockenwelle über der Kurbelwelle an. Ein Drehschieber entlüftet das Gehäuse, hält einen leichten Überdruck und so das Öl im Inneren.',
    data: [
      ['Schmierung', 'Druckumlauf, Zahnradpumpe'],
      ['Ölmenge', '3¾ Pint (etwa 2,1 l)'],
    ],
    care: 'Den Filter nur mit Spülöl reinigen, nie mit Benzin.',
    unverified: ['Ölfilter-Intervall: der Handbuchtext S. 14 nennt 7500–10 000 Meilen, Fig. 2 7500–9000 Meilen'],
  },
  ignition: {
    title: 'Zündung (Magnet)',
    text: 'Die R 12 mit einem Vergaser hat einen kombinierten Licht-Zünd-Magnet. Er liefert Zündstrom und Lichtstrom getrennt. Unterbrecher und Hochspannungsverteiler sitzen in derselben Einheit. Den Zündzeitpunkt verstellt der Drehgriff links am Lenker. Eine Kette von der Nockenwelle treibt den Magnet an.',
    data: [
      ['Kontaktabstand', '0,3–0,4 mm'],
      ['Kontakte nachstellen', 'etwa alle 4800 km'],
    ],
    care: 'Die Kontakte mit einem sauberen Lappen reinigen, nie mit Schmirgel, und von Öl freihalten. Beim Abspritzen des Motorrads den Magnet abdecken. Bei der jährlichen Durchsicht von einem Bosch-Dienst prüfen lassen.',
  },
  generator: {
    title: 'Lichtmaschine',
    text: 'Die Lichtmaschine sitzt im selben Gehäuse wie der Magnet und erzeugt den Strom für die Beleuchtung. Dank eines schnellen Reglers im Inneren fährt das Motorrad auch bei abgeklemmter Batterie. Die Batterie versorgt das Licht nur bei stehendem Motor.',
    data: [
      ['Typ (Datenblatt)', 'Bosch D 2 BRS 170'],
    ],
    care: 'Lichtmaschine und Magnet nicht mit Wasser abspritzen. Das Fett in Lagern und Getriebe sollte ein Bosch-Dienst bei der Generalüberholung erneuern.',
    unverified: ['das Datenblatt nennt Bosch D 2 BRS 170 als „Alternator“, ohne zu sagen, zu welcher Ausführung (Magnet oder Batterie) sie gehört'],
  },
  sparkplugs: {
    title: 'Zündkerzen',
    text: 'Jeder Zylinder hat eine Kerze. Das Handbuch erlaubt nur zugelassene Typen, die auch unter hoher Last keine Glühzündung verursachen. Verrußte Kerzen sind die typische Folge eines offen gelassenen Startkolbens.',
    data: [
      ['Typ (Handbuch)', 'Bosch DM 175/1'],
      ['Typ (Datenblatt)', 'Bosch M 175 T1 oder W 175 T1'],
    ],
    care: 'Nur die vorgeschriebenen Kerzen verwenden. Die beiden Quellen nennen sie unterschiedlich, daher den Typ am Motorrad prüfen.',
    unverified: ['das Handbuch S. 19 nennt Bosch DM 175/1, das Datenblatt Bosch M 175 T1 oder W 175 T1'],
  },
  kickstarter: {
    title: 'Kickstarter',
    text: 'Der Hebel sitzt hinter dem linken Trittbrett. Die Kickstarterwelle liegt wie die Getriebewellen längs, deshalb steht der Hebel seitlich ab und wird quer zur Maschine nach unten getreten, der geriffelte Pedalgummi zeigt nach hinten. Beim Treten dreht ein Zahnsegment zwei Stirnräder, die über die Kupplung die Getriebehauptwelle durchdrehen. In Ruhestellung gibt eine Klaue die Innenverzahnung frei, das Rad läuft dann leer. Gestartet wird im Leerlauf.',
    data: [],
    care: 'Vorher den Benzinhahn öffnen und den Zündschlüssel im Scheinwerfer eindrücken. Kräftig und mit vollem Hub treten.',
  },
  clutch: {
    title: 'Kupplung',
    text: 'Auf dem Schwungrad sitzt eine trockene Zweischeibenkupplung. Sechs Federn drücken eine Druckplatte gegen beidseitig belegte Reibscheiben, dazwischen liegt eine Mitnehmerscheibe. Der Hebel links am Lenker zieht über einen Bowdenzug einen Hebel am Getriebe und hebt so die Druckplatte von den Scheiben ab.',
    data: [
      ['Bauart', 'zwei Scheiben, trocken'],
      ['Federn', '6'],
    ],
    care: 'Beim Einstellen der Bremsen auch den Kupplungszug prüfen. Der Hebel braucht Spiel, sonst verschleißt der Belag unnötig.',
  },
  gearbox: {
    title: 'Vierganggetriebe',
    text: 'Ein handgeschaltetes Vierganggetriebe. Die Räder auf der Hauptwelle stehen ständig im Eingriff mit lose laufenden Rädern auf der Abtriebswelle. Schiebemuffen mit Klauen wählen den Gang. Getriebe und Motor bilden einen Block, und in das Gehäuse ist ein Werkzeugbehälter eingegossen.',
    data: [
      ['1. Gang', '3,18 : 1'],
      ['2. Gang', '2,06 : 1'],
      ['3. Gang', '1,42 : 1'],
      ['4. Gang', '1,09 : 1'],
    ],
    care: 'Getriebereparaturen dem Fachmann überlassen.',
  },
  gearlever: {
    title: 'Schalthebel',
    text: 'Der Hebel läuft in einer Kulisse, die zugleich das rechte Kniekissen bildet. Geschaltet wird von Hand. Beim Hochschalten auskuppeln und Gas wegnehmen, beim Herunterschalten etwa Halbgas geben. Gänge zu überspringen wird nicht empfohlen.',
    data: [],
    care: 'Der erste Gang dient nur zum Anfahren. Im dichten Stadtverkehr genügt der zweite oder dritte.',
  },
  driveshaft: {
    title: 'Kardanwelle',
    text: 'Die Kraft geht vom Getriebe über eine elastische Gummikupplung auf die Kardanwelle. Eine Zahnkupplung dahinter gleicht Längsbewegungen aus. Die Welle treibt dann den Kegelradsatz an.',
    data: [],
    care: null,
  },
  reardrive: {
    title: 'Hinterradantrieb',
    text: 'Ein schrägverzahnter Kegelradsatz treibt das Hinterrad über eine Keilverzahnung an und läuft fast geräuschlos. Der untere Teil des Gehäuses ist zugleich der Ölbehälter. Den Ölstand zeigt ein Messstab mit Sechskantkopf auf der linken Seite.',
    data: [
      ['Übersetzung Hinterachse', '1 : 4,07'],
      ['Ritzel / Tellerrad', '14 / 57 Zähne'],
    ],
    care: 'Öl bis zum unteren Gewinde auffüllen, nie über den oberen Ring.',
  },
  frame: {
    title: 'Pressstahlrahmen',
    text: 'Der Rahmen aus gepresstem Stahl war die große Neuerung gegenüber der R 11, deren Motor übernommen wurde. Es ist ein Doppelrahmen aus Stahlpressteilen mit U-Profil, als Dreiecksverband versteift. Vorn umfassen die beiden Hälften den Lenkkopf im Halbkreis und sind dahinter durch gepresste Knotenbleche verbunden. Der untere Holm läuft unter Motor und Getriebe gerade nach hinten und biegt vor der Hinterachse in einem Bogen nach oben in den oberen Holm. Vor dem Hinterrad versteift eine einteilige, dem Kotflügel folgende gebogene Strebe beide Seiten. Motor und Getriebe bilden einen im Rahmen aufgehängten Block. Eine Hinterradfederung gibt es nicht, das Heck ist starr.',
    data: [
      ['Radstand', '1380 mm'],
      ['Hinterradfederung', 'keine (starrer Rahmen)'],
    ],
    care: 'Alle Muttern und Schrauben anfangs in kurzen Abständen prüfen, auch am hinteren Kotflügel und am Gepäckträger.',
  },
  fork: {
    title: 'Teleskopgabel',
    text: 'BMW stellte sie als erste ihrer Art vor: ineinander gleitende Rohre, innen Schraubenfedern und einstellbare Ventile der Öldämpfung. Sie fängt Stöße weich und fast reibungsfrei ab und dämpft den Rückschlag. Öl wird nur bei Reparaturen eingefüllt, die oberen Stopfen dienen zugleich der Entlüftung.',
    data: [
      ['Bauart', 'Teleskopgabel, hydraulisch gedämpft'],
    ],
    care: 'Nach einer Reparatur kommt etwa ¼ Pint (rund 0,14 l) Stoßdämpferöl in jedes Bein. Die Stopfen mit Kupferwolle wie die Luftfilter reinigen. Die Lenkkopflager bei der jährlichen Durchsicht neu fetten.',
  },
  steeringdamper: {
    title: 'Lenkungsdämpfer',
    text: 'Mit einer großen Flügelmutter in der Lenkermitte wird die Lenkung je nach Straße fester oder leichter gestellt.',
    data: [],
    care: 'Anziehen macht die Lenkung schwerer, Lösen leichter.',
  },
  frontwheel: {
    title: 'Vorderrad',
    text: 'Felge 3 × 19 Zoll mit doppelt starken Endspeichen. Das Rad hält eine Steckachse, die nach Lösen der Klemmschraube am linken Gabelbein herausgeschraubt wird. Vorder-, Hinter- und bei Gespannen das Seitenwagenrad sind austauschbar. Innen liegt die Trommelbremse.',
    data: [
      ['Felge', '3 × 19 Zoll'],
      ['Reifen', '3,5 × 19'],
    ],
    care: 'Reifendruck ohne Seitenwagen etwa 1,0 bar.',
    unverified: ['Reifen: Datenblatt 3,5 × 19, Handbuch S. 6 und 34 nennt 26 × 3,50 Zoll'],
  },
  rearwheel: {
    title: 'Hinterrad',
    text: 'Gleich wie das Vorderrad, nur wird es über eine Keilverzahnung vom Kegelradsatz angetrieben. Das hintere Kotflügelende lässt sich abnehmen, so kommt das Rad heraus, ohne die Maschine zu kippen. Bei der Solomaschine wird die Steckachse durch Rechtsdrehen herausgeschraubt.',
    data: [
      ['Felge', '3 × 19 Zoll'],
      ['Reifen', '3,5 × 19'],
    ],
    care: 'Beim Reifenwechsel keinen Schmutz an die Verzahnung lassen und das Rad nur auf völlig saubere Verzahnung aufsetzen. Luftdruck solo etwa 1,45 bar.',
  },
  brakes: {
    title: 'Innenbackenbremsen',
    text: 'Beide Bremsen sind Innenbackenbremsen und gegen Wasser und Schmutz vollständig gekapselt. Die vordere wird mit dem rechten Handhebel betätigt, die hintere mit dem Fußhebel. Laut Handbuch bremst man mit beiden zugleich, in Kurven nur hinten und auf langen Gefällen abwechselnd mit Hand- und Fußbremse.',
    data: [
      ['Trommeldurchmesser', '200 mm (vorn und hinten)'],
    ],
    care: 'Die Vorderbremse mit der Flügelschraube am Bremsdeckel nachstellen, die Hinterbremse mit der Flügelmutter an der Zugstange. In den Hebeln immer etwas Spiel lassen. Dabei auch den Kupplungszug prüfen.',
  },
  fenders: {
    title: 'Kotflügel',
    text: 'Der hintere Kotflügel hat ein abnehmbares Ende. So lässt sich das Hinterrad ausbauen, ohne die Maschine zu kippen oder anzuheben, was vor allem Gespannfahrer schätzen. Bei der Seitenwagenmaschine muss zuerst das Schlusslicht abgeschraubt werden.',
    data: [],
    care: 'Die Befestigung von Kotflügeln und Gepäckträger in den ersten Kilometern prüfen.',
  },
  stand: {
    title: 'Kippständer',
    text: 'Jede Maschine hat unter dem Rahmen zwei Kippständer, die von Federn hochgehalten werden. Auf den Ständern wird das Motorrad so weit angehoben, dass sich die Räder leicht ausbauen lassen.',
    data: [
      ['Anzahl', '2 (vorn und hinten)'],
    ],
    care: null,
  },
  saddle: {
    title: 'Sattel',
    text: 'Der Sattel liegt 70 cm über dem Boden. Eine lederbezogene Pressschale mit tiefen Seitenteilen, einer Nietreihe und hochgezogenem hinterem Rand. Vorn ist er am Rahmen drehbar gelagert, hinten führt auf jeder Seite eine Stange senkrecht nach unten in eine Schraubenfeder, die unter einer Lasche am oberen Rahmenholm hängt.',
    data: [
      ['Sitzhöhe', '0,70 m'],
    ],
    care: null,
  },
  tank: {
    title: 'Kraftstoffbehälter',
    text: 'Der Tank fasst 14 Liter. Unten sitzt ein Kraftstoffhahn mit Wasserabscheider und Sieb. Empfohlen ist Benzin und Benzol zu gleichen Teilen, während des Einfahrens wird ein Obenschmiermittel beigemischt. Der Verbrauch liegt bei 3,5 bis 4 Litern auf 100 km.',
    data: [
      ['Tankinhalt', '14 l'],
      ['Kraftstoffverbrauch', '3,5–4 l / 100 km'],
      ['Ölverbrauch', '1–2 l / 1000 km'],
    ],
    care: 'Vor dem Start den Hahn öffnen, nach dem Abstellen schließen. Wasserabscheider und Sieb im Hahn ab und zu reinigen.',
  },
  handlebar: {
    title: 'Lenker',
    text: 'Die meisten Bedienelemente sitzen am Lenker. Rechts Gasdrehgriff, Hupenknopf, Abblendschalter und Handbremshebel. Links Kupplungshebel, Zünddrehgriff und Kurzschlussknopf. In der Mitte die Mutter des Lenkungsdämpfers.',
    data: [],
    care: 'Züge und Kabel am Lenker etwa alle 3200 km auf Scheuerstellen prüfen.',
  },
  throttle: {
    title: 'Gasdrehgriff',
    text: 'Der rechte Drehgriff betätigt über einen Bowdenzug den Vergaserschieber. Nach hinten gedreht öffnet er, nach vorn schließt er. Der Zug hat am Schieber eine Stellschraube.',
    data: [],
    care: 'Zum Einstellen des Leerlaufs den Zug lockern und das Spiel danach wieder herausnehmen.',
  },
  advance: {
    title: 'Zündverstellung',
    text: 'Der linke Drehgriff verdreht über einen Bowdenzug den Unterbrecher. Nach außen, vom Fahrer weg, gedreht gibt er Frühzündung, nach innen Spätzündung. Immer mit Spätzündung starten, sonst kann der Motor zurückschlagen.',
    data: [],
    care: 'Klopft der Motor, besonders bergauf, auf Spät stellen, bis es aufhört. Bei voller Reisegeschwindigkeit in der Ebene ganz auf Früh fahren.',
  },
  footbrake: {
    title: 'Fußbremse',
    text: 'Der Hebel liegt hinter dem rechten Trittbrett und betätigt die hintere Trommelbremse. In Kurven bremst nur er. Auf langen Gefällen wechselt man mit der Handbremse ab, damit sich nicht beide zugleich erhitzen.',
    data: [],
    care: 'Die Hinterbremse mit der Flügelmutter an der Bremsstange nachstellen. Die Gelenke des Gestänges alle 320 bis 480 km ölen.',
  },
  killbutton: {
    title: 'Kurzschlussknopf',
    text: 'Die R 12 mit einem Vergaser hat links am Lenker einen Knopf, der die Zündung kurzschließt. Damit stellt man am Fahrtende den Motor ab und nimmt in einer Kurve oder vor einem plötzlichen Hindernis schnell Fahrt weg.',
    data: [],
    care: 'Der Motor lässt sich auch mit dem Zündschlüssel im Scheinwerfer abstellen. Nach dem Abstellen den Benzinhahn schließen.',
  },
  headlamp: {
    title: 'Scheinwerfer',
    text: 'Im Scheinwerfer sitzen eine Zweifadenlampe für Fern- und Abblendlicht und eine Parklampe. Der Schlüssel oben schaltet Zündung und Licht, eine rote Kontrolllampe leuchtet bei eingeschalteter Zündung. Der Tachometer sitzt im Scheinwerfer und wird über eine Schnecke vom Getriebe angetrieben.',
    data: [],
    care: 'Die rote Kontrolllampe bei längerem Halt nicht brennen lassen, sonst entlädt sich die Batterie über die Lichtmaschine.',
  },
  battery: {
    title: 'Batterie',
    text: 'Die Batterie steht hinter dem Getriebe auf dem linken unteren Rahmenholm, direkt vor dem Hinterreifen. Bei der Maschine mit einem Vergaser speist sie nur das Licht im Stand. Zündung und Fahrlicht liefern Magnet und Lichtmaschine, deshalb fährt das Motorrad auch mit abgeklemmter Batterie.',
    data: [],
    care: 'Die Batterie alle 4 bis 6 Wochen prüfen, ob gefahren wird oder nicht. Laden und Pflege nach Bosch-Vorschrift.',
  },
  taillight: {
    title: 'Schlusslicht',
    text: 'Bei der Seitenwagenmaschine muss das Schlusslicht abgeschraubt werden, bevor das hintere Kotflügelende abgenommen wird.',
    data: [],
    care: null,
  },
  horn: {
    title: 'Hupe',
    text: 'Die Hupe sitzt vorn zwischen den beiden Rahmenholmen unter dem Emblemblech und zeigt nach vorn. Ihr Knopf ist am rechten Lenkergriff.',
    data: [],
    care: null,
  },
};

// LUBE in content.js order: [point, interval, lubricant]
export const DE_LUBE = [
  ['Motor, Ölstand (Messstab)', 'alle 400 km prüfen, bis zum oberen Ring auffüllen', 'Gargoyle Mobiloil BB, im Winter Arctic, bei Hitze D'],
  ['Motor, Ölwechsel', 'alle 1900 km (beim Einfahren alle 480 km), Filter alle 12 000–16 000 km', 'Gargoyle Mobiloil BB'],
  ['Einfüllöffnung Getriebe', 'alle 970 km prüfen, bis zum unteren Gewinde auffüllen; nach dem Einfahren Öl wechseln', 'Gargoyle Mobiloil BB'],
  ['Hinterradantrieb (Kegelradgehäuse)', 'alle 970 km prüfen, Wechsel nach dem Einfahren, dann etwa alle 16 000 km', 'Gargoyle Mobiloil D'],
  ['Magnet, Klappöler', 'alle 1900 km, Öl nachfüllen, bis es am zweiten Öler austritt', 'Motoröl wie für den Motor'],
  ['Schmiernippel der Radnaben', 'alle 970 km mit der Fettpresse', 'Gargoyle Mobilgrease Nr. 4, nie gewöhnliches Fett'],
  ['Bremsgestänge und Bowdenzüge', 'alle 320–480 km', 'Öl'],
  ['Öldämpfer der Gabel', 'keine regelmäßige Schmierung, nur verlorenes Öl ergänzen, bei Reparatur erneuern', 'Stoßdämpferöl'],
];

// SPECS in content.js order: [label, value]
export const DE_SPECS = [
  ['Baujahre', '1935–1942'],
  ['Gebaute Stückzahl', '36 000'],
  ['Hubraum', '745 cm³'],
  ['Bohrung × Hub', '78 × 78 mm'],
  ['Leistung', '18 PS bei 3400 U/min'],
  ['Verdichtung', '5,2 : 1'],
  ['Höchstgeschwindigkeit', '110 km/h'],
  ['Getriebeübersetzungen', '3,18 / 2,06 / 1,42 / 1,09 : 1'],
  ['Hinterachsübersetzung', '1 : 4,07 (14/57)'],
  ['Kupplung', 'zwei Scheiben, trocken'],
  ['Bremsen', 'Trommel, Ø 200 mm'],
  ['Felgen', '3 × 19 Zoll'],
  ['Radstand', '1380 mm'],
  ['Länge × Breite × Höhe', '2100 × 900 × 940 mm'],
  ['Tankinhalt', '14 l'],
  ['Gewicht fahrfertig', '185 kg (Datenblatt), 188 kg (Handbuch)'],
  ['Sitzhöhe', '0,70 m'],
  ['Ölmenge Motor', '3¾ Pint (etwa 2,1 l)'],
  ['Zuladung', '300 kg (Datenblatt), 210 kg (Handbuch)'],
  ['Kraftstoffverbrauch', '3,5–4 l / 100 km'],
  ['Ölverbrauch', '1–2 l / 1000 km'],
  ['Neupreis', '1630 RM'],
];

export const DE_ABOUT = 'Die BMW R 12 kam 1935 als erstes Motorrad der Welt mit hydraulisch gedämpfter Teleskopgabel. Der Motor stammte von der R 11, neu waren der Pressstahlrahmen und eben diese Gabel. Bis 1942 entstanden 36 000 Stück, die meisten gingen an Militär und Behörden. Damit war die R 12 das meistverkaufte BMW-Motorrad der Vorkriegszeit. Diese Ausführung ist die zivile mit einem SUM-Vergaser, 745 cm³ und 18 PS. Das Handbuch von 1936 ordnet sie in die neue 750-cm³-Klasse als Tourenmaschine ein, die R 17 als Sportmaschine.';

export const DE_MEDIA = {
  f01: { title: 'Rechte Seite mit Schmierplan', text: 'Die rechte Seite gezeichnet, mit Hinweisen, was wie oft geschmiert wird: Hinterradantrieb, Getriebe, Kurbelgehäuse, Gabel und Bremsgestänge. Die Zeichnung zeigt die R 12 mit zwei Vergasern, die Schmierstellen gelten auch für die Ausführung mit einem Vergaser.' },
  f03: { title: 'Rechtes Lenkerende', text: 'Gasdrehgriff mit Öffnungs- und Schließrichtung, Abblendschalter, Hupenknopf und Handbremshebel.' },
  f04: { title: 'Bedienelemente von oben', text: 'Die ganze Maschine von oben mit allen Bedienelementen: Schlüssel und Tachometer im Scheinwerfer, Lenkungsdämpfer, Kupplung und Zünddrehgriff links, Gas, Hupe und Vorderbremse rechts, Schalthebel am Tank, Kickstarter und Fußbremse.' },
  f05: { title: 'Linkes Lenkerende', text: 'Kupplungshebel und Zünddrehgriff, Frühzündung vom Fahrer weg, Spätzündung zum Fahrer hin.' },
  f06: { title: 'Schalthebel', text: 'Die Kulisse am rechten Kniekissen mit erstem bis viertem Gang und Leerlauf. Der Hebel mit Kugelknopf führt nach unten zum Getriebe.' },
  f07: { title: 'Vorderbremse', text: 'Die vordere Trommelbremse mit ihrem Bowdenzug. Das Spiel wird mit der Flügelschraube in der Mitte des Bremsdeckels eingestellt.' },
  f08: { title: 'Hinterbremse', text: 'Der Hinterradantrieb mit der Bremsstange und der Flügelmutter b an ihrem Ende. Rechts die offen liegende Kardanwelle und der Schalldämpfer.' },
  f10: { title: 'Unterbrecher am Magnet', text: 'Der Unterbrecher des Licht-Zünd-Magnets der R 12 mit einem Vergaser. Der Hebel rechts verstellt den Zündzeitpunkt zwischen früh und spät.' },
  f11: { title: 'Ventilspiel einstellen', text: 'Der Ventilkammerdeckel ist abgenommen, zwei Schlüssel sitzen am Stößel. Das Spiel wird kalt auf 0,1 mm eingestellt.' },
  f14: { title: 'SUM-Vergaser', text: 'Drei Schnitte durch den SUM-Vergaser: Gasschieber, Schwimmerkammer, Düsen und der Startkolben 20 mit seinem Knopf 22 für den Kaltstart.' },
  f17: { title: 'Zweischeibenkupplung', text: 'Schnitt durch das Schwungrad: sechs Federn drücken die Druckplatte auf zwei belegte Scheiben mit einer Mitnehmerscheibe dazwischen.' },
  f18: { title: 'Kraftübertragung', text: 'Das Getriebe im Leerlauf und in allen vier Gängen, von der Kurbelwelle über die Kupplung bis zur Kardanwelle.' },
  f19: { title: 'Scheinwerfer von oben', text: 'In der Mitte der Zünd- und Lichtschlüssel, davor der Tachometer, links die Kontrolllampe und rechts der Sicherungsstopfen. Durch Drehen des Schlüssels wählt man Park- oder Fernlicht.' },
  f20: { title: 'Motorschnitt', text: 'Der linke Zylinder aufgeschnitten: das Ventil liegt neben der Bohrung (seitengesteuerter Motor), Kolben, Pleuel, Kurbelwelle, unten die Ölpumpe und oben der Magnet. Der rechte Zylinder ist von außen gezeichnet.' },
  f23: { title: 'Vorderrad ausbauen', text: 'Klemmschraube 1 am linken Gabelbein, Schlüssel 2, Steckachse 3 und Distanzstück 4.' },
  f24: { title: 'Hinterrad ausbauen', text: 'Eine Solomaschine auf rechtes Trittbrett und Zylinder gelegt, Steckachse 5 und Distanzstück 6 heraus. Am hinteren Kotflügel ein zeitgenössisches Kennzeichen, IIA 362.' },
  f25: { title: 'Hinterrad, Seitenwagenmaschine', text: 'Mit Seitenwagen bleibt die Maschine auf dem hinteren Ständer, und das hintere Kotflügelende wird abgenommen.' },
  p_head: { title: 'Rechter Zylinderkopf und Auspuff', text: 'Eine R 12 bei einer Veteranenfahrt in Wilster 2018: gerippter Aluminiumkopf, Zündkerze, Auspuffrohr, das Rahmenknotenblech mit Emailleemblem und die Hupe vor dem vorderen Rahmenholm.' },
  p_left: { title: 'Linke Motorseite', text: 'Eine unrestaurierte R 12: SUM-Vergaser und Schwimmerkammer, Ansaugrohr aus Aluminium, Lichtmaschine, Batterie hinter dem Getriebe und der runde Deckel des Werkzeugbehälters.' },
  p_side: { title: 'Linke Seite', text: 'Eine R 12 im originalen, unrestaurierten Zustand, mit verblassten Linien und Patina.' },
  p_tail: { title: 'Schalldämpferende', text: 'Die geschossförmige Spitze des Schalldämpfers und der flache Fischschwanz, der aus ihr herauswächst.' },
  p_front: { title: 'Front, Baujahr 1940', text: 'Gabelverkleidungen mit Doppellinie, der vordere Kotflügel mit löffelförmigem Ende und das gebogene vordere Kennzeichen.' },
  p_tank: { title: 'Tank und Schaltkulisse', text: 'Eine R 12 von 1940 aus der Sammlung der BMW Mobile Tradition: linierter Tank, Kniekissen mit Schaltkulisse und Hebel, Tankdeckel.' },
  p_rear: { title: 'Gepäckträger und Schlusslicht', text: 'Verchromter Gepäckträger, tropfenförmiges Schlusslicht und darunter das hintere Kennzeichen (an dieser Maschine ein modernes).' },
  p_drive: { title: 'Hinterradantrieb', text: 'Der Aluminiumdeckel des Hinterradantriebs mit Schrauben und Einfüllschraube, dahinter das Fischschwanzende des Schalldämpfers.' },
  p_engine: { title: 'Motor von rechts', text: 'Der Motor einer R 12 von 1940: schwarzer Graugusszylinder, gerippter Aluminiumkopf, Ansaugrohr aus Aluminium zur Ventilkammer und oben die Zündkerze.' },
  p_1936: { title: 'Maschine von 1936 von vorn', text: 'Eine R 12 von 1936 im Niederrheinischen Motorradmuseum: Scheinwerfer, Lenker, der linierte vordere Kotflügel und der vordere Bremsdeckel.' },
  p_fork: { title: 'Teleskopgabel', text: 'Eine R 12-Gabel von etwa 1937 in Militärausführung (graue Lackierung, WL-Kennzeichen). Die Verkleidungen haben dieselbe Form wie bei der Zivilmaschine.' },
};
