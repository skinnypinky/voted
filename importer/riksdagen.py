import requests

def get_pdf_url(document):
    filbilaga = document.get("filbilaga") or {}
    files = filbilaga.get("fil") or []

    if isinstance(files, dict):
        files = [files]

    for file in files:
        if file.get("typ") == "pdf" and file.get("url"):
            return file["url"].strip()
            
    return None

def get_document(beteckning, riksmote):
    url = (
        "https://data.riksdagen.se/dokumentlista/"
        f"?sok={beteckning}&rm={riksmote}&utformat=json"
    )

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

    except Exception as e:
        print("API error:", beteckning, e)
        return None

    documents = data.get("dokumentlista", {}).get("dokument", [])

    for document in documents:
        if (
            document.get("beteckning") == beteckning
            and document.get("rm") == riksmote
        ):
            return {
                "title": document["titel"],
                "notisrubrik": (document.get("notisrubrik") or "").strip() or None,
                "summary": (document.get("summary") or "").strip() or None,
                "organ": (document.get("organ") or "").strip() or None,
                "url": get_pdf_url(document)
            }
    
    print("No matching document:", beteckning, riksmote)
    return None