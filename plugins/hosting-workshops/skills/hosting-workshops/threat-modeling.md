# Threat-Modeling Workshop

Threat modeling answers four questions about a system — *what are we working on, what can go wrong, what are we going to do about it, did we do a good enough job?* — and it's done as a **group** because no single role can answer them: dev knows the implementation, ops the deployment, product the data, security the attack landscape. The skipped move is forgetting that (the "Hero Threat Modeler") — and triaging/owning the mitigations rather than just admiring the threats.

## The recipe

1. **Get the right room; exclude senior managers.** Dev (incl. architect) + product + ≥1 security specialist minimum; ops/QA/privacy valuable. Senior managers shift candid "here's what's attackable" into politics — a `tool-group-dynamics.md` safety problem. Assign a facilitator and notetaker.
2. **Scope & model together** (the first question). Build/review a **data flow diagram**; agree trust boundaries and assets. A *contested* model can't be threat-modeled — reach consensus first.
3. **Enumerate** (the second question) as structured divergence (`tool-ideation.md`): **STRIDE-per-element** (Spoofing, Tampering, Repudiation, Information disclosure, Denial of service, Elevation of privilege) walked across each DFD element — or attack trees. Defer judgment; record every threat raised. The **Elevation of Privilege** card game gamifies this and draws non-security developers in.
4. **Triage** (`tool-convergence.md`) by likelihood × impact, pragmatically (High/Med/Low) — resist the CVSS rabbit hole.
5. **Mitigate** — each kept threat gets a **named owner** and a control, or an explicit acceptance. *No unowned threat.*
6. **Verify & repeat** — retro it; capture; schedule the refresh. Little-and-often (feature-sized ~15–30 min; cross-team ~90 min), *not* a big-bang "model everything" day.

## Required moves

- [ ] **Right room, no senior managers, blame-free** — or people won't admit weaknesses.
- [ ] **Model agreed before enumerating.**
- [ ] **STRIDE-per-element (or attack trees); EoP to draw devs in** — structured, not blank-page.
- [ ] **Triaged pragmatically** (H/M/L), not a scoring debate.
- [ ] **Every kept threat owned** with a control.
- [ ] **Little-and-often, continuously refreshed** — not one big-bang.

## Failure modes

- **The Hero Threat Modeler** — one expert solo; the room's knowledge never enters.
- **Boiling the ocean** — modeling the whole system at once; outputs too big to act on.
- **Admiration of the problem** — endless enumeration, no owned mitigations.
- **Security-team-only** — threats found, mitigations disconnected from implementation.
- **Contested model** — enumerating before agreeing what the system is.
- **One-and-done** — a register filed and never refreshed.

## Depth

`Hosting Workshops/corpus/applied-playbooks/threat-modeling-workshop.md` in an optional source corpus (when available).
