SmartSales – Enterprise Agent for Sales Lead Qualification
Google x Kaggle AI Agents Intensive – Capstone Project

Track: Enterprise Agents
Author: Daniyal Imran

1. Problem Overview

Most small and medium businesses struggle with sales lead qualification.
Manually reading leads, researching companies, scoring potential customers, and drafting first-contact outreach takes too long—especially for teams without dedicated SDRs.

SmartSales solves this by using multi-agent automation to:

Enrich company information

Qualify leads using rule-based + LLM-style reasoning

Draft personalized outreach

Schedule automated follow-ups

Store memory for future actions

2. Architecture Overview

SmartSales uses four core agents:

1. Orchestration Agent

Runs multi-threaded enrichment

Combines raw lead + enriched data

Writes memory logs and persists states

2. Qualification Agent

Uses rule-based scoring

Adds LLM-style reasoning

Writes decisions to CRM

Produces 0–100 qualification score

3. Outreach Agent

Drafts personalized email subject + body

Uses company signals, industry, and growth notes

4. Follow-Up Scheduler

Schedules actions in background threads

Writes follow-up metadata to CRM and MemoryBank

3. Tools Used
Custom Tools (built by me):

CRMTool – in-memory structured store

MemoryBank – long-term storage

CompanyEnricherTool – simulates external enrichment

LLM Reasoning Function – deterministic LLM-like reasoning

Agents (ADK-style design):

Orchestration

Qualification

Outreach

Follow-Up

4. Dataset

The system uses sample_leads.csv containing:

id,company_name,contact_name,contact_email,website,notes
L1,AcmePay,Ali,ali@acmepay.com,acmepay.com,Series A
L2,ShopRight,Ayesha,ayesha@shopright.pk,shopright.pk,

5. Pipeline Demonstration

The Kaggle notebook shows:

Loading sample_leads.csv

Running multi-agent pipeline

Displaying enriched company data

Scoring and qualifying leads

Drafting outreach message

Scheduling follow-ups

Evaluating precision & recall

Example output:

{
  "score": 75,
  "status": "qualified",
  "outreach": {
      "subject": "...",
      "body": "..."
  }
}

6. Evaluation

A dictionary of true labels is provided:

{"L1": "qualified", "L2": "nurture"}


Using this, SmartSales calculates:

Precision

Recall

True Positives

False Positives

True Negatives

False Negatives

This demonstrates the agent’s ability to match human judgment.

7. Why This Is an Enterprise Agent

SmartSales qualifies as an Enterprise Track project because:

It automates revenue-critical operations

It improves sales workflow productivity

It reduces manual human labor

It integrates multi-agent design patterns

It can be expanded into real CRM workflow systems

Enterprises (SMBs, SaaS, fintech, e-commerce) can save hours weekly using this workflow.

8. Future Improvements

If ADK server tools were added, we could:

Integrate Gemini for real LLM reasoning

Add web search-based enrichment

Deploy to a live endpoint

Add a proper vector memory database

Add voice call summarization agents

9. Conclusion

SmartSales demonstrates a complete multi-agent enterprise automation system using modular ADK-style architecture.

It satisfies all required Capstone criteria:

✔ Multi-agent system
✔ Real-world use case
✔ Tools + memory + orchestration
✔ Enterprise workflow automation
✔ Kaggle Notebook demonstration
✔ GitHub repo with full code
