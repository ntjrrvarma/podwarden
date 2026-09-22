# Day 2: Kubernetes Telemetry Enricher & Offline Fallback Mode

**Project:** PodWarden - Autonomous K8s Incident Triage Agent  
**Date:** September 22, 2026  
**Status:** Enricher implemented, Offline mock mode verified, Ingress pipeline wired.

## 🎯 Today's Objective
Move beyond simple alert reception by building the telemetry harvesting layer. When an alert fires, PodWarden must automatically query the target Kubernetes pod to extract recent container logs, restart counts, termination reasons, and event histories.

## 🏗️ What Was Built Today

1. **Kubernetes Client Integration (`src/enrichers/k8s.py`):**
   * Integrated the official Python Kubernetes client (`kubernetes`).
   * Configured authentication detection supporting both in-cluster service accounts and local `~/.kube/config` profiles.

2. **Robust Offline Fallback Mode:**
   * Added automated exception catching that falls back to a simulated telemetry payload if no active cluster is present. This allows local development and testing without requiring a live cloud connection.

3. **Ingress Pipeline Wiring (`src/main.py`):**
   * Connected the webhook background task to the telemetry enricher.
   * Successfully processed mock Prometheus payloads, parsing target pod names and logging structured restart metrics and crash logs.

## 🚀 Roadmap for Tomorrow (Day 3)
* **LLM Triage Engine (`src/engine/triage.py`):** Feed the harvested telemetry dictionary into a structured reasoning model, utilizing our Pydantic contracts to output a validated root-cause analysis and safe `kubectl` remediation steps.

---
*Building open-source infrastructure tools takes time and compute. If PodWarden sounds like a tool that will save your team's on-call sleep, consider [sponsoring my work on GitHub](https://github.com/sponsors/ntjrrvarma).*