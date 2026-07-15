Przez connector Notion wczytaj modularny indeks Workspace Constitution, Start Here, moduł 00 oraz moduły 01, 05, 07 i 10. Następnie podaj:

1. wersję Constitution,
2. oczekiwane konto Notion,
3. aktualny status Daily Context Sync,
4. zasady zadań i priorytetów,
5. regułę zapraszania innych osób do Calendar.

Dla każdego dokumentu powiedz, czy odczyt był pełny. Jeżeli nie możesz go otworzyć albo treść jest obcięta, powiedz to wprost.
```

Test jest zaliczony tylko wtedy, gdy czat naprawdę odczyta aktualną treść przez connector Notion.

## 10.6. Test projektu

W projekcie zawierającym nową instrukcję otwórz zupełnie nową rozmowę i napisz:

```text
Zanim odpowiesz merytorycznie, opisz jakie dokumenty wczytałeś przez connector Notion na początku tej rozmowy.
```

Oczekiwany rezultat:

- Constitution;
- Start Here;
- moduł 00;
- moduły właściwe dla tematu;
- jawny status pełności odczytu.

Zapisz pozytywne wyniki testów jako źródła w `Sources & Evidence`.

---

## Etap 11 z 12 — Daily Context Sync

Najpierw sprawdź, czy konto ma dostęp do ChatGPT Scheduled Tasks lub innej realnej automatyzacji.

Nie twórz wydarzenia kalendarzowego jako imitacji automatyzacji.

## 11.1. Docelowy harmonogram

```text
Codziennie o 05:00
Strefa: [TIMEZONE]
```

## 11.2. Prompt zadania

```text
Nazwa: Daily Context Sync

Wykonaj codzienną synchronizację Personal AI Workspace.

1. Zweryfikuj właściwe konta.
2. Odczytaj modularny indeks Workspace Constitution, Start Here, moduł 00 i moduł 10.
3. Odczytaj rekord ostatniego udanego Sync Run.
4. Zbierz cały dostępny nowy kontekst od ostatniej synchronizacji:
   - rozmowy i pamięć dostępne w bieżącym zakresie,
   - Gmail Inbox i Sent,
   - projekty,
   - Notion,
   - Calendar,
   - GitHub,
   - Drive i inne zatwierdzone źródła.
5. Nie twierdź, że sprawdzono wszystkie źródła, jeżeli dostęp był częściowy.
6. Klasyfikuj informacje jako:
   - augmentation,
   - correction,
   - contradiction,
   - supersession,
   - new event,
   - new fact.
7. Przed aktualizacją wyszukaj i odczytaj rekord kanoniczny.
8. Aktualizuj Knowledge, Relations, Projects, Decisions, Strategies, Observations,
   Commitments i Tasks.
9. Z Gmail promuj tylko trwały kontekst. Nie zapisuj sekretów.
10. Nigdy nie wysyłaj automatycznie maili.
11. Utwórz szkic odpowiedzi lub zadanie, gdy jest potrzebne działanie.
12. Nie wykonuj kosmetycznych edycji resetujących retencję.
13. Przestrzegaj retencji Knowledge i zakazu automatycznego usuwania Relations.
14. Zapisz Sync Run:
    - początek i koniec,
    - zakres,
    - źródła dostępne,
    - źródła niedostępne,
    - utworzone i zmienione rekordy,
    - zadania,
    - błędy,
    - poziom kompletności,
    - punkt startowy następnego przebiegu.
15. Zgłoś użytkownikowi tylko istotne zmiany, ryzyka, zadania A i decyzje wymagające potwierdzenia.
```

## 11.3. Sync Runs

Utwórz bazę:

| Pole | Typ |
|---|---|
| Run | Title |
| Started | Date/time |
| Finished | Date/time |
| Since | Date/time |
| Until | Date/time |
| Status | Select |
| Sources Checked | Multi-select |
| Sources Unavailable | Multi-select |
| Created Records | Number |
| Updated Records | Number |
| Created Tasks | Number |
| Errors | Text |
| Coverage | Select |
| Next Cursor | Text |
| Summary | Text |

## 11.4. Ważne ograniczenia

- Automatyzacja może mieć inne możliwości niż zwykły czat.
- Dostęp do aplikacji zależy od konta i uprawnień.
- Zadanie utworzone w projekcie może nie mieć dostępu do plików projektu.
- Scheduled Task nie może być traktowane jako gwarantowany proces serwerowy bez kontroli.
- Gdy automatyzacja nie jest dostępna, wpisz:
  ```text
  DESIGNED_NOT_CONFIGURED
  ```

---

## Etap 12 z 12 — Globalny skill Codexa — moduł opcjonalny

Wykonaj ten etap tylko, jeżeli użytkownik korzysta z Codexa.

## 12.1. Struktura skilla

```text
personal-ai-workspace/
├── SKILL.md
├── VERSION
├── CHANGELOG.md
├── README.md
├── INSTALL.md
├── WORKING_INSTRUCTIONS.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── workspace-manifest.md
│   ├── knowledge-system.md
│   ├── relations-system.md
│   ├── decision-engine.md
│   ├── task-system.md
│   ├── gmail-context.md
│   └── calendar-contacts-candor.md
├── scripts/
│   ├── install.sh
│   ├── install.ps1
│   └── verify_skill.py
└── tests/
    ├── test_skill_contract.py
    ├── pressure-scenarios.md
    └── TEST_RESULTS.md
```

## 12.2. Minimalny SKILL.md

```markdown
---
name: personal-ai-workspace
description: Use when work creates durable knowledge, files, tasks, decisions, relationship context, Gmail context, Calendar events, Contacts lookups, or Workspace updates for the owner.
---

# Personal AI Workspace

Before significant work:

1. Verify connected account identities.
2. Read the current Workspace Constitution and Start Here.
3. Use canonical Notion records.
4. Search before creating duplicates.
5. Fetch current pages before updating.
6. Verify every write by readback.
7. Follow consent rules for email, attendees, contacts, and high-risk tasks.
8. Do not store hidden chain-of-thought, credentials, or unnecessary sensitive data.
9. Do not claim background execution without a real automation.
```

## 12.3. Lokalizacja globalna

Skill użytkownika powinien zostać zapisany w:

```text
$HOME/.agents/skills/personal-ai-workspace
```

Ma wtedy zastosowanie do repozytoriów użytkownika.

## 12.4. Globalny AGENTS.md

Utwórz:

```text
~/.codex/AGENTS.md
```

Przykład:

```markdown
# Global working agreements

Before significant work involving my projects, decisions, tasks, relationships, files, or personal context:

1. Load and follow the `personal-ai-workspace` skill.
2. Verify the connected accounts.
3. Read the Workspace Constitution from Notion.
4. Do not claim a write succeeded without readback.
5. Follow explicit-consent rules for sending email, external Calendar invitees, and contact modifications.
```

## 12.5. Testy

Skill powinien testować:

- wymagane pliki;
- prawidłowy frontmatter;
- konta i identyfikatory;
- reguły prywatności;
