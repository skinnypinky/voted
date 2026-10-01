import requests
import xml.etree.ElementTree as ET
from urllib.parse import urljoin


def get_votering_titles(status_url):
    if not status_url:
        return {}

    url = urljoin("https://data.riksdagen.se/", status_url)

    response = requests.get(url, timeout=10)
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


def get_document(beteckning, riksmote):
    url = (
        "https://data.riksdagen.se/dokumentlista/"
        f"?rm={riksmote}&bet={beteckning}&doktyp=bet&utformat=json"
    )

    response = requests.get(url, timeout=10)
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
                "votering_titles": get_votering_titles(
                    document.get("dokumentstatus_url_xml")
                )
            }

    return None