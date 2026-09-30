import requests

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
                "title": document["titel"]
            }

    print("No matching document:", beteckning, riksmote)
    return None