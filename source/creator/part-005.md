| Name | Title |
| Type | Select |
| Custom Type | Text |
| Domains | Multi-select |
| Status | Select |
| Confidence | Select |
| Sensitivity | Select |
| Canonical Summary | Text |
| Sources | Relation → Sources & Evidence |
| Primary Source | URL |
| Origin Area | Select |
| Origin Page | URL |
| Last Verified | Date |
| Review Date | Date |
| Last Edited | Last edited time |

Typy przykładowe:

```text
Fact
Concept
Person
Organization
Project
Product
Place
Event
Preference
Procedure
Decision
Strategy
Observation
Hypothesis
Question
Tool
Metric
Other
```

Statusy:

```text
Draft
Verified
Disputed
Superseded
Archived
```

Confidence:

```text
High
Medium
Low
Unknown
```

Sensitivity:

```text
Normal
Personal
Confidential
```

## 4.3. Knowledge Relations

Pola:

| Pole | Typ |
|---|---|
| Name | Title |
| From | Relation → Knowledge Nodes |
| Relation Type | Select lub Text |
| Custom Relation | Text |
| To | Relation → Knowledge Nodes |
| Evidence | Relation → Sources & Evidence |
| Confidence | Select |
| Status | Select |
| Valid From | Date |
| Valid To | Date |
| Notes | Text |
| Last Edited | Last edited time |

Typy relacji:

```text
is-a
part-of
belongs-to
created-by
works-with
depends-on
supports
contradicts
causes
influences
applies-to
derived-from
mentioned-in
supersedes
related-to
```

## 4.4. Sources & Evidence

Pola:

| Pole | Typ |
|---|---|
| Name | Title |
| Source Type | Select |
| Custom Type | Text |
| Source URL | URL |
| Author or Provider | Text |
| Published | Date |
| Accessed | Date |
| Reliability | Select |
| Evidence Status | Select |
| Notes | Text |
| Last Edited | Last edited time |

Source Type:

```text
Web
Book
Document
Email
Conversation
Notion Page
Drive File
Person
Dataset
Image
Audio
Video
Other
```

Evidence Status:

```text
Primary
Secondary
Unverified
Disputed
Archived
```

## 4.5. Topic Maps

Pola:

| Pole | Typ |
|---|---|
| Name | Title |
| Domain | Select |
| Summary | Text |
| Nodes | Relation → Knowledge Nodes |
| Relations | Relation → Knowledge Relations |
| Status | Select |
| Last Reviewed | Date |
| Next Review | Date |

## 4.6. Review Queue

Pola:

| Pole | Typ |
|---|---|
| Name | Title |
| Node | Relation → Knowledge Nodes |
| Relation | Relation → Knowledge Relations |
| Source | Relation → Sources & Evidence |
| Reason | Multi-select |
| Priority | Select |
| Status | Select |
| Review By | Date |
| Notes | Text |

Reasons:

```text
Unverified
Low Confidence
Missing Source
Contradiction
Possible Duplicate
Stale
Privacy Review
Needs Classification
Retention Review
Other
```

## 4.7. Workspace Index

Pola:

| Pole | Typ |
|---|---|
| Name | Title |
| Area | Select |
| Page Type | Select |
| Page URL | URL |
| Index Status | Select |
| Nodes | Relation → Knowledge Nodes |
| Last Indexed | Date |
| Notes | Text |

Index Status:

```text
Not Indexed
Partial
Complete
Needs Reindex
Excluded
```

## 4.8. Graph Dashboard

Utwórz stronę z:

- ostatnio zmienionymi węzłami;
- aktywnymi relacjami;
- otwartą Review Queue;
- Workspace Index;
- mapami tematycznymi;
- diagramami Mermaid dla wybranych domen.

Nie próbuj stale wyświetlać całego grafu w jednym diagramie. Generuj grafy tematyczne.

## 4.9. Retencja Knowledge

W każdym elemencie Knowledge dodaj pole systemowe `Last Edited`.

Jeśli Notion pozwala, dodaj formułę:

```text
Deletion Eligible After = dateAdd(Last Edited, 1 year)
```

Zasady:

1. nie usuwaj autonomicznie elementu przed upływem pełnego roku od ostatniej edycji;
2. upływ roku oznacza przegląd, nie automatyczne usunięcie;
3. przed terminem można:
   - zarchiwizować;
   - oznaczyć jako Superseded;
   - scalić z zachowaniem źródeł;
   - przekierować;
4. domyślnym działaniem jest archiwizacja;
5. trwałe usunięcie wymaga wyraźnej zgody właściciela;
6. przed usunięciem sprawdź aktywne relacje, unikalne źródła i wartość historyczną.

### Rezultat etapu

Utwórz pierwszy węzeł:

```text
[ASSISTANT_NAME] Workspace
```

oraz relację:

```text
Knowledge system — part-of → [ASSISTANT_NAME] Workspace
```

Zweryfikuj oba rekordy.

---

## Etap 5 z 12 — Relations

W `Relations` utwórz:

```text
People & Agents
Relationship Types
Relationships
Interactions & Notes
Commitments & Follow-ups
Relationship Review Queue
Relationship Dashboard
```

## 5.1. People & Agents

Pola:

| Pole | Typ |
|---|---|
| Name | Title |
| Entity Type | Select |
| Aliases | Text |
| Roles | Multi-select |
| Organizations | Text lub Relation |
| Profile Summary | Text |
| Preferred Communication | Text |
| Status | Select |
| Sensitivity | Select |
| Last Verified | Date |
| Knowledge Node | Relation → Knowledge Nodes |
| Sources | Relation → Sources & Evidence |
| Primary Source | URL |
| Last Edited | Last edited time |

Entity Type:

```text
Human
AI Assistant
Other Agent
```

Nie zapisuj asystenta AI jako człowieka.

## 5.2. Relationship Types

Pola:

| Pole | Typ |
|---|---|
| Name | Title |
| Category | Select |
| Directional | Checkbox |
| Symmetric | Checkbox |
| Inverse Type | Text |
| Definition | Text |
| Status | Select |

Przykłady:

```text
sibling-of
parent-of
child-of
friend-of
colleague-of
manager-of
reports-to
client-of
service-provider-to
mentor-of
mentee-of
partner-of
knows
collaborates-with
assistant-to
assisted-by
```

## 5.3. Relationships

Pola:

| Pole | Typ |
|---|---|
| Name | Title |
| From | Relation → People & Agents |
| Relationship Type | Relation → Relationship Types |
| To | Relation → People & Agents |
| Status | Select |
| Perspective | Select |
| Confidence | Select |
| Sensitivity | Select |
| Summary | Text |
| Context | Text |
| Valid From | Date |
| Valid To | Date |
| Last Verified | Date |
| Sources | Relation → Sources & Evidence |
| Knowledge Relation | Relation → Knowledge Relations |
| Last Edited | Last edited time |

Model musi obsługiwać relacje wiele-do-wielu.

## 5.4. Interactions & Notes

Pola:

| Pole | Typ |
|---|---|
| Name | Title |
| Date | Date/time |
| People | Relation → People & Agents |
