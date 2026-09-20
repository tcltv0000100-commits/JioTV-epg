import gzip
import xml.etree.ElementTree as ET
from datetime import datetime

SOURCE_GZ = "epg_ripper_ALL_SOURCES1.gz"
OUTPUT_XML = "filtered_epg.xml"
OUTPUT_GZ = "filtered_epg.xml.gz"

# ==============================
# ✅ CHANNEL LIST (UPDATED LOGOS - HD PREFERRED)
# channel [space] logo_url(optional)
# ==============================

CHANNELS_TEXT = """
9x.jalwa.in https://jiotv.catchup.cdn.jio.com/dare_images/images/9X_Jalwa.png
9x.jhakaas.in https://upload.wikimedia.org/wikipedia/en/3/3d/9X_Jhakaas_logo.png
9xm.in https://jiotv.catchup.cdn.jio.com/dare_images/images/9XM.png
9x.tashan.in https://jiotv.catchup.cdn.jio.com/dare_images/images/9X_Tashan.png
aaj.tak.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Aaj_Tak_HD.png
and.flix.hd.in https://jiotv.catchup.cdn.jio.com/dare_images/images/And_Flix_HD.png
and.pictures.hd.in https://jiotv.catchup.cdn.jio.com/dare_images/images/And_Pictures_HD.png
And.Prive.HD.in https://jiotv.catchup.cdn.jio.com/dare_images/images/And_Prive_HD.png
and.tv.hd.in https://jiotv.catchup.cdn.jio.com/dare_images/images/And_TV_HD.png
and.xplorhd.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Zee_Xplor_HD.png
animal.planet.hd.world.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Animal_Planet_HD_World.png
b4u.kadak.in https://jiotv.catchup.cdn.jio.com/dare_images/images/B4U_Kadak.png
b4u.movies.in https://jiotv.catchup.cdn.jio.com/dare_images/images/B4U_Movies.png
b4u.music.in https://jiotv.catchup.cdn.jio.com/dare_images/images/B4U_Music.png
big.magic.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Big_Magic.png
cartoon.network.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Cartoon_Network.png
cn.hd+.english.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Cartoon_Network_HD.png
Colors.Cineplex.HD.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Colors_Cineplex_HD.png
colors.cineplex.superhits.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Colors_Cineplex_Superhits.png
colors.hd.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Colors_HD.png
colors.infinity.hd.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Colors_Infinity_HD.png
colors.rishtey.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Colors_Rishtey.png
colors.super.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Colors_Super.png
dangal.2.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Dangal_2.png
dangal.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Dangal.png
dd.sports.in https://jiotv.catchup.cdn.jio.com/dare_images/images/DD_Sports.png
dhoom.music.in https://upload.wikimedia.org/wikipedia/en/a/a2/Dhoom_Music_Logo.png
discovery.hd.world.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Discovery_HD.png
discovery.kids.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Discovery_Kids.png
discovery.science.in https://upload.wikimedia.org/wikipedia/commons/e/e6/Discovery_Science_logo.png
discovery.turbo.in https://upload.wikimedia.org/wikipedia/commons/1/1d/Discovery_Turbo_logo.png
disney.channel.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Disney_Channel.png
disney.junior.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Disney_Junior.png
eurosports.hd.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Eurospot_HD.png
Food.Food.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Food_Food.png
history.tv18.hd.in https://jiotv.catchup.cdn.jio.com/dare_images/images/History_TV18_HD.png
hungama.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Hungama_TV.png
india.tv.in https://jiotv.catchup.cdn.jio.com/dare_images/images/India_TV.png
Sony.Max.HD.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Sony_Max_HD.png
mn+.hd.in https://jiotv.catchup.cdn.jio.com/dare_images/images/MN_Plus_HD.png
mnx.hd.in https://jiotv.catchup.cdn.jio.com/dare_images/images/MNX_HD.png
movies.now.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Movies_Now.png
Movies.Now.HD.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Movies_Now_HD.png
mtv.hd.in https://jiotv.catchup.cdn.jio.com/dare_images/images/MTV_HD_Plus.png
mtv.in https://jiotv.catchup.cdn.jio.com/dare_images/images/MTV.png
nat.geo.wild.hd.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Nat_Geo_Wild_HD.png
national.geographic.hd.in https://jiotv.catchup.cdn.jio.com/dare_images/images/National_Geographic_HD.png
nick.hd+.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Nick_HD_Plus.png
nick.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Nickelodeon.png
nick.jr.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Nick_Jr.png
pogo.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Pogo.png
romedy.now.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Romedy_Now.png
sab.hd.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Sony_SAB_HD.png
set.hd.in https://jiotv.catchup.cdn.jio.com/dare_images/images/SET_HD.png
showbox.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Showbox.png
sonic.nickelodeon.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Sonic_Nickelodeon.png
sony.bbc.earth.hd.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Sony_BBC_Earth_HD.png
sony.max.1.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Sony_Max.png
sony.max.2.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Sony_Max_2.png
sony.pal.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Sony_Pal.png
sony.pix.hd.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Sony_Pix_HD.png
sony.sab.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Sony_SAB_HD.png
sony.sports.ten.1.hd.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Sony_Sports_Ten_1_HD.png
sony.sports.ten.2.hd.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Sony_Sports_Ten_2_HD.png
sony.sports.ten.3.hd.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Sony_Sports_Ten_3_HD.png
sony.sports.ten.5.hd.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Sony_Sports_Ten_5_HD.png
sony.wah.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Sony_Wah.png
sony.yay.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Sony_Yay.png
star.bharat.hd.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Star_Bharat_HD.png
Star.Gold.2.HD.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Star_Gold_2_HD.png
star.gold.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Star_Gold.png
star.gold.hd.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Star_Gold_HD.png
star.gold.romance.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Star_Gold_Romance.png
star.gold.select.hd.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Star_Gold_Select_HD.png
star.gold.thrills.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Star_Gold_Thrills.png
star.movies.hd.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Star_Movies_HD.png
star.movies.select.hd.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Star_Movies_Select_HD.png
star.plus.hd.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Star_Plus_HD.png
star.sports.1.hd.hindi.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Star_Sports_1_Hindi_HD.png
star.sports.1.hd.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Star_Sports_1_HD.png
star.sports.2.hd.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Star_Sports_2_HD.png
star.sports.2.hindi.hd.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Star_Sports_2_Hindi_HD.png
star.sports.3.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Star_Sports_3.png
Star.Sports.First.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Star_Sports_First.png
star.sports.khel.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Star_Sports_Khel.png
star.sports.select.1.hd.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Star_Sports_Select_1_HD.png
star.sports.select.2.hd.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Star_Sports_Select_2_HD.png
star.utsav.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Star_Utsav.png
star.utsav.movies.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Star_Utsav_Movies.png
tlc.hd.in https://jiotv.catchup.cdn.jio.com/dare_images/images/TLC_HD.png
Travelxp.HD.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Travelxp_HD.png
tv9.kannada.in https://jiotv.catchup.cdn.jio.com/dare_images/images/TV9_Kannada.png
tv9.marathi.in https://jiotv.catchup.cdn.jio.com/dare_images/images/TV9_Marathi.png
zee.action.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Zee_Action.png
zee.anmol.cinema.2.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Zee_Anmol_Cinema.png
zee.anmol.cinema.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Zee_Anmol_Cinema.png
zee.anmol.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Zee_Anmol.png
zee.bollywood.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Zee_Bollywood.png
zee.cinema.hd.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Zee_Cinema_HD.png
zee.classic.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Zee_Classic.png
zee.tv.hd.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Zee_TV_HD.png
zing.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Zing.png
zoom.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Zoom.png
skysp.cricket.in https://upload.wikimedia.org/wikipedia/en/3/37/Sky_Sports_Cricket_logo_2020.png
astro.cricket.in https://upload.wikimedia.org/wikipedia/commons/d/df/Astro_Cricket_Logo.png
Astro.Cricket.my https://upload.wikimedia.org/wikipedia/commons/d/df/Astro_Cricket_Logo.png
foxcricket.in https://upload.wikimedia.org/wikipedia/en/3/37/Fox_Cricket_logo.png
willow.cricket.hd.in https://upload.wikimedia.org/wikipedia/commons/c/c3/Willow_TV_logo.png
willow.xtra.in https://upload.wikimedia.org/wikipedia/commons/c/c3/Willow_TV_logo.png
supersport.school.hd.in https://upload.wikimedia.org/wikipedia/en/e/e0/SuperSport_logo.png
mastiii.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Mastiii.png
music.india.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Music_India.png
star.sports.first.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Star_Sports_First.png
food.food.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Food_Food.png
baby.tv.english.(gb,en).in https://upload.wikimedia.org/wikipedia/commons/c/c5/BabyTV_logo.png
star.life.in https://upload.wikimedia.org/wikipedia/commons/6/63/Star_Life_%28India%29.svg
the.q.india.in https://jiotv.catchup.cdn.jio.com/dare_images/images/The_Q.png
goldmines.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Goldmines.png
haryana.beats.in https://jiotv.catchup.cdn.jio.com/dare_images/images/MH_One_Dilse.png
vh1.hd.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Vh1_HD.png
bollywood.hd.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Zee_Bollywood.png
sports.18.2.in https://jiotv.catchup.cdn.jio.com/dare_images/images/Sports18_Khel.png
Sky.Sports.Cricket.HD.ie https://upload.wikimedia.org/wikipedia/en/3/37/Sky_Sports_Cricket_logo_2020.png
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
