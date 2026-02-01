import gzip
import xml.etree.ElementTree as ET
from datetime import datetime

SOURCE_GZ = "epg_ripper_ALL_SOURCES1.gz"
OUTPUT_XML = "filtered_epg.xml"
OUTPUT_GZ = "filtered_epg.xml.gz"

# ==============================
# ✅ CHANNEL LIST (PLAIN FORMAT)
# channel [space] logo_url(optional)
# ==============================

CHANNELS_TEXT = """
9x.jalwa.in http://ryzen.one/logos2/9x_jalwa.jpg
9x.jhakaas.in
9xm.in http://ryzen.one/logos2/9Xm.jpg
9x.tashan.in
aaj.tak.in http://b1gchlogos.xyz/wp-content/uploads/2023/08/Aaj-Tak-HD.png
and.flix.hd.in http://ryzen.one/logos2/&flixhd.jpg
and.pictures.hd.in http://ryzen.one/logos2/&pictures.jpg
and.prive.hd.in
and.tv.hd.in http://ryzen.one/logos2/&tvhd.jpg
and.xplorhd.in https://go4.pw/India/&explorer.png
animal.planet.hd.world.in http://ryzen.one/logos2/animal_planethd.jpg
b4u.kadak.in
b4u.movies.in
b4u.music.in
big.magic.in
cartoon.network.in
cn.hd+.english.in
colors.cineplex.hd.in
colors.cineplex.superhits.in
colors.hd.in
colors.infinity.hd.in
colors.rishtey.in
colors.super.in
dangal.2.in
dangal.in
dd.sports.in
dhoom.music.in
discovery.hd.world.in
discovery.kids.in
discovery.science.in
discovery.turbo.in
disney.channel.in
disney.junior.in
eurosports.hd.in
history.tv18.hd.in
hungama.in
india.tv.in
investigation.discovery.in
max.hd.in http://ryzen.one/logos2/sony_maxhd.jpg
mn+.hd.in
mnx.hd.in
movies.now.in
movies.now.hd.in https://go4.pw/ASIA/INDIAN/MOVIESNOWHD.png
mtv.hd.in
mtv.in
nat.geo.wild.hd.in
national.geographic.hd.in
nick.hd+.in
nick.in
nick.jr.in
pogo.in
romedy.now.in
sab.hd.in
set.hd.in
showbox.in
sonic.nickelodeon.in
sony.bbc.earth.hd.in http://ryzen.one/logos2/sony_bbc_earthhd.jpg
sony.max.1.in
sony.max.2.in http://ryzen.one/logos2/sony_max2.jpg
sony.pal.in http://b1g.fun/logos2/sony_pal.jpg
sony.pix.hd.in http://ryzen.one/logos2/sony_pixhd.jpg
sony.sab.in http://ryzen.one/logos2/sony_sabhd.jpg
sony.sports.ten.1.hd.in
sony.sports.ten.2.hd.in
sony.sports.ten.3.hd.in
sony.sports.ten.5.hd.in
sony.wah.in http://ryzen.one/logos2/sony_wah.jpg
sony.yay.in
star.bharat.hd.in http://ryzen.one/logos2/star_bharathd.jpg
star.gold.2.hd.in http://ryzen.one/logos2/star_gold2.jpg
star.gold.in https://go4.pw/India/STARGOLD2.png
star.gold.hd.in http://ryzen.one/logos2/star_goldhd.jpg
star.gold.romance.in
star.gold.select.hd.in
star.gold.thrills.in
star.movies.hd.in http://ryzen.one/logos2/tlc_hd.jpg
star.movies.select.hd.in http://ryzen.one/logos2/star_movies_selecthd.jpg
star.plus.hd.in http://ryzen.one/logos2/star_plushd.jpg
star.sports.1.hd.hindi.in
star.sports.1.hd.in http://ryzen.one/logos2/star_sports1hd.jpg
star.sports.2.hd.in http://ryzen.one/logos2/star_sports2.jpg
star.sports.2.hindi.hd.in http://ryzen.one/logos2/star_sports_select2.jpg
star.sports.3.in http://ryzen.one/logos2/star_sports_3.jpg
star.sports.khel.in http://ryzen.one/logos2/sports18_khel.jpg
star.sports.select.1.hd.in http://ryzen.one/logos2/star_sports_select_1hd.jpg
star.sports.select.2.hd.in http://ryzen.one/logos2/star_sports_select2.jpg
star.utsav.in http://ryzen.one/logos2/star_utsav.jpg
star.utsav.movies.in
tlc.hd.in
Travelxp.HD.in
tv9.kannada.in
tv9.marathi.in
zee.action.in
zee.anmol.cinema.2.in
zee.anmol.cinema.in
zee.anmol.in
zee.bollywood.in
zee.cinema.hd.in
zee.classic.in
zee.tv.hd.in
zing.in
zoom.in
skysp.cricket.in
astro.cricket.in
foxcricket.in
willow.cricket.hd.in
willow.xtra.in
supersport.school.hd.in
mastiii.in
music.india.in
star.sports.first.in https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSBjneDJZWkUzWhrFzbHfXwnynpigT-867HEA&s
food.food.in
baby.tv.english.(gb,en).in
star.life.in
the.q.india.in
goldmines.in
haryana.beats.in
vh1.hd.in
bollywood.hd.in
sports.18.2.in
"""

