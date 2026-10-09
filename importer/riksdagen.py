import xml.etree.ElementTree as ET
from urllib.parse import urljoin


def get_votering_titles(status_url, session):
    if not status_url:
        return {}

    url = urljoin("https://data.riksdagen.se/", status_url)

    response = session.get(url, timeout=10)
    response.raise_for_status()

    root = ET.fromstring(response.content)

    titles = {}

    for point in root.iter():
        if point.tag.split("}")[-1] != "utskottsforslag":
            continue

        votering_id = None
        rubrik = None

        for child in point.iter():
            tag = child.tag.split("}")[-1]

            if tag == "votering_id":
                votering_id = child.text

            elif tag == "rubrik":
                rubrik = child.text

        if votering_id and rubrik:
            titles[votering_id.upper()] = rubrik

    return titles


def get_pdf_url(document):
    filbilaga = document.get("filbilaga") or {}
    files = filbilaga.get("fil") or []

    if isinstance(files, dict):
        files = [files]

    for file in files:
        if file.get("typ") == "pdf" and file.get("url"):
            return file["url"].strip()
            
    return None

def get_document(beteckning, riksmote, session):
    url = (
        "https://data.riksdagen.se/dokumentlista/"
        f"?rm={riksmote}&bet={beteckning}&doktyp=bet&utformat=json"
    )

    response = session.get(url, timeout=10)
    response.raise_for_status()

    documents = response.json()["dokumentlista"]["dokument"]

    for document in documents:
        if (
            document.get("beteckning") == beteckning
            and document.get("rm") == riksmote
        ):
            return {
                "dok_id": document["dok_id"],
                "title": document["titel"],
                "votering_titles": get_votering_titles(document.get("dokumentstatus_url_xml"), session),
                "notisrubrik": (document.get("notisrubrik") or "").strip() or None,
                "summary": (document.get("summary") or "").strip() or None,
                "organ": (document.get("organ") or "").strip() or None,
                "url": get_pdf_url(document)
            }
    
    print("No matching document:", beteckning, riksmote)
    return None

def get_ledamot_image(intressent_id, session):
    url = (
        "https://data.riksdagen.se/personlista/"
        f"?iid={intressent_id}&utformat=json"
    )

    response = session.get(url, timeout=10)
    response.raise_for_status()

    data = response.json()

    return data["personlista"]["person"]["bild_url_192"]
    