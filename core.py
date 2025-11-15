# core.py
"""
SmartSales core module - Sales Lead Qualification Agent (skeleton)
This file contains the main tools and agent pipeline. It is intentionally
self-contained and makes NO external API calls. Replace placeholders with
real ADK tools/LLM calls when deploying.
"""

import time
import logging
from threading import Thread
from queue import Queue
from typing import Dict, Any, List
import json

# Basic logging / observability
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SmartSales")

# ---------- Simple in-memory "CRM" tool (custom tool) ----------
class CRMTool:
    def __init__(self):
        self.db: Dict[str, Dict[str, Any]] = {}

    def upsert(self, lead_id: str, payload: Dict[str, Any]) -> None:
        self.db[lead_id] = {**self.db.get(lead_id, {}), **payload}
        logger.info(f"CRM upsert: {lead_id} -> {payload}")

    def get(self, lead_id: str) -> Dict[str, Any]:
        return self.db.get(lead_id, {})

    def all(self) -> Dict[str, Dict[str, Any]]:
        return self.db

# ---------- Simple Memory Bank (long-term memory) ----------
class MemoryBank:
    def __init__(self):
        self.mem: Dict[str, List[Dict[str, Any]]] = {}

    def write(self, lead_id: str, record: Dict[str, Any]) -> None:
        self.mem.setdefault(lead_id, []).append(record)
        logger.info(f"Memory write: {lead_id} <- {record}")

    def read(self, lead_id: str) -> List[Dict[str, Any]]:
        return self.mem.get(lead_id, [])

# ---------- Enrichment Tool (simulated: replace with Search/Enrich ADK tool) ----------
class CompanyEnricherTool:
    def run(self, lead: Dict[str, Any]) -> Dict[str, Any]:
        # Simulated enrichment; in real project, call Search/Company APIs or ADK tools
        enriched = {
            "website": lead.get("website", ""),
            "industry": "FinTech" if "fin" in lead.get("company_name","").lower() else "SaaS",
            "employee_count": 75 if "Series A" in lead.get("notes", "") else (120 if "Scale-up" in lead.get("notes","") else 12),
            "tech_stack": ["Python","Postgres"] if "Data" in lead.get("company_name","") else ["Node.js"],
            "recent_news": lead.get("notes", "") 
        }
        logger.info(f"Enricher -> {lead['id']} : {enriched}")
        return enriched

# ---------- Simple LLM placeholder (simulate LLM reasoning) ----------
def llm_reasoning_prompt(prompt: str) -> str:
    # In real implementation, call ADK LLM tool (Gemini) with this prompt
    # Here we return deterministic simulated response for reproducibility
    if "qualification" in prompt.lower():
        return "LLM: lead looks promising due to funding and tech-stack match."
    return "LLM: default reasoning."

# ---------- Agents ----------
class OrchestrationAgent:
    def __init__(self, enricher: CompanyEnricherTool, crm: CRMTool, memory: MemoryBank):
        self.enricher = enricher
        self.crm = crm
        self.memory = memory

    def handle_batch(self, leads: List[Dict[str,Any]]) -> List[Dict[str,Any]]:
        # Demonstrates "parallel" enrichment via threads (conceptual)
        q = Queue()
        results = []

        def worker(lead):
            enriched = self.enricher.run(lead)
            self.memory.write(lead['id'], {"enriched": enriched, "ts": time.time()})
            combined = {**lead, **enriched}
            q.put(combined)

        threads = []
        for lead in leads:
            t = Thread(target=worker, args=(lead,))
            t.start()
            threads.append(t)
        for t in threads:
            t.join()
        while not q.empty():
            results.append(q.get())
        logger.info(f"Orchestration finished for batch of {len(leads)} leads.")
        return results

class QualificationAgent:
    def __init__(self, crm: CRMTool, memory: MemoryBank):
        self.crm = crm
        self.memory = memory

    def score(self, lead: Dict[str,Any]) -> Dict[str,Any]:
        # Rule-based scoring + LLM reasoning (simulated)
        score = 0
        reasons = []
        if lead.get("employee_count",0) >= 50:
            score += 30
            reasons.append("Team size >= 50")
        if "FinTech" in lead.get("industry",""):
            score += 25
            reasons.append("Industry match: FinTech")
        if "Series A" in lead.get("recent_news",""):
            score += 20
            reasons.append("Funding signal: Series A")

        # LLM reasoning (simulate)
        llm_text = llm_reasoning_prompt("qualification reasoning for lead")
        reasons.append(llm_text)
        # normalize to 0-100
        score = min(100, score)
        result = {"score": score, "reasons": reasons}
        logger.info(f"Qualification -> {lead['id']} score={score}")
        # persist to CRM and memory
        self.crm.upsert(lead['id'], {"score": score, "status": "qualified" if score>50 else "nurture"})
        self.memory.write(lead['id'], {"qualification": result, "ts": time.time()})
        return result