# ==============================
# ✅ CLEAN ID (ONLY FOR MATCHING)
# ==============================

SUFFIXES = [".in", ".uk", ".hk", ".us", ".us2", ".au", ".za", ".al", ".pl", ".no"]

def clean_id(cid):
    cid = cid.strip().lower()
    for s in SUFFIXES:
        if cid.endswith(s):
            cid = cid[:-len(s)]
            break
    return cid + ".in"

# ==============================
# ✅ PARSE CHANNELS (KEEP ORIGINAL)
# ==============================

CHANNELS = {}
for line in CHANNELS_TEXT.splitlines():
    if not line.strip():
        continue

    parts = line.split(maxsplit=1)
    original_id = parts[0].strip().lower()
    logo = parts[1].strip() if len(parts) == 2 else None

    cleaned = clean_id(original_id)

    CHANNELS[cleaned] = {
        "original": original_id,
        "logo": logo
    }

# ==============================
# ✅ MAIN LOGIC
# ==============================

def main():
    kept = set()
    programmes = 0

    with open(OUTPUT_XML, "wb") as out:
        out.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
        out.write(
            f'<tv generator-info-name="filtered_epg" '
            f'date="{datetime.utcnow().strftime("%Y%m%d%H%M%S +0000")}">\n'
            .encode()
        )

        with gzip.open(SOURCE_GZ, "rb") as f:
            for _, elem in ET.iterparse(f, events=("end",)):

                # ---------- CHANNEL ----------
                if elem.tag == "channel":
                    raw_id = elem.attrib.get("id", "")
                    cid = clean_id(raw_id)

                    if cid in CHANNELS:
                        elem.attrib["id"] = CHANNELS[cid]["original"]
                        kept.add(cid)

                        logo = CHANNELS[cid]["logo"]
                        if logo:
                            for i in elem.findall("icon"):
                                elem.remove(i)
                            icon = ET.Element("icon")
                            icon.set("src", logo)
                            elem.append(icon)

                        out.write(ET.tostring(elem) + b"\n")

                    elem.clear()

                # ---------- PROGRAMME ----------
                elif elem.tag == "programme":
                    raw_id = elem.attrib.get("channel", "")
                    cid = clean_id(raw_id)

                    if cid in kept:
                        elem.attrib["channel"] = CHANNELS[cid]["original"]
                        out.write(ET.tostring(elem) + b"\n")
                        programmes += 1

                    elem.clear()

        out.write(b"</tv>")

    # ---------- COMPRESS ----------
    with open(OUTPUT_XML, "rb") as fi, gzip.open(OUTPUT_GZ, "wb") as fo:
        fo.writelines(fi)

    print("✅ DONE")
    print("Channels :", len(kept))
    print("Programmes :", programmes)

# ==============================
# ✅ RUN
# ==============================

if __name__ == "__main__":
    main()
