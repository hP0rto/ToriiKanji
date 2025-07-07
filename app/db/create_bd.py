import sqlite3
from lxml import etree

# Conecta ao banco
conn = sqlite3.connect("toriikanji.db")
cursor = conn.cursor()
with open("schema.sql", "r", encoding="utf-8") as f:
    sql_script = f.read()
cursor.executescript(sql_script)

print("schema.sql executed")

# Lê o XML
tree = etree.parse("kanjidic2.xml")
root = tree.getroot()

for character in root.findall("character"):
    kanji = character.findtext("literal")
    grade = character.findtext("misc/grade")
    jlpt = character.findtext("misc/jlpt")

    onyomi = []
    kunyomi = []
    significados = []

    rmgroup = character.find("reading_meaning/rmgroup")
    if rmgroup is not None:
        for reading in rmgroup.findall("reading"):
            rtype = reading.get("r_type")
            if rtype == "ja_on":
                onyomi.append(reading.text)
            elif rtype == "ja_kun":
                kunyomi.append(reading.text)
        for meaning in rmgroup.findall("meaning"):
            if meaning.get("m_lang") is None:  # só inglês
                significados.append(meaning.text)

    cursor.execute("""
        INSERT OR REPLACE INTO kanji_dict
        (kanji, onyomi, kunyomi, meaning, grade, jlpt)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        kanji,
        ", ".join(onyomi),
        ", ".join(kunyomi),
        "; ".join(significados),
        int(grade) if grade else None,
        int(jlpt) if jlpt else None
    ))

conn.commit()

cursor.execute("SELECT COUNT(*) FROM kanji_dict")
total = cursor.fetchone()[0]
print("Total de kanji no banco:", total)
conn.close()
