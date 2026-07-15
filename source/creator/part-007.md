Dobry wynik nie dowodzi dobrej decyzji. Zły wynik nie dowodzi złej decyzji.

## 6.7. Decision Patterns

Pola:

| Pole | Typ |
|---|---|
| Pattern | Title |
| Pattern Type | Select |
| Domains | Multi-select |
| Status | Select |
| Confidence | Select |
| Description | Text |
| Evidence Decisions | Relation → Decision Cases |
| Evidence Reviews | Relation → Decision Reviews |
| Alternative Explanation | Text |
| Implication for Advice | Text |
| Knowledge Node | Relation → Knowledge Nodes |
| Review Date | Date |
| Last Reviewed | Date |
| Last Edited | Last edited time |

Status:

```text
Hypothesis
Observed
Validated
Disputed
Superseded
```

Nie potwierdzaj wzorca na podstawie jednego wyniku.

Wzorzec zachowania nie jest diagnozą kliniczną.

## 6.8. Decision Lessons & Heuristics

Pola:

| Pole | Typ |
|---|---|
| Lesson | Title |
| Domains | Multi-select |
| Applies When | Text |
| Do | Text |
| Avoid | Text |
| Evidence Count | Number |
| Source Decisions | Relation → Decision Cases |
| Source Reviews | Relation → Decision Reviews |
| Confidence | Select |
| Status | Select |
| Last Validated | Date |
| Review Date | Date |
| Knowledge Node | Relation → Knowledge Nodes |
| Last Edited | Last edited time |

Jedna decyzja zwykle daje lekcję Draft, nie Validated.

## 6.9. Decision Dashboard

Dodaj widoki:

- Decision Pipeline;
- Reviews Due;
- Chosen Options;
- Recent Decision Reviews;
- Decision Patterns;
- Validated Lessons.

## 6.10. Pierwsza decyzja

Pierwszym Decision Case może być:

```text
Czy wdrożyć pełny Personal AI Workspace?
```

Warianty:

1. nie tworzyć systemu;
2. stworzyć tylko prosty notatnik;
3. stworzyć pełny system.

Po 30 dniach zaplanuj przegląd wartości i ciężaru obsługi.

---

## Etap 7 z 12 — Tasks

W `Tasks` utwórz bazę `Task Outbox`.

## 7.1. Task Outbox — pola

| Pole | Typ |
|---|---|
| Task | Title |
| Target List | Select |
| Category | Select |
| Status | Select |
| Automation Mode | Select |
| Execution Owner | Select |
| Due Date | Date |
| Recurrence Rule | Text |
| Reason | Text |
| Deduplication Key | Text |
| Source Type | Select |
| Source URL | URL |
| Person | Relation → People & Agents |
| Relationship | Relation → Relationships |
| Interaction | Relation → Interactions & Notes |
| Commitment | Relation → Commitments & Follow-ups |
| Backend | Select |
| Backend Status | Select |
| GitHub Repository | Text |
| GitHub Project | Text |
| GitHub Issue Number | Number |
| GitHub Issue URL | URL |
| Project Assignment | Select |
| Calendar Event ID | Text |
| Calendar Event URL | URL |
| External Invitees | Text |
| Invitees Approved | Checkbox |
| Last Sync Attempt | Date |
| Sync Error | Text |
| Last Edited | Last edited time |

## 7.2. Priorytety

```text
A — pilne, blokujące albo kosztowne w przypadku zwłoki
B — ważne, ale nie natychmiastowe
C — backlog, pomysły i działania opcjonalne
```

Lista A powinna zawierać około pięciu aktywnych zadań.

## 7.3. Backend zadań

Wybierz pierwszy dostępny i zaakceptowany wariant:

### Wariant A — Google Tasks

Użyj tylko wtedy, gdy dostępny jest prawdziwy konektor zadań.

### Wariant B — GitHub Issues

Rekomendowany, jeżeli użytkownik korzysta z GitHuba.

Ustal:

- repozytorium;
- opcjonalny GitHub Project;
- właścicieli zadań;
- etykiety.

Tytuły:

```text
[USER][A][PRACA] Przygotować plan migracji
[ASSISTANT][B][NOTION] Naprawić niespójną relację
[SHARED][C][BIZNES] Przeanalizować nowy kanał sprzedaży
```

Utwórz etykiety:

```text
lista:A
lista:B
lista:C
```

Każde issue będące zadaniem musi mieć dokładnie jedną etykietę priorytetu.

Zadanie cykliczne także otrzymuje jedną z tych etykiet. Cykliczność zapisuje się osobno.

Przed utworzeniem:

1. sprawdź duplikaty;
2. sprawdź liczbę zadań A;
3. utwórz issue;
4. zweryfikuj numer i URL;
5. zweryfikuj etykietę;
6. zapisz wynik w Task Outbox.

Jeżeli konektor nie obsługuje GitHub Projects, nie twierdź, że issue zostało dodane do projektu. Ustaw:

```text
Project Assignment = Pending
```

albo:

```text
Project Assignment = Unsupported
```

### Wariant C — Notion Only

Jeśli brak zewnętrznego backendu, Task Outbox pozostaje systemem zadań.

## 7.4. Tryb automatyzacji

```text
Auto
Confirm First
```

Uzgodnij z użytkownikiem zasady.

---

## Etap 7A — System Evolution Lab

Ten moduł tworzy jeden jawny „zeszyt” działania systemu. Nie jest prywatnym scratchpadem ani ukrytym tokiem rozumowania.

Utwórz pod głównym Workspace pełnostronicową bazę:

```text
System Evolution Lab
```

Pola:

| Pole | Typ |
|---|---|
| Entry | Title |
| Entry Type | Select |
| Status | Select |
| Captured At | Date |
| Review Date | Date |
| Affected Area | Multi-select |
| Source URL | URL |
| Observation | Text |
| Evidence | Text |
| Impact | Select |
| Frequency | Select |
| Confidence | Select |
| Sensitivity | Select |
| Suggested Improvement | Text |
| Proposal Scope | Text |
| Benefits | Text |
| Costs and Risks | Text |
| Counterarguments | Text |
| Rollback Plan | Text |
| Needs User Approval | Checkbox |
| User Decision | Text |
| Review Outcome | Text |
| Next Action | Text |
| Related Modules | Multi-select |
| Created | Created time |
| Last Edited | Last edited time |
| Entry ID | Unique ID |

Entry Type:

```text
Observation
Incident
Pattern
Weekly Review
Improvement Proposal
Decision
Implementation Result
```

Status:

```text
Captured
Monitoring
Ready for Review
Proposed
Approved
Rejected
Implemented
Reverted
Archived
```

Impact:

```text
Critical
High
Medium
Low
```

Frequency:

```text
One-off
Repeated
Systemic
Unknown
```

Utwórz widoki:

```text
Obserwacje
Tygodniowe przeglądy
Propozycje ulepszeń
```

## Kiedy dodawać obserwację

Zapisuj, gdy wystąpi:

- korekta użytkownika;
- błąd konektora;
- brak kontekstu pogarszający wynik;
- niepotrzebnie powtórzona praca;
- niejasna lub sprzeczna reguła;
- powtarzalny wzorzec;
- wysokowartościowa możliwość ulepszenia;
- nieoczekiwany rezultat wdrożenia lub rollback.