class OutreachAgent:
    def __init__(self, crm: CRMTool):
        self.crm = crm

    def draft(self, lead: Dict[str,Any]) -> Dict[str,str]:
        # In real system, you'd call an LLM to generate personalized outreach
        subj = f"Quick question about {lead.get('company_name')} and your {lead.get('industry')} stack"
        body = (f"Hi {lead.get('contact_name')},\n\n"
                f"I noticed {lead.get('recent_news','your recent activities')} at {lead.get('company_name')} and thought there might be a fit.\n\n"
                f"Are you available for a 15-minute call next week?\n\nBest,\nDaniyal")
        logger.info(f"Outreach drafted -> {lead['id']}")
        self.crm.upsert(lead['id'], {"outreach": {"subject": subj, "body": body}})
        return {"subject": subj, "body": body}

# ---------- Follow-up scheduler (long-running ops simulated) ----------
class FollowUpScheduler:
    def __init__(self, crm: CRMTool, memory: MemoryBank):
        self.crm = crm
        self.memory = memory
        self.scheduled = {}

    def schedule(self, lead_id: str, delay_seconds: int, note: str):
        # Instead of real scheduling, simulate pause/resume via thread
        def waiter():
            logger.info(f"Follow-up scheduled for {lead_id} in {delay_seconds}s")
            time.sleep(delay_seconds)
            # on wake, write to CRM and memory as "followup_due"
            self.crm.upsert(lead_id, {"followup_due": True})
            self.memory.write(lead_id, {"followup": note, "ts": time.time()})
            logger.info(f"Follow-up due for {lead_id}")

        t = Thread(target=waiter, daemon=True)
        t.start()
        self.scheduled[lead_id] = {"thread": t, "note": note, "delay": delay_seconds}
        return True

# ---------- Evaluation utilities ----------
def evaluate_predictions(crm: CRMTool, labeled: Dict[str,str]) -> Dict[str, float]:
    # labeled: dict lead_id -> "qualified"/"nurture"
    tp = fp = tn = fn = 0
    for lead_id, label in labeled.items():
        rec = crm.get(lead_id)
        predicted = rec.get("status","nurture")
        if predicted=="qualified" and label=="qualified": tp+=1
        if predicted=="qualified" and label!="qualified": fp+=1
        if predicted!="qualified" and label!="qualified": tn+=1
        if predicted!="qualified" and label=="qualified": fn+=1
    precision = tp / (tp+fp) if (tp+fp)>0 else 0.0
    recall = tp / (tp+fn) if (tp+fn)>0 else 0.0
    return {"precision": precision, "recall": recall, "tp":tp,"fp":fp,"tn":tn,"fn":fn}

# ---------- Pipeline function ----------
def pipeline(leads: List[Dict[str,Any]], labeled: Dict[str,str]=None) -> Dict[str,Any]:
    crm = CRMTool()
    memory = MemoryBank()
    enricher = CompanyEnricherTool()

    orch = OrchestrationAgent(enricher, crm, memory)
    qual = QualificationAgent(crm, memory)
    out = OutreachAgent(crm)
    scheduler = FollowUpScheduler(crm, memory)

    enriched = orch.handle_batch(leads)
    processed = []
    for e in enriched:
        q = qual.score(e)
        # if qualified, draft outreach and schedule follow-up (simulate 5s delay)
        if q["score"] > 50:
            draft = out.draft(e)
            scheduler.schedule(e["id"], delay_seconds=5, note="1st follow up")
        processed.append({**e, **q})

    metrics = {}
    if labeled:
        metrics = evaluate_predictions(crm, labeled)
    return {"processed": processed, "crm": crm.all(), "memory": memory.mem, "metrics": metrics}

# ---------- If run as script for demo ----------
if __name__ == "__main__":
    # simple demo using sample_leads.csv if available
    import csv
    leads = []
    try:
        with open("sample_leads.csv", newline='', encoding='utf-8') as f:
            r = csv.DictReader(f)
            for row in r:
                # basic type conversions
                leads.append(dict(row))
    except FileNotFoundError:
        # fallback demo leads
        leads = [
            {"id":"L1","company_name":"AcmePay","contact_name":"Ali","contact_email":"ali@acmepay.com","website":"acmepay.com","notes":"Series A"},
            {"id":"L2","company_name":"ShopRight","contact_name":"Ayesha","contact_email":"ayesha@shopright.pk","website":"shopright.pk","notes":""}
        ]
    result = pipeline(leads, labeled={"L1":"qualified","L2":"nurture"})
    print(json.dumps(result["metrics"], indent=2))
    # keep main thread alive to allow follow-up threads to run briefly
    time.sleep(6)
    print("CRM snapshot:", json.dumps(result["crm"], indent=2))
