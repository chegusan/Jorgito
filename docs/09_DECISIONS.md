# 09 — Decision Log

Use short ADR-style entries only for decisions that affect future work.

---

## D-001 — Target Hermes CLI/TUI first

Status: Accepted

Reason:
Arch Linux makes a Desktop-first path less attractive. The real target is the environment where the mascot will actually be used.

Consequence:
Desktop integration is outside MVP.

---

## D-002 — Native integration before custom adapter

Status: Accepted

Reason:
Minimize code, maintenance, token use, and failure points.

Consequence:
An adapter is only considered after measured native limitations.

---

## D-003 — Standard Petdex atlas for MVP

Status: Accepted

Reason:
Maximize compatibility and use existing validators/tooling.

Consequence:
No custom state format or v2 requirement unless evidence demands it.

---

## D-004 — Visual semantics

Status: Accepted

- review/thinking → Jorgito reading a book with glasses
- running/working → Jorgito digging/moving earth with a shovel

---

## D-005 — Cost-aware generation

Status: Accepted

Initial test only generates idle, review, and running.

Use deterministic derivation whenever it provides acceptable quality.
