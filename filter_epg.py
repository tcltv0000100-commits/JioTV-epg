import gzip
import xml.etree.ElementTree as ET
from datetime import datetime

SOURCE_GZ = "epg_ripper_ALL_SOURCES1.gz"
OUTPUT_XML = "filtered_epg.xml"
OUTPUT_GZ = "filtered_epg.xml.gz"

# ==============================
# ✅ AAPKI REQUESTED CHANNELS LIST (FILTER KE LIYE)
# ==============================

CHANNELS_LIST = """
9x.jalwa.in
9x.jhakaas.in
9xm.in
9x.tashan.in
aaj.tak.in
and.flix.hd.in
and.pictures.hd.in
And.Prive.HD.in
and.tv.hd.in
and.xplorhd.in
animal.planet.hd.world.in
b4u.kadak.in
b4u.movies.in
b4u.music.in
big.magic.in
cartoon.network.in
cn.hd+.english.in
Colors.Cineplex.HD.in
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
Food.Food.in
history.tv18.hd.in
hungama.in
india.tv.in
Sony.Max.HD.in
mn+.hd.in
mnx.hd.in
movies.now.in
Movies.Now.HD.in
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
sony.bbc.earth.hd.in
sony.max.1.in
sony.max.2.in
sony.pal.in
sony.pix.hd.in
sony.sab.in
sony.sports.ten.1.hd.in
sony.sports.ten.2.hd.in
sony.sports.ten.3.hd.in
sony.sports.ten.5.hd.in
sony.wah.in
sony.yay.in
star.bharat.hd.in
Star.Gold.2.HD.in
star.gold.in
star.gold.hd.in
star.gold.romance.in
star.gold.select.hd.in
star.gold.thrills.in
star.movies.hd.in
star.movies.select.hd.in
star.plus.hd.in
star.sports.1.hd.hindi.in
star.sports.1.hd.in
star.sports.2.hd.in
star.sports.2.hindi.hd.in
star.sports.3.in
Star.Sports.First.in
star.sports.khel.in
star.sports.select.1.hd.in
star.sports.select.2.hd.in
star.utsav.in
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
Astro.Cricket.my
foxcricket.in
willow.cricket.hd.in
willow.xtra.in
supersport.school.hd.in
mastiii.in
music.india.in
star.sports.first.in
food.food.in
baby.tv.english.(gb,en).in
star.life.in
the.q.india.in
goldmines.in
haryana.beats.in
vh1.hd.in
bollywood.hd.in
sports.18.2.in
Sky.Sports.Cricket.HD.ie
"""

# ==============================
# ✅ CLEAN ID (MATCHING LOGIC)
# ==============================

SUFFIXES = [".in", ".uk", ".hk", ".us", ".us2", ".au", ".za", ".al", ".pl", ".no", ".ie", ".my"]

def clean_id(cid):
    cid = cid.strip().lower()
    for s in SUFFIXES:
        if cid.endswith(s):
            cid = cid[:-len(s)]
            break
    return cid + ".in"

# Clean target map banayein
TARGET_CHANNELS = {}
for line in CHANNELS_LIST.splitlines():
    line = line.strip()
    if line:
        cleaned = clean_id(line)
        TARGET_CHANNELS[cleaned] = line.lower()

# ==============================
# ✅ MAIN LOGIC
# ==============================

def main():
    kept_channels = set()
    programmes = 0

    print("⏳ Processing requested channels & fetching logos automatically from GZ...")

    with open(OUTPUT_XML, "wb") as out:
        out.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
        out.write(
            f'<tv generator-info-name="filtered_epg" '
            f'date="{datetime.utcnow().strftime("%Y%m%d%H%M%S +0000")}">\n'
            .encode()
        )

        with gzip.open(SOURCE_GZ, "rb") as f:
            for _, elem in ET.iterparse(f, events=("end",)):

                # ---------- CHANNEL FILTER & AUTO LOGO ----------
                if elem.tag == "channel":
                    raw_id = elem.attrib.get("id", "")
                    cid = clean_id(raw_id)

                    # Sirf aapki requested list me se filter karega
                    if cid in TARGET_CHANNELS:
                        elem.attrib["id"] = TARGET_CHANNELS[cid]
                        kept_channels.add(cid)

                        # .gz ke andar jo bhi default logo hoga, use preserve rakhega
                        out.write(ET.tostring(elem) + b"\n")

                    elem.clear()

                # ---------- PROGRAMME FILTER ----------
                elif elem.tag == "programme":
                    raw_id = elem.attrib.get("channel", "")
                    cid = clean_id(raw_id)

                    if cid in kept_channels:
                        elem.attrib["channel"] = TARGET_CHANNELS[cid]
                        out.write(ET.tostring(elem) + b"\n")
                        programmes += 1

                    elem.clear()

        out.write(b"</tv>")

    # ---------- COMPRESS ----------
    with open(OUTPUT_XML, "rb") as fi, gzip.open(OUTPUT_GZ, "wb") as fo:
        fo.writelines(fi)

    print("✅ DONE")
    print("Filtered Channels Saved :", len(kept_channels))
    print("Programmes Saved         :", programmes)

# ==============================
# ✅ RUN
# ==============================

if __name__ == "__main__":
    main()
