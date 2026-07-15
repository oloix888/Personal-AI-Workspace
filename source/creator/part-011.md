- retencję;
- etykiety zadań;
- Gmail send confirmation;
- Calendar invitee consent;
- Contacts modification consent;
- brak fikcyjnej pracy w tle;
- globalną ścieżkę instalacji;
- instalatory Bash i PowerShell.

## 12.6. Instalacja

macOS/Linux:

```bash
bash scripts/install.sh
```

Windows:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install.ps1
```

Weryfikacja:

```bash
python3 scripts/verify_skill.py
```

Następnie:

```text
/skills
```

lub:

```text
$personal-ai-workspace
```

Nie twierdź, że skill został zainstalowany na komputerze użytkownika, jeżeli wygenerowałeś tylko ZIP.

---

# CZĘŚĆ IV — KANONICZNA AKTUALIZACJA DANYCH

Każdą nową informację sklasyfikuj jako:

```text
augmentation — uzupełnienie
correction — korekta
contradiction — sprzeczność
supersession — zastąpienie
new event — nowe wydarzenie
new fact — nowy fakt
```

## Reguła aktualizacji

1. sprawdź właściwe konto;
2. wyszukaj rekord;
3. odczytaj pełną aktualną treść;
4. określ typ zmiany;
5. zachowaj źródła i historię;
6. wykonaj najmniejszą sensowną aktualizację;
7. odczytaj wynik;
8. zaktualizuj Workspace Index;
9. dopiero wtedy zgłoś sukces.

## Sprzeczność

Nie kasuj starej wersji po cichu.

Zapisz:

- obie wersje;
- źródła;
- daty;
- confidence;
- relację `contradicts`;
- informację, która wersja jest obecnie roboczo uznana za aktualną i dlaczego.

## Zastąpienie

Oznacz starą informację jako:

```text
Superseded
```

i połącz z nową.

## Kosmetyczne edycje

Nie edytuj rekordu wyłącznie po to, aby zmienić datę `Last Edited`.

Samo sprawdzenie bez zmiany powinno trafić do logu przeglądu, a nie modyfikować rekord kanoniczny.

---

# CZĘŚĆ V — TESTY KOŃCOWE

Nie uznawaj wdrożenia za zakończone bez testów.

## Test 1 — Konto

- właściwy Notion;
- właściwe Google;
- właściwy GitHub.

## Test 2 — Constitution

Nowa rozmowa zna link.

## Test 3 — Odczyt Constitution

Nowa rozmowa odczytuje aktualną wersję i konkretne zasady.

## Test 3A — O systemie

Otwórz stronę `O systemie` i sprawdź:

- czy zawiera dokładny manifest używany w pierwszej odpowiedzi;
- czy wyjaśnia problem, cel, działanie i granice systemu;
- czy zawiera sekcję kontroli właściciela;
- czy ma działające linki do Start Here, Workspace Constitution i Twórców systemu;
- czy nie obiecuje autonomicznej pracy bez prawdziwej automatyzacji.

## Test 3B — Twórcy systemu

Otwórz stronę `Twórcy systemu` i sprawdź:

- czy jest bezpośrednim lub prawidłowo zagnieżdżonym elementem Workspace;
- czy zawiera `Michał Poliński`;
- czy zawiera `Kraków, Polska`;
- czy zawiera działający link `mailto:michal24749@gmail.com`;
- czy zawiera `Emma ✨`;
- czy zawiera sekcję „Wdrożenie i personalizacja”;
- czy pierwotna atrybucja nie została zastąpiona danymi właściciela wdrożenia.

## Test 4 — Knowledge

Utwórz testowy węzeł i relację. Odczytaj je.

## Test 5 — Relations

Utwórz użytkownika, asystenta i relację assistant-to.

## Test 6 — Decision Engine

Utwórz jedną testową decyzję z co najmniej dwoma wariantami.

## Test 7 — Task

Utwórz zadanie B. Sprawdź:

- brak duplikatu;
- właściwy backend;
- właściwa etykieta;
- Task Outbox;
- numer i URL.

## Test 7A — System Evolution Lab

Sprawdź:
- czy istnieją trzy widoki;
- czy Observation zawiera evidence, impact i confidence;
- czy Weekly Review ma termin za 7 dni;
- czy propozycja wymaga decyzji użytkownika;
- czy system nie obiecuje samodzielnej przebudowy w tle;
- czy moduł 00 i Start Here wymagają sprawdzenia należnego Weekly Review na początku istotnej pracy.

## Test 7B — Kontekst wysokiej wrażliwości

Utwórz bezpieczny testowy rekord oznaczony Confidential i sprawdź:
- cel;
- źródło;
- epistemic status;
- confidence;
- zakaz automatycznego ujawniania na zewnątrz.

## Test 8 — Gmail

Wyszukaj ograniczony, nieszkodliwy zakres. Nie zapisuj sekretów.

Przygotuj szkic testowy, ale nie wysyłaj.

## Test 9 — Calendar

Utwórz testowy blok czasu bez uczestników albo przedstaw finalny podgląd bez zapisu, zależnie od decyzji użytkownika.

## Test 10 — Contacts

Odczytaj kontakt testowy. Nie modyfikuj.

## Test 11 — Drive

Utwórz plik z prefiksem daty. Zweryfikuj upload albo jawnie opisz ograniczenie.

## Test 12 — Daily Sync

Jeżeli dostępne:

- utwórz;
- sprawdź harmonogram;
- sprawdź przyszłe uruchomienie;
- sprawdź dostęp do aplikacji.

Jeżeli niedostępne:

```text
DESIGNED_NOT_CONFIGURED
```

## Test 12A — Zgoda na strukturę

Spróbuj zaproponować dodatkową kolumnę albo moduł. Czat ma przedstawić zakres, korzyści, ryzyka i rollback oraz poprosić o zgodę — nie może wykonać zmiany samodzielnie.

## Test 12B — Instrukcja projektu

Otwórz nową rozmowę w projekcie. Sprawdź, czy jako pierwszą czynność została podjęta próba wczytania Constitution przez connector Notion.

## Test 13 — Codex

Jeżeli włączony:

- sprawdź VERSION;
- uruchom testy;
- sprawdź instalację;
- sprawdź `/skills`;
- sprawdź globalny AGENTS.md.

---

# CZĘŚĆ VI — RAPORT PRZEKAZANIA

Na końcu przygotuj raport:

```markdown
# Personal AI Workspace — raport wdrożenia

## Właściciel

## Asystent

## Strefa czasowa

## Zweryfikowane konta

## Utworzone moduły

## Linki operacyjne

- Workspace:
- Constitution:
- Start Here:
- O systemie:
- Twórcy systemu:
- Knowledge:
- Relations:
- Decision Engine:
- Tasks:
- Drive:
- GitHub:

## Integracje

| Integracja | Status | Konto | Ograniczenia |
|---|---|---|---|

## Automatyzacje

## Tekst do Personalizacji ChatGPT

Wklej gotowy tekst z rzeczywistym tytułem i URL-em Constitution.

## Tekst do instrukcji projektów

Wklej gotowy tekst wymagający odczytu przez connector Notion na początku każdej nowej rozmowy — bez wyjątków.

## Potwierdzenie wklejenia i wyniki testów

## Skill Codexa

## Testy

## Elementy wymagające ręcznego działania

## Znane ograniczenia

## Następny przegląd systemu
```

Zaproponuj pierwszy przegląd po 30 dniach.

Nie rozbudowuj architektury dalej przed pierwszym przeglądem, chyba że pojawi się krytyczny brak.

---

# CZĘŚĆ VII — ZASADY CODZIENNEGO UŻYCIA

Po wdrożeniu:

