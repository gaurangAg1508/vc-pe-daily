#!/usr/bin/env python3
"""Build a daily VC/PE reading edition from public RSS feeds. Standard library only."""
from __future__ import annotations
import email.utils, html, json, re, urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
CONFIG, DATA = ROOT / "config", ROOT / "site" / "data"
ARCHIVE = DATA / "archive"
HEADERS = {"User-Agent": "VC-PE-Daily/1.0 (personal research reader)"}
DEAL_TERMS = ["funding","raised","raises","series a","series b","series c","seed round","venture capital","private equity","investment","invests","acquires","acquisition","buyout","growth capital","fundraise","valuation","ipo","exit","merger","fund closes","debt financing"]
ANALYSIS_TERMS = ["analysis","explainer","deep dive","how ","why ","lessons","strategy","valuation","venture capital","private equity","investing","market","founder","unit economics","business model","portfolio"]
SECTOR_TERMS = {
 "AI / software":[" ai ","artificial intelligence","machine learning","software","saas"],
 "Fintech":["fintech","payments","lending","banking","financial services"],
 "Healthcare":["health","medtech","biotech","pharma","hospital"],
 "Climate / energy":["climate","energy","battery"," ev ","carbon","renewable"],
 "Consumer":["consumer","commerce","retail","d2c","brand"],
 "Industrial / deep tech":["deep tech","manufacturing","robotics","semiconductor","industrial"]
}

def clean(value):
    return re.sub(r"\s+"," ",html.unescape(re.sub(r"<[^>]+>"," ",value or ""))).strip()

def lname(tag):
    return tag.rsplit("}",1)[-1].split(":")[-1].lower()

def child(node, names):
    for c in list(node):
        if lname(c.tag) in names:
            return "".join(c.itertext()).strip()
    return ""

def parse_date(value):
    if not value: return None
    try:
        dt=email.utils.parsedate_to_datetime(value.strip())
        if dt.tzinfo is None: dt=dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception: pass
    try:
        dt=datetime.fromisoformat(value.strip().replace("Z","+00:00"))
        if dt.tzinfo is None: dt=dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception: return None

def get_feed(source):
    req=urllib.request.Request(source["url"],headers=HEADERS)
    try:
        with urllib.request.urlopen(req,timeout=22) as res: payload=res.read(4_000_000)
        root=ET.fromstring(payload)
        nodes=[n for n in root.iter() if lname(n.tag) in ("item","entry")]
        output=[]
        for n in nodes[:50]:
            title=clean(child(n,("title",)))
            url=""
            for c in list(n):
                if lname(c.tag)=="link":
                    url=(c.attrib.get("href") or c.text or "").strip()
                    if c.attrib.get("rel","alternate")=="alternate": break
            summary=clean(child(n,("description","summary","encoded","content")))[:620]
            published=parse_date(child(n,("pubdate","published","updated","date")))
            publisher=child(n,("source",))
            if title and url:
                output.append({"title":title,"url":url,"summary":summary,
                  "published_at":published.isoformat() if published else None,"_published":published,
                  "source":publisher or source["name"],"region":source.get("region","Global"),
                  "kind":source.get("kind","news")})
        return output,None
    except Exception as exc:
        return [],f"{source['name']}: {type(exc).__name__}: {str(exc)[:140]}"

def norm(title):
    title=re.sub(r"\s+-\s+[^-]+$","",title)
    return re.sub(r"[^a-z0-9]+","",title.lower())

def is_deal(item):
    text=(item["title"]+" "+item["summary"]).lower()
    return any(t in text for t in DEAL_TERMS)

def score(item,now):
    text=(item["title"]+" "+item["summary"]).lower()
    value=sum(2.5 for t in DEAL_TERMS if t in text)+sum(1.6 for t in ANALYSIS_TERMS if t in text)
    if item["kind"]=="analysis": value+=5
    if item["_published"]:
        age=max(0,(now-item["_published"]).total_seconds()/3600)
        value+=max(0,8-age/9)
    if len(item["summary"])>160: value+=1.2
    if any(t in text for t in ("opinion","sponsored","press release")): value-=2
    return value

def sector_for(text):
    padded=" "+text.lower()+" "
    for sector,terms in SECTOR_TERMS.items():
        if any(t in padded for t in terms): return sector
    return "Not clear from the headline / excerpt"

def deal_lens(item):
    text=(item["title"]+" "+item["summary"]).lower()
    sector=sector_for(text)
    hypotheses=[]
    if any(t in text for t in ("expand","expansion","scale","growth","new market","capacity")):
        hypotheses.append("Capital may fund expansion or capacity growth. Test whether demand and execution capacity justify the pace.")
    if any(t in text for t in ("ai","artificial intelligence","software","platform","technology","automation")):
        hypotheses.append("The investor may be underwriting product differentiation or technology-led productivity. Test defensibility, switching costs and distribution.")
    if any(t in text for t in ("revenue","customer","users","profit","orders","traction")):
        hypotheses.append("Reported traction may reduce demand risk. Verify revenue quality, retention, repeat usage and customer concentration.")
    if any(t in text for t in ("india","southeast asia","asia","emerging market","tier 2","rural")):
        hypotheses.append("The opportunity may involve an underpenetrated or fragmented market. Validate willingness to pay, go-to-market costs and local competition.")
    if not hypotheses:
        hypotheses=[
          "The investor may see a path to attractive growth relative to the price paid. The excerpt does not establish the actual investment thesis.",
          "The round may provide runway for a next milestone. Identify that milestone and what evidence would demonstrate progress."
        ]
    questions=[
      "What specific milestone does this capital make possible, and by when?",
      "What evidence supports product-market fit: retention, repeat purchase, cohort behaviour or gross margin?",
      "What could make this investment lose money: competition, regulation, execution, dilution or valuation?"
    ]
    if sector=="AI / software": questions[1]="Is the product defensible beyond access to a foundation model: proprietary data, workflow integration, distribution or switching costs?"
    elif sector=="Healthcare": questions[1]="What are the regulatory, clinical validation, reimbursement and provider-adoption hurdles?"
    elif sector=="Climate / energy": questions[1]="Do project economics work after capex, utilisation, offtake, policy support and cost of capital?"
    elif sector=="Fintech": questions[1]="How do credit losses, fraud, CAC, take rate and contribution margin behave by cohort?"
    return {"sector":sector,"reported_context":item["summary"] or "The feed supplied no excerpt. Open the source article to verify deal facts.",
      "hypotheses":hypotheses[:3],"what_to_validate":["Use of proceeds and runway","Revenue growth, gross margin and burn","Retention, repeat usage and customer concentration","Competitive advantage and likely exit paths"],
      "vcic_questions":questions,
      "caveat":"These are first-pass hypotheses generated from the headline and RSS excerpt, not confirmed statements from the investor. Read the linked article and verify the facts."}

def public_item(item,now):
    pub=item.get("_published")
    return {"title":item["title"],"url":item["url"],"summary":item["summary"],"source":item["source"],
      "region":item["region"],"kind":item["kind"],"published_at":item.get("published_at"),
      "hours_old":round(max(0,(now.astimezone(timezone.utc)-pub).total_seconds()/3600),1) if pub else None,
      "is_deal":is_deal(item)}

def main():
    settings=json.loads((CONFIG/"settings.json").read_text(encoding="utf-8"))
    sources=json.loads((CONFIG/"feeds.json").read_text(encoding="utf-8"))
    now=datetime.now(timezone.utc); local=now.astimezone(ZoneInfo(settings.get("timezone","Asia/Singapore")))
    cutoff=now-timedelta(hours=int(settings.get("max_age_hours",72)))
    errors=[]; collected=[]; seen=set()
    for source in sources:
        items,error=get_feed(source)
        if error: errors.append(error)
        for item in items:
            if item["_published"] and item["_published"]<cutoff: continue
            key=norm(item["title"])
            if not key or key in seen: continue
            seen.add(key); item["_score"]=score(item,now); collected.append(item)
    collected.sort(key=lambda x:x["_score"],reverse=True)
    india=[x for x in collected if x["region"]=="India"]
    global_items=[x for x in collected if x["region"]!="India"]
    target=int(settings.get("daily_story_count",8))
    selected=india[:int(settings.get("india_story_target",4))]+global_items[:int(settings.get("global_story_target",4))]
    chosen={x["url"] for x in selected}
    if len(selected)<target: selected += [x for x in collected if x["url"] not in chosen][:target-len(selected)]
    selected=selected[:target]
    deals=[x for x in selected if is_deal(x)]
    deal=deals[0] if deals else (selected[0] if selected else None)
    article_pool=[x for x in collected if x["kind"]=="analysis"]
    if not article_pool: article_pool=[x for x in collected if any(t in (x["title"]+" "+x["summary"]).lower() for t in ANALYSIS_TERMS)]
    if not article_pool: article_pool=selected[:]
    article=max(article_pool,key=lambda x:x["_score"]) if article_pool else None
    stories=[public_item(x,local) for x in selected]
    edition={"date":local.strftime("%Y-%m-%d"),"generated_at":local.isoformat(),"timezone":settings.get("timezone","Asia/Singapore"),
      "title":settings.get("site_title","VC & PE Daily"),"subtitle":settings.get("reader_subtitle",""),
      "story_count":len(stories),"sources_checked":len(sources),"sources_with_errors":errors,"stories":stories,
      "deal_of_the_day":({**public_item(deal,local),"analysis":deal_lens(deal)} if deal else None),
      "article_of_the_day":({**public_item(article,local),"why_read":"Selected from the configured investor and founder analysis feeds. Focus on the argument, evidence and assumptions—not just the conclusion.",
       "reading_prompts":["What is the author's central claim, and what evidence supports it?","Which assumption would you challenge as an investor?","What could this teach you about sourcing, diligence, valuation or value creation?"]} if article else None),
      "vcic_drill":["Would you invest? State your decision in one sentence.","What are the three strongest reasons to invest—and the three biggest risks?","What five diligence questions would you ask before submitting an IC memo?"],
      "editor_note":"Automated first-pass curation. Headlines and excerpts are discovery aids; use the publisher link for full context and verify transaction details."}
    DATA.mkdir(parents=True,exist_ok=True); ARCHIVE.mkdir(parents=True,exist_ok=True)
    (DATA/"latest.json").write_text(json.dumps(edition,ensure_ascii=False,indent=2),encoding="utf-8")
    (ARCHIVE/f"{edition['date']}.json").write_text(json.dumps(edition,ensure_ascii=False,indent=2),encoding="utf-8")
    index=ARCHIVE/"index.json"; dates=set()
    if index.exists():
        try: dates.update(json.loads(index.read_text(encoding="utf-8")))
        except Exception: pass
    dates.add(edition["date"])
    index.write_text(json.dumps(sorted(dates,reverse=True)[:int(settings.get("archive_index_limit",180))],indent=2),encoding="utf-8")
    print(f"Generated {edition['date']}: {len(stories)} stories, {len(errors)} feed errors.")
    if not collected: print("Warning: no recent feed items. Check RSS access and feed URLs.")

if __name__=="__main__": main()
