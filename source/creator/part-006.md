| Relationship | Relation → Relationships |
| Note Type | Select |
| Epistemic Status | Select |
| Perspective | Select |
| Confidence | Select |
| Sensitivity | Select |
| Summary | Text |
| Sources | Relation → Sources & Evidence |
| Action Needed | Checkbox |
| Knowledge Node | Relation → Knowledge Nodes |
| Last Edited | Last edited time |

Note Type:

```text
Interaction
Observation
Preference
Commitment
Follow-up
Boundary
Conflict
Milestone
Context
Correction
Hypothesis
Other
```

Epistemic Status:

```text
Fact
Reported Claim
Observation
Interpretation
Hypothesis
```

## 5.5. Commitments & Follow-ups

Pola:

| Pole | Typ |
|---|---|
| Name | Title |
| Type | Select |
| Owner | Relation → People & Agents |
| Related People | Relation → People & Agents |
| Relationship | Relation → Relationships |
| Interaction | Relation → Interactions & Notes |
| Status | Select |
| Target List | Select |
| Due Date | Date |
| Recurrence Rule | Text |
| Needs Task | Checkbox |
| Task Outbox | Relation → Task Outbox |
| Sources | Relation → Sources & Evidence |
| Summary | Text |

## 5.6. Zasady jakości Relations

- Nie pomijaj informacji tylko dlatego, że jest medyczna, intymna, seksualna, dotyczy substancji, dokładnej lokalizacji, finansów, religii, polityki, prawa albo prywatnego konfliktu.
- Zapisuj ją, gdy jest materialnie istotna dla relacji, bezpieczeństwa, granic, zdrowia, decyzji, czasu, ryzyk albo celów właściciela.
- Oznacz `Sensitivity: Confidential` i zapisz cel, źródło, datę/kontekst, epistemic status, perspektywę oraz confidence.
- Plotkę lub pogłoskę można zapisać jako `Reported Claim`, `Interpretation` albo `Hypothesis`, nigdy automatycznie jako fakt.
- Nie diagnozuj psychologicznie.
- Nie wyciągaj trwałej cechy z pojedynczego zachowania.
- Przy sprzeczności zachowaj obie wersje i źródła.
- Nie używaj wiedzy do manipulowania osobą.
- Nie umieszczaj wrażliwego szczegółu w mailu, wydarzeniu, zadaniu albo publicznym dokumencie bez właściwej zgody właściciela.
- Nie usuwaj automatycznie danych Relations.
- Domyślnie archiwizuj.
- Trwałe usunięcie wymaga jawnego polecenia użytkownika.

## 5.7. Profile startowe

Utwórz:

1. profil użytkownika jako `Human`;
2. profil asystenta jako `AI Assistant`;
3. typ relacji `assistant-to`;
4. typ odwrotny `assisted-by`;
5. relację:
   ```text
   [ASSISTANT_NAME] — assistant-to → [USER_NAME]
   ```

Zweryfikuj profile i relację.

---

## Etap 6 z 12 — Decision Engine

W `Decisions` utwórz stronę `Decision Engine`.

Pod nią utwórz:

```text
Decision Cases
Decision Options
Decision Criteria
Option Evaluations
Decision Reviews
Decision Patterns
Decision Lessons & Heuristics
Decision Dashboard
```

## 6.1. Kiedy rejestrować decyzję

Używaj Decision Engine, gdy decyzja jest:

- istotna finansowo, zawodowo, zdrowotnie, relacyjnie lub strategicznie;
- kosztowna do odwrócenia;
- one-way door;
- podejmowana przy dużej niepewności;
- powtarzalna;
- potencjalnie bardzo ucząca;
- związana z kilkoma sensownymi wariantami;
- wymagająca późniejszej retrospektywy.

Nie zapisuj każdej drobnej decyzji.

## 6.2. Decision Cases

Pola:

| Pole | Typ |
|---|---|
| Decision | Title |
| Decision Date | Date |
| Status | Select |
| Owner | Select |
| Decision Type | Select |
| Domains | Multi-select |
| Importance | Select |
| Reversibility | Select |
| Decision Method | Select |
| Context Conditions | Multi-select |
| Question | Text |
| Chosen Decision | Text |
| Rationale | Text |
| Expected Outcome | Text |
| Risks | Text |
| Constraints | Text |
| Assumptions | Text |
| Confidence | Select |
| Review Date | Date |
| Last Reviewed | Date |
| People | Relation → People & Agents |
| Knowledge Nodes | Relation → Knowledge Nodes |
| Source URL | URL |
| Project URL | URL |
| GitHub Issue URL | URL |
| Last Edited | Last edited time |

Status:

```text
Framing
Analyzing
Decided
Executing
Review Due
Reviewed
Superseded
Archived
```

## 6.3. Decision Options

Pola:

| Pole | Typ |
|---|---|
| Option | Title |
| Decision | Relation → Decision Cases |
| Status | Select |
| Description | Text |
| Expected Upside | Text |
| Expected Downside | Text |
| Cost | Text |
| Time to Impact | Text |
| Risks | Text |
| Reversibility | Select |
| Confidence | Select |
| Source URL | URL |
| Last Edited | Last edited time |

Zawsze rozważ status quo, gdy jest realnym wariantem.

## 6.4. Decision Criteria

Pola:

| Pole | Typ |
|---|---|
| Criterion | Title |
| Decision | Relation → Decision Cases |
| Category | Select |
| Weight | Number |
| Direction | Select |
| Threshold | Text |
| Description | Text |
| Source URL | URL |
| Last Edited | Last edited time |

Direction:

```text
Maximize
Minimize
Meet threshold
Boolean
```

## 6.5. Option Evaluations

Pola:

| Pole | Typ |
|---|---|
| Evaluation | Title |
| Decision | Relation → Decision Cases |
| Option | Relation → Decision Options |
| Criterion | Relation → Decision Criteria |
| Score | Number |
| Weight Snapshot | Number |
| Weighted Score | Formula |
| Evidence | Text |
| Confidence | Select |
| Source URL | URL |
| Last Edited | Last edited time |

Skala:

```text
1 = bardzo źle
10 = bardzo dobrze
```

Najpierw zastosuj kierunek kryterium.

Formuła:

```text
Weighted Score = Score × Weight Snapshot
```

Wynik jest wsparciem, nie automatycznym werdyktem.

## 6.6. Decision Reviews

Pola:

| Pole | Typ |
|---|---|
| Review | Title |
| Decision | Relation → Decision Cases |
| Review Date | Date |
| Outcome Status | Select |
| Outcome Rating | Number |
| Expected vs Actual | Text |
| Positive Outcomes | Text |
| Negative Outcomes | Text |
| Unintended Consequences | Text |
| Decision Quality | Select |
| Execution Quality | Select |
| Result Attribution | Select |
| Would Choose Again | Select |
| Lessons | Text |
| Next Actions | Text |
| Sources | Relation → Sources & Evidence |
| GitHub Issue URL | URL |
| Last Edited | Last edited time |

Zawsze oddziel:

- Decision Quality;
- Execution Quality;
- External Factors;
- Outcome Quality.

