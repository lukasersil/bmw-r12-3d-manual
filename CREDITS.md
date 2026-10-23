# Prameny a cizí obsah / Sources and third-party material

> Neoficiální fanouškovský projekt, nevznikl ve spolupráci s BMW AG ani BMW Group Classic. BMW, logo BMW a označení modelů jsou ochranné známky BMW AG; v modelu jsou jen jako součást věrné repliky historického stroje a licence tohoto repa k nim nedává žádná práva.
>
> Unofficial fan project, not made with or endorsed by BMW AG or BMW Group Classic. BMW, the BMW logo and model names are trademarks of BMW AG; they appear only as part of a faithful replica of a historic machine, and the licences of this repository grant no rights to them.

Nic z tohoto seznamu nespadá pod MIT ani CC BY 4.0 tohoto repa. Při dalším použití dodrž licenci každého souboru.
Nothing listed here is covered by this repository's MIT or CC BY 4.0 licences. Follow each file's own licence when you reuse it.

## Fotky z Wikimedia Commons / Photos from Wikimedia Commons (`media/`, `blender/refs/`)

| Soubory / Files | Autor / Author | Licence | Zdroj / Source |
|---|---|---|---|
| `media/p_head.jpg` | Nightflyer | CC BY-SA 4.0 | https://commons.wikimedia.org/wiki/File:Schleswig-Holstein,_Wilster,_Zehnte_Internationale_VFV_ADAC_Zwei-Tage-Motorrad-Veteranen-Fahrt-Norddeutschland_und_33te_Int-Windmill-Rally_NIK_4083.jpg |
| `media/p_left.jpg`, `media/p_side.jpg`, `media/p_tail.jpg` | Tux-Man | CC0 | https://commons.wikimedia.org/wiki/File:BMW_R12.jpg |
| `media/p_front.jpg` | Addvisor | CC BY-SA 4.0 | https://commons.wikimedia.org/wiki/File:BMW_R12_(1940).jpg |
| `media/p_tank.jpg`, `media/p_rear.jpg`, `media/p_drive.jpg`, `blender/refs/c3h_r12_1940_spurzem.jpg` | Lothar Spurzem | CC BY-SA 2.0 DE | https://commons.wikimedia.org/wiki/File:BMW_R_12,_Baujahr_1940,_2006-07-16.jpg |
| `media/p_engine.jpg` | Lothar Spurzem | CC BY-SA 2.0 DE | https://commons.wikimedia.org/wiki/File:2006-07-16_BMW_R_12_-_Motor.JPG |
| `media/p_1936.jpg` | Stahlkocher | CC BY-SA 3.0 | https://commons.wikimedia.org/wiki/File:BMW_R_12_1936.jpg |
| `media/p_fork.jpg` | André Karwath (Aka) | CC BY-SA 2.5 | https://commons.wikimedia.org/wiki/File:BMW_R_12_fork_(circa_1937).jpg |

Fotky jsou oříznuté a zmenšené (`tools/media_spec.py`). Soubory pod CC BY-SA se při dalším šíření musí šířit pod stejnou licencí.
Photos are cropped and scaled (`tools/media_spec.py`). Files under CC BY-SA must be shared under the same licence.

## Dobové příručky BMW / Period BMW documents (`media/f*.jpg`, `blender/refs/etl_r12_1938_partslist.jpg`)

- *Instruction Book R 12 / R 17*, BMW, Mnichov / Munich 1936, sken / scan: BMW Group Archive. Obrázky / figures: Fig. 1 (`media/f01.jpg`), Fig. 3 (`media/f03.jpg`), Fig. 4 (`media/f04.jpg`), Fig. 5 (`media/f05.jpg`), Fig. 6 (`media/f06.jpg`), Fig. 7 (`media/f07.jpg`), Fig. 8 (`media/f08.jpg`), Fig. 10 (`media/f10.jpg`), Fig. 11 (`media/f11.jpg`), Fig. 14 (`media/f14.jpg`), Fig. 17 (`media/f17.jpg`), Fig. 18 (`media/f18.jpg`), Fig. 19 (`media/f19.jpg`), Fig. 20 (`media/f20.jpg`), Fig. 23 (`media/f23.jpg`), Fig. 24 (`media/f24.jpg`), Fig. 25 (`media/f25.jpg`).
- *Ersatzteilliste für die BMW Krafträder R 12 / R 17*, BMW, březen / March 1938: fotka R 12 na s. 4 (`blender/refs/etl_r12_1938_partslist.jpg`), tabule dílů sloužily jako podklad pro tvary.
- Fact sheet *BMW R 12*, BMW Group Archive: technické údaje v textech (vlastními slovy, čísla s odkazem na zdroj).

Skeny jsou v projektu jako citace historických pramenů k jednotlivým dílům, s uvedením zdroje. Autorská práva a vodoznaky zůstávají jejich vlastníkům; nejsou pod licencí tohoto repa. Pokud jsi držitel práv a nesouhlasíš, napiš a skeny odstraním.
The scans are included as cited historical sources for the parts, with their origin. Rights and watermarks remain with their owners; they are not under this repository's licences. If you hold the rights and object, get in touch and they will be removed.

## Logo a ochranné známky / Logo and trademarks

Logo BMW (intro `scene/logo.txt`, znak na nádrži `blender/textures/roundel.png`, nápis na kolenních opěrkách `blender/textures/kneepad.png`) je ochranná známka BMW AG. / The BMW logo (intro, tank badge, knee grips) is a trademark of BMW AG.

## Fotka autora / Author's photo

`assets/avatar.png` je fotka autora, není pod žádnou volnou licencí. Když stránku použiješ pro vlastní projekt, nahraď ji svojí. / `assets/avatar.png` is the author's photo and is not openly licensed; replace it with your own.

## Software a písma / Software and fonts

- [three.js](https://threejs.org) 0.186.1, MIT, načítá se z CDN jsDelivr / loaded from the jsDelivr CDN
- [Draco](https://github.com/google/draco) dekodér (`draco/`), Apache License 2.0, Google
- Písma [Bebas Neue](https://fonts.google.com/specimen/Bebas+Neue) a [DM Sans](https://fonts.google.com/specimen/DM+Sans), SIL Open Font License, Google Fonts
- Model postavený v [Blenderu](https://www.blender.org) skriptem `blender/build_r12.py`
