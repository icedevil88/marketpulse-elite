"""Publish one prewritten, educational topic in both languages each day.
No live prices, buy/sell signals, or personalized advice.
"""
from datetime import datetime
from zoneinfo import ZoneInfo
import json, os, urllib.parse, urllib.request

TOPICS = [
("📚 Börsenwissen: Diversifikation\n\nWer nur eine Aktie hält, trägt ein hohes unternehmensspezifisches Risiko. Eine breite Streuung kann dieses Risiko reduzieren, schützt aber nicht vor allgemeinen Marktverlusten.\n\nBildungsinhalt, keine persönliche Anlageberatung.",
 "📚 Market basics: Diversification\n\nHolding just one stock creates significant company-specific risk. Diversification can reduce that risk but cannot eliminate broad market losses.\n\nEducational content, not personalized investment advice."),
("🔎 Aktienanalyse: Umsatz ist nicht Gewinn\n\nPrüfe neben dem Umsatz auch Margen, Cashflow und Verschuldung. Starkes Wachstum allein bedeutet nicht automatisch eine attraktive Bewertung.\n\nBildungsinhalt, keine persönliche Anlageberatung.",
 "🔎 Stock research: Revenue is not profit\n\nLook beyond sales growth: examine margins, cash flow and debt. Fast growth does not automatically make a stock attractively valued.\n\nEducational content, not personalized investment advice."),
("🛡️ Krypto-Risiko: Verwahrung\n\nPrivate Keys und Recovery-Phrasen gehören niemals in Chats oder Cloud-Notizen. Prüfe Gegenparteirisiken und sichere Backups, bevor du Kryptowährungen verwahrst.\n\nBildungsinhalt, keine persönliche Anlageberatung.",
 "🛡️ Crypto risk: Custody\n\nNever share private keys or recovery phrases in chats or cloud notes. Understand counterparty risk and secure backups before holding crypto assets.\n\nEducational content, not personalized investment advice."),
("📊 Börsenwissen: Bewertung\n\nDas Kurs-Gewinn-Verhältnis ist nur ein Ausgangspunkt. Vergleiche Unternehmen mit ähnlichen Geschäftsmodellen und berücksichtige Wachstum, Qualität und Risiken.\n\nBildungsinhalt, keine persönliche Anlageberatung.",
 "📊 Market basics: Valuation\n\nThe price-to-earnings ratio is only a starting point. Compare similar businesses and account for growth, quality and risks.\n\nEducational content, not personalized investment advice."),
("⚖️ Risikomanagement\n\nÜberlege vor einer Investition, wie groß ein möglicher Verlust sein darf und ob du kurzfristig auf das Geld angewiesen bist. Hohe Renditechancen gehen meist mit hohen Risiken einher.\n\nBildungsinhalt, keine persönliche Anlageberatung.",
 "⚖️ Risk management\n\nBefore investing, consider the size of a loss you could tolerate and whether you need the money soon. Higher potential returns usually involve greater risk.\n\nEducational content, not personalized investment advice."),
("🔍 Krypto-Recherche\n\nAchte bei Projekten auf überprüfbare Entwicklung, Token-Angebot, Sicherheitsrisiken und Konzentration der Bestände. Social-Media-Hype ist keine belastbare Analyse.\n\nBildungsinhalt, keine persönliche Anlageberatung.",
 "🔍 Crypto research\n\nReview verifiable development, token supply, security risks and ownership concentration. Social-media hype is not reliable due diligence.\n\nEducational content, not personalized investment advice."),
("🗓️ Wochencheck: Investmentthese\n\nNotiere, warum du ein Unternehmen interessant findest, welche Annahmen dahinterstehen und welche Fakten deine These widerlegen würden. Überprüfe sie regelmäßig.\n\nBildungsinhalt, keine persönliche Anlageberatung.",
 "🗓️ Weekly check: Investment thesis\n\nWrite down why a business interests you, the assumptions behind your thesis, and what evidence would disprove it. Review it regularly.\n\nEducational content, not personalized investment advice.")
]
def send(token, channel, message):
    data=urllib.parse.urlencode({"chat_id":channel,"text":message}).encode()
    req=urllib.request.Request("https://api.telegram.org/bot"+token+"/sendMessage",data=data)
    with urllib.request.urlopen(req,timeout=20) as response:
        result=json.load(response)
    if not result.get("ok"):
        raise RuntimeError("Telegram rejected "+channel)
    print("Published to "+channel)
def main():
    token=os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token: raise SystemExit("Missing TELEGRAM_BOT_TOKEN secret")
    now=datetime.now(ZoneInfo("Europe/Brussels"))
    index=now.toordinal()%len(TOPICS)
    de,en=TOPICS[index]
    send(token,"@MarketPulseEliteDE",de)
    send(token,"@MarketPulseEliteGlobal",en)
if __name__=="__main__": main()
