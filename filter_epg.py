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
9x.jhakaas.in http://b1gchlogos.xyz/wp-content/uploads/2023/08/Zee-Bihar-Jharkhand.png
9xm.in http://ryzen.one/logos2/9Xm.jpg
9x.tashan.in
aaj.tak.in http://b1gchlogos.xyz/wp-content/uploads/2023/08/Aaj-Tak-HD.png
and.flix.hd.in http://ryzen.one/logos2/&flixhd.jpg
and.pictures.hd.in http://ryzen.one/logos2/&pictureshd.jpg
and.prive.hd.in 
and.tv.hd.in http://ryzen.one/logos2/&tvhd.jpg
and.xplorhd.in https://go4.pw/India/&explorer.png
animal.planet.hd.world.in http://ryzen.one/logos2/animal_planethd.jpg
b4u.kadak.in http://ryzen.one/logos2/b4u_kadak.jpg
b4u.movies.in http://ryzen.one/logos2/b4u_movies.jpg
b4u.music.in http://ryzen.one/logos2/b4u_music.jpg
big.magic.in http://ryzen.one/logos2/zee_bigmagic.jpg
cartoon.network.in http://ryzen.one/logos2/catoon_network_hd+.jpg
cn.hd+.english.in http://ryzen.one/logos2/catoon_network_hd+.jpg
colors.cineplex.hd.in http://ryzen.one/logos2/colors_cineplexhd.jpg
colors.cineplex.superhits.in http://ryzen.one/logos2/colors_cineplex.jpg
colors.hd.in http://ryzen.one/logos2/colorshd.jpg
colors.infinity.hd.in http://ryzen.one/logos2/colors_infinityhd.jpg
colors.rishtey.in http://ryzen.one/logos2/colors_rishtey.jpg
colors.super.in http://ryzen.one/logos2/colors_rishtey.jpg
dangal.2.in http://ryzen.one/logos2/dangal2.jpg
dangal.in http://ryzen.one/logos2/dangal.jpg
dd.sports.in http://ryzen.one/logos2/dd_sports.jpg
dhoom.music.in
discovery.hd.world.in http://ryzen.one/logos2/discovery_worldhd.jpg
discovery.kids.in http://ryzen.one/logos2/discovery_kids.jpg
discovery.science.in
discovery.turbo.in
disney.channel.in http://b1gchlogos.xyz/wp-content/uploads/2023/08/Disney.png
disney.junior.in 
eurosports.hd.in
history.tv18.hd.in http://ryzen.one/logos2/history_tv18.jpg
hungama.in
india.tv.in http://b1gchlogos.xyz/wp-content/uploads/2023/08/India-TV.png
max.hd.in http://ryzen.one/logos2/sony_maxhd.jpg
mn+.hd.in http://ryzen.one/logos2/mn+moviedhd.jpg
mnx.hd.in http://ryzen.one/logos2/mnx_hd.jpg
movies.now.in
movies.now.hd.in http://ryzen.one/logos2/movies_nowhd.jpg
mtv.hd.in http://ryzen.one/logos2/mtv+hd.jpg
mtv.in
nat.geo.wild.hd.in http://ryzen.one/logos2/nat_geo_wildhd.jpg
national.geographic.hd.in http://ryzen.one/logos2/net_geo_hindihd.jpg
nick.hd+.in http://ryzen.one/logos2/nick+hd.jpg
nick.in http://ryzen.one/logos2/nickhd.jpg
nick.jr.in http://ryzen.one/logos2/nick_jr.jpg
pogo.in http://ryzen.one/logos2/pogo.jpg
romedy.now.in http://ryzen.one/logos2/romedy_nowhd.jpg
sab.hd.in http://ryzen.one/logos2/sony_sabhd.jpg
set.hd.in http://ryzen.one/logos2/sony_tvhd.jpg
showbox.in http://ryzen.one/logos2/showbox.jpg
sonic.nickelodeon.in http://ryzen.one/logos2/nick_sonic.jpg
sony.bbc.earth.hd.in http://ryzen.one/logos2/sony_bbc_earthhd.jpg
sony.max.1.in
sony.max.2.in http://ryzen.one/logos2/sony_max2.jpg
sony.pal.in http://ryzen.one/logos2/sony_pal.jpg
sony.pix.hd.in http://ryzen.one/logos2/sony_pixhd.jpg
sony.sab.in http://ryzen.one/logos2/sony_sabhd.jpg
sony.sports.ten.1.hd.in http://ryzen.one/logos2/sony_ten1.jpg
sony.sports.ten.2.hd.in http://ryzen.one/logos2/sony_ten2.jpg
sony.sports.ten.3.hd.in http://ryzen.one/logos2/sony_ten3.jpg
sony.sports.ten.5.hd.in http://ryzen.one/logos2/sony_ten5.jpg
sony.wah.in http://ryzen.one/logos2/sony_wah.jpg
sony.yay.in http://ryzen.one/logos2/sony_yay.jpg
star.bharat.hd.in http://ryzen.one/logos2/star_bharathd.jpg
star.gold.2.hd.in http://ryzen.one/logos2/star_gold2.jpg
star.gold.in http://ryzen.one/logos2/star_gold2.jpg
star.gold.hd.in http://ryzen.one/logos2/star_goldhd.jpg
star.gold.romance.in
star.gold.select.hd.in 
star.gold.thrills.in 
star.movies.hd.in 
star.movies.select.hd.in http://ryzen.one/logos2/star_movies_selecthd.jpg
star.plus.hd.in http://ryzen.one/logos2/star_plushd.jpg
star.sports.1.hd.hindi.in 
star.sports.1.hd.in http://ryzen.one/logos2/star_sports1hd.jpg
star.sports.2.hd.in http://ryzen.one/logos2/star_sports2.jpg
star.sports.2.hindi.hd.in http://ryzen.one/logos2/star_sports2.jpg
star.sports.3.in http://ryzen.one/logos2/star_sports_3.jpg
star.sports.khel.in http://ryzen.one/logos2/sports18_khel.jpg
star.sports.select.1.hd.in http://ryzen.one/logos2/star_sports_select_1hd.jpg
star.sports.select.2.hd.in http://ryzen.one/logos2/star_sports_select2.jpg
star.utsav.in http://ryzen.one/logos2/star_utsav.jpg
star.utsav.movies.in
tlc.hd.in http://ryzen.one/logos2/tlc_hd.jpg
Travelxp.HD.in http://b1gchlogos.xyz/wp-content/uploads/2023/08/TravelXP4K.png
tv9.kannada.in
tv9.marathi.in
zee.action.in http://ryzen.one/logos2/zee_action.jpg
zee.anmol.cinema.2.in
zee.anmol.cinema.in http://ryzen.one/logos2/zee_anmolcinema.jpg
zee.anmol.in http://ryzen.one/logos2/zee_anmol.jpg
zee.bollywood.in http://ryzen.one/logos2/zee_bollywood.jpg
zee.cinema.hd.in http://ryzen.one/logos2/zee_cinema.jpg
zee.classic.in http://ryzen.one/logos2/zee_classic.jpg
zee.tv.hd.in http://ryzen.one/logos2/zee_tvhd.jpg
zing.in http://ryzen.one/logos2/zing.jpg
zoom.in http://ryzen.one/logos2/zoom.jpg
skysp.cricket.in
astro.cricket.in http://ryzen.one/logos2/astro_cricket.jpg
foxcricket.in
willow.cricket.hd.in http://ryzen.one/logos2/willowhd.jpg
willow.xtra.in http://ryzen.one/logos2/willowxtra.jpg
supersport.school.hd.in http://ryzen.one/logos2/supersports_cricket.jpg
mastiii.in http://ryzen.one/logos2/mastiii.jpg
music.india.in http://ryzen.one/logos2/music_india.jpg
star.sports.first.in https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSBjneDJZWkUzWhrFzbHfXwnynpigT-867HEA&s
food.food.in http://ryzen.one/logos2/food_food.jpg
baby.tv.english.(gb,en).in http://ryzen.one/logos2/baby_tvhd.jpg
star.life.in https://upload.wikimedia.org/wikipedia/commons/6/63/Star_Life_%28India%29.svg
the.q.india.in http://ryzen.one/logos2/the_q.jpg
goldmines.in http://ryzen.one/logos2/goldmines.jpg
haryana.beats.in https://mym2e.fun/images/pJALEGYQDgwbUdRmcM-QRYikR-k2jDWt-xcbL2zgSTAqjv56J5E-3muEdNejl7UxxhhbsH87JYFl2k-RrMmzbg.jpeg
vh1.hd.in https://mym2e.fun/images/pJALEGYQDgwbUdRmcM-QRYikR-k2jDWt-xcbL2zgSTAqjv56J5E-3muEdNejl7UxxhhbsH87JYFl2k-RrMmzbg.jpeg
bollywood.hd.in https://s1.vcdn.biz/static/f/5512601881/image.jpg
sports.18.2.in http://ryzen.one/logos2/sports18_khel.jpg
Sky.Sports.Cricket.HD.ie
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
