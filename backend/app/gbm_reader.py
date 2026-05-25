"""Module to read GBM portfolio Excel files and return structured data."""
import openpyxl
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent.parent / "data" / "gbm"


def _parse_num(value) -> float:
    """Convierte un valor a float, manejando strings con formato de moneda/porcentaje.
    Ejemplos: '$23.20' -> 23.20, '-$0.92' -> -0.92, '2.02%' -> 2.02, '-' -> 0
    """
    if value is None or value == "-":
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    # Es string con formato
    s = str(value).strip()
    if s in ("-", "", "N/A"):
        return 0.0
    # Detectar signo negativo antes del símbolo de moneda: -$1.23
    negative = False
    if s.startswith("-"):
        negative = True
        s = s[1:]
    # Quitar símbolos de moneda y porcentaje
    s = s.replace("$", "").replace("%", "").replace(",", "").strip()
    try:
        result = float(s)
        return -result if negative else result
    except (ValueError, TypeError):
        return 0.0

# Tipo de cambio USD/MXN por defecto (fallback si falla la consulta)
_USD_MXN_FALLBACK = 19.45


def fetch_usd_mxn() -> float:
    """Obtiene el tipo de cambio USD/MXN en tiempo real.
    Usa httpx (ya instalado) para evitar bloqueos por User-Agent.
    Si falla, regresa el valor de fallback."""
    try:
        import httpx
        url = "https://api.frankfurter.app/latest?base=USD&symbols=MXN"
        resp = httpx.get(url, timeout=5, follow_redirects=True)
        resp.raise_for_status()
        data = resp.json()
        return round(float(data["rates"]["MXN"]), 4)
    except Exception:
        return _USD_MXN_FALLBACK


def read_nacional() -> list[dict]:
    """Read national market portfolio from Excel."""
    filepath = DATA_DIR / "portafolio-nacional.xlsx"
    if not filepath.exists():
        return []

    wb = openpyxl.load_workbook(filepath, read_only=True)
    ws = wb.active

    instruments = []
    current_section = ""

    for row in ws.iter_rows(values_only=True):
        if not row or row[0] is None:
            continue

        cell0 = str(row[0]).strip()

        # Detect section headers
        if cell0 in ("Mercado de Capitales Nacional", "Fondos de Inversión Deuda", "Efectivo"):
            current_section = cell0
            continue

        # Skip header rows and title
        if cell0 in ("Emisora/Fondo", "App GBM Portfolio"):
            continue

        # Skip cash entries with 0 value
        if cell0.startswith("EFEC.") and _parse_num(row[5]) == 0:
            continue

        try:
            ticker = cell0
            shares = _parse_num(row[1])
            avg_cost = _parse_num(row[2])
            market_price = _parse_num(row[3])
            market_value = _parse_num(row[5])
            gain_loss = _parse_num(row[6])
            var_day_pct = _parse_num(row[8])
            portfolio_pct = _parse_num(row[10])

            # Calculate return percentage
            if avg_cost > 0 and shares > 0:
                total_cost = avg_cost * shares
                return_pct = ((market_value - total_cost) / total_cost) * 100
            else:
                return_pct = 0

            instruments.append({
                "ticker": ticker,
                "section": current_section,
                "market": "Nacional",
                "currency": "MXN",
                "shares": shares,
                "avgCost": avg_cost,
                "marketPrice": market_price,
                "marketValue": market_value,
                "gainLoss": gain_loss,
                "returnPct": round(return_pct, 2),
                "varDayPct": var_day_pct,
                "portfolioPct": portfolio_pct
            })
        except (ValueError, TypeError, IndexError):
            continue

    wb.close()
    return instruments


def read_usa(usd_mxn: float = _USD_MXN_FALLBACK) -> list[dict]:
    """Read USA market portfolio from Excel."""
    filepath = DATA_DIR / "portafolio-usa.xlsx"
    if not filepath.exists():
        return []

    wb = openpyxl.load_workbook(filepath, read_only=True)
    ws = wb.active

    instruments = []
    current_section = ""

    for row in ws.iter_rows(values_only=True):
        if not row or row[0] is None:
            continue

        cell0 = str(row[0]).strip()

        if cell0 in ("Mercado de Capitales USA", "Liquidez"):
            current_section = cell0
            continue

        if cell0 in ("Emisora/Fondo", "App GBM Portfolio"):
            continue

        if cell0 == "efectivo" and _parse_num(row[5]) == 0:
            continue

        try:
            ticker = cell0
            shares = _parse_num(row[1])
            avg_cost = _parse_num(row[2])
            market_price = _parse_num(row[3])
            market_value = _parse_num(row[5])
            gain_loss = _parse_num(row[6])
            var_hist_pct = _parse_num(row[7])
            var_day_pct = _parse_num(row[8])
            cost_value = _parse_num(row[9])
            portfolio_pct = _parse_num(row[10])

            instruments.append({
                "ticker": ticker,
                "section": current_section,
                "market": "USA",
                "currency": "USD",
                "shares": shares,
                "avgCost": avg_cost,
                "marketPrice": market_price,
                "marketValue": market_value,
                "marketValueMXN": round(market_value * usd_mxn, 2),
                "gainLoss": gain_loss,
                "returnPct": round(((market_price - avg_cost) / avg_cost) * 100, 2) if avg_cost > 0 else 0,
                "varDayPct": var_day_pct,
                "costValue": cost_value,
                "portfolioPct": portfolio_pct
            })
        except (ValueError, TypeError, IndexError):
            continue

    wb.close()
    return instruments


def get_full_portfolio() -> dict:
    """Get complete portfolio data with summaries."""
    # Obtener tipo de cambio en tiempo real
    USD_MXN = fetch_usd_mxn()

    nacional = read_nacional()
    usa = read_usa(USD_MXN)

    # Calculate totals
    nacional_value = sum(i["marketValue"] for i in nacional)
    usa_value_usd = sum(i["marketValue"] for i in usa)
    usa_value_mxn = usa_value_usd * USD_MXN

    total_mxn = nacional_value + usa_value_mxn

    # Nacional cost
    nacional_cost = sum(i["avgCost"] * i["shares"] for i in nacional)
    # USA cost
    usa_cost = sum(i["costValue"] for i in usa if "costValue" in i and i["costValue"] > 0)
    if usa_cost == 0:
        usa_cost = sum(i["avgCost"] * i["shares"] for i in usa)

    total_cost_mxn = nacional_cost + (usa_cost * USD_MXN)
    total_gain = total_mxn - total_cost_mxn
    total_return_pct = (total_gain / total_cost_mxn * 100) if total_cost_mxn > 0 else 0

    return {
        "nacional": nacional,
        "usa": usa,
        "summary": {
            "nacionalValueMXN": round(nacional_value, 2),
            "usaValueUSD": round(usa_value_usd, 2),
            "usaValueMXN": round(usa_value_mxn, 2),
            "totalValueMXN": round(total_mxn, 2),
            "totalGainMXN": round(total_gain, 2),
            "totalReturnPct": round(total_return_pct, 2),
            "usdMxnRate": USD_MXN
        }
    }
