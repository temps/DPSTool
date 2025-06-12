import requests
from bs4 import BeautifulSoup

SIMCRAFT_URL = "https://www.simulationcraft.org/reports/PR_Raid.html"


def fetch_raid_dps(url: str = SIMCRAFT_URL):
    """Fetch raid DPS summary from SimulationCraft."""
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        return {"error": str(e)}

    soup = BeautifulSoup(resp.text, "html.parser")
    b = soup.find("b", string="Raid DPS:")
    raid_dps = b.parent.text.split(":", 1)[1].strip() if b else None

    ranking_row = None
    for table in soup.find_all("table"):
        if "DPS" in table.get_text():
            rows = table.find_all("tr")
            if len(rows) > 1:
                ranking_row = [c.get_text(" ", strip=True) for c in rows[1].find_all("td")]
            break

    return {"raid_dps": raid_dps, "top_ranking": ranking_row}
