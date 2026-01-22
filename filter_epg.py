import gzip
import xml.etree.ElementTree as ET
from datetime import datetime

SOURCE_GZ = "epg_ripper_ALL_SOURCES1.gz"
OUTPUT_XML = "filtered_epg.xml"
OUTPUT_GZ = "filtered_epg.xml.gz"

# ✅ Your exact channel IDs (as in source)
CHANNELS = {
    "9X.Jalwa.in",
    "9X.JHAKAAS.in",
    "9XM.in",
    "9X.TASHAN.in",
    "AAJ.TAK.in",
    "and.Flix.HD.in",
    "and.flix.in",
    "and.PICTURES.HD.in",
    "and.PICTURES.in",
    "and.PRIVE.HD.in",
    "and.TV.HD.in",
    "and.TV.in",
    "and.xplorHD.in",
    "ANIMAL.PLANET.HD.WORLD.in",
    "ANIMAL.PLANET.in",
    "B4U.KADAK.in",
    "B4U.Movies.in",
    "B4U.MUSIC.in",
    "BIG.MAGIC.in",
    "CARTOON.NETWORK.in",
    "CN.HD+.English.in",
    "Colors.Cineplex.HD.in",
    "COLORS.CINEPLEX.SUPERHITS.in",
    "COLORS.HD.in",
    "COLORS.in",
    "COLORS.INFINITY.HD.in",
    "COLORS.INFINITY..in",
    "COLORS.RISHTEY.in",
    "COLORS.SUPER.in",
    "Dangal.2.in",
    "DANGAL.in",
    "DD.Sports.in",
    "DHOOM.MUSIC.in",
    "DISCOVERY.CHANNEL.in",
    "DISCOVERY.HD.WORLD.in",
    "DISCOVERY.KIDS.in",
    "Discovery.Science.in",
    "Discovery.Turbo.in",
    "DISNEY.CHANNEL.in",
    "DISNEY.JUNIOR.in",
    "Eurosport.in",
    "EUROSPORTS.HD.in",
    "HISTORY.CHANNEL.in",
    "HISTORY.TV18.HD.in",
    "HUNGAMA.in",
    "INDIA.TV.in",
    "Investigation.Discovery.in",
    "MAX.HD.in",
    "MN+.HD.in",
    "MNX.HD.in",
    "Movies.Now.HD.in",
    "MTV.HD.in",
    "NAT.GEO.WILD.HD.in",
    "NAT.GEO.WILD.in",
    "NATIONAL.GEOGRAPHIC.HD.in",
    "NATIONAL.GEOGRAPHIC.in",
    "NICK.HD+.in",
    "NICK.in",
    "NICK.JR.in",
    "POGO.in",
    "ROMEDY.NOW.in",
    "SAB.HD.in",
    "SET.HD.in",
    "SET.in",
    "Showbox.in",
    "SONIC.NICKELODEON.in",
    "SONY.BBC.EARTH.HD.in",
    "SONY.BBC.EARTH.in",
    "SONY.MAX.1.in",
    "SONY.MAX.2.in",
    "SONY.MAX.in",
    "SONY.PAL.in",
    "SONY.PIX.HD.in",
    "SONY.PIX.in",
    "SONY.SAB.in",
    "SONY.SPORTS.TEN.1.HD.in",
    "SONY.SPORTS.TEN.1.in",
    "SONY.SPORTS.TEN.2.HD.in",
    "SONY.SPORTS.TEN.2.in",
    "SONY.SPORTS.TEN.3.HD.in",
    "SONY.SPORTS.TEN.3.in",
    "SONY.SPORTS.TEN.5.HD.in",
    "SONY.SPORTS.TEN.5.in",
    "SONY.WAH.in",
    "Sony.yay.in",
    "STAR.BHARAT.HD.in",
    "STAR.BHARAT.in",
    "Star.Gold.2.in",
    "STAR.GOLD.HD.in",
    "STAR.GOLD.in",
    "STAR.GOLD.ROMANCE.in",
    "Star.Gold.Select.HD.in",
    "STAR.GOLD.SELECT.in",
    "STAR.GOLD.THRILLS.in",
    "STAR.MOVIES.HD.in",
    "STAR.MOVIES.in",
    "STAR.MOVIES.SELECT.HD.in",
    "STAR.MOVIES.SELECT.in",
    "STAR.PLUS.HD.in",
    "STAR.PLUS.in",
    "STAR.SPORTS.1.HD.HINDI.in",
    "STAR.SPORTS.1.HD.in",
    "STAR.SPORTS.1.HINDI.in",
    "STAR.SPORTS.1.in",
    "STAR.SPORTS.2.HD.in",
    "STAR.SPORTS.2.HINDI.HD.in",
    "STAR.SPORTS.2.HINDI.in",
    "STAR.SPORTS.2.in",
    "STAR.SPORTS.3.in",
    "Star.Sports.Khel.in",
    "STAR.SPORTS.SELECT.1.HD.in",
    "Star.Sports.Select.1.in",
    "STAR.SPORTS.SELECT.2.HD.in",
    "STAR.SPORTS.SELECT.2.in",
    "STAR.UTSAV.in",
    "STAR.UTSAV.MOVIES.in",
    "TLC.HD.in",
    "TLC.in",
    "TRAVEL.XP.(HD).in",
    "TV9.KANNADA.in",
    "TV9.MARATHI.in",
    "ZEE.ACTION.in",
    "ZEE.ANMOL.CINEMA.2.in",
    "ZEE.ANMOL.CINEMA.in",
    "ZEE.ANMOL.in",
    "ZEE.Bollywood.in",
    "ZEE.CINEMA.HD.in",
    "ZEE.CINEMA.in",
    "ZEE.CLASSIC.in",
    "ZEE.TV.HD.in",
    "ZEE.TV.in",
    "ZING.in",
    "ZOOM.in",
    "SkySp.Cricket.uk",
    "Astro.Cricket.hk",
    "FoxCricket.au",
    "Willow.Cricket.HD.us2",
    "Willow.Xtra.us2",
    "SuperSport.School.HD.za",
    "Mastiii.in",
    "Music.India.in",
    "Star.Sports.First.in",
    "Music.India.in",
    "Food.Food.in",
    "Baby.TV.English.(GB,EN).no",
    "Star.Life.al",
    "The.Q.India.in",
    "Goldmines.Movies.in",
    "MTV.HD.it",
    "Haryana.Beats.in",
    "VH1.HD.us2",
    "Bollywood.HD.pl",
    "Sports.18.2.in",
}

def clean_channel_id(source_id: str) -> str:
    """
    Convert source ID to display-style ID:
      DD.Bangla.in -> DD Bangla"
      SONY.MAX.1.in -> SONY MAX 1
    """
    s = source_id
    if s.endswith(".in"):
        s = s[:-3]
    s = s.replace(".", " ")
    s = " ".join(s.split())
    return s

def main():
    kept_ids = set()      # original ids
    id_map = {}           # original -> cleaned

    kept_channels = 0
    kept_programmes = 0

    print("Reading:", SOURCE_GZ)

    with open(OUTPUT_XML, "wb") as out:
        out.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
        out.write(
            f'<tv generator-info-name="filtered_epg_generator" date="{datetime.utcnow().strftime("%Y%m%d%H%M%S +0000")}">\n'
            .encode("utf-8")
        )

        with gzip.open(SOURCE_GZ, "rb") as f:
            context = ET.iterparse(f, events=("end",))

            for event, elem in context:
                tag = elem.tag

                # ✅ Handle <channel>
                if tag == "channel":
                    ch_id = elem.attrib.get("id", "")

                    if ch_id in CHANNELS:
                        new_id = clean_channel_id(ch_id)

                        kept_ids.add(ch_id)
                        id_map[ch_id] = new_id

                        # replace <channel id="...">
                        elem.attrib["id"] = new_id

                        out.write(ET.tostring(elem, encoding="utf-8"))
                        out.write(b"\n")

                        kept_channels += 1

                    elem.clear()

                # ✅ Handle <programme>
                elif tag == "programme":
                    cid = elem.attrib.get("channel", "")

                    if cid in kept_ids:
                        # Replace programme channel="oldid" -> channel="newid"
                        elem.attrib["channel"] = id_map.get(cid, cid)

                        out.write(ET.tostring(elem, encoding="utf-8"))
                        out.write(b"\n")

                        kept_programmes += 1

                    elem.clear()

        out.write(b"</tv>\n")

    # ✅ gzip output
    with open(OUTPUT_XML, "rb") as f_in, gzip.open(OUTPUT_GZ, "wb") as f_out:
        f_out.writelines(f_in)

    print("✅ Saved:", OUTPUT_XML)
    print("✅ Saved:", OUTPUT_GZ)
    print("✅ Channels kept:", kept_channels)
    print("✅ Programmes kept:", kept_programmes)

if __name__ == "__main__":
    main()
