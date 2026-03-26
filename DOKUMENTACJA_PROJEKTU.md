# Dokumentacja Projektu: Generator Ofert Piłkochwytów — Siatki Kramer

> **Kontekst:** Firma Siatki Kramer (sklep.siatki-kramer.pl) sprzedaje kompletne konstrukcje piłkochwytów.
> Celem projektu jest zbudowanie interaktywnego generatora wycen/ofert jako podstrony istniejącego serwisu.

---

## 1. Cel i zakres projektu

Generator ofert ma umożliwić klientowi samodzielne skonfigurowanie piłkochwytu, obliczenie kosztu wszystkich materiałów i wygenerowanie profesjonalnej oferty PDF, którą:
- **może zachować lokalnie**,
- **otrzymuje automatycznie na podany e-mail**,
- **może z niej zamówić materiały klikając link** (przycisk w mailu).

Generator **nie** obejmuje montażu — wyłącznie materiały + transport.

---

## 2. Umiejscowienie aplikacji

| Element | Lokalizacja |
|---|---|
| Generator ofert | Osobna podstrona w menu głównym serwisu siatki-kramer.pl |
| Frontend | Podstrona istniejącego serwisu (WordPress lub osobna SPA) |
| Backend (logika kalkulatora + wysyłka maila + generowanie PDF) | Do ustalenia — zalecane: Node.js / PHP lub serverless (np. Vercel Functions, AWS Lambda) |
| Baza danych (numery ofert, historia) | Do ustalenia — zalecane: prosta baza (MySQL / PostgreSQL / Supabase) |

---

## 3. Funkcjonalności aplikacji (pełna lista)

### 3.1 Konfiguracja piłkochwytu (KROK 1 — wybór kształtu i wymiarów)

Klient wybiera **kształt układu piłkochwytu** widoczny wizualnie (rzut z góry):

| Kształt | Liczba zastrzałów | Opis |
|---|---|---|
| **Linia prosta** | 2 | Jedna ściana |
| **L** | 4 | Dwie ściany pod kątem |
| **U** | 6 | Trzy ściany (np. za jedną bramką) |
| **Zamknięty** | 8 | Cztery ściany (cały teren) |

> UI: przyciski/ikonki z wizualnym podglądem kształtu — klient musi łatwo rozumieć wybór.

Klient podaje dla każdej ściany:
- **Długość ściany** [m]
- **Wysokość** — do wyboru: **4 m / 5 m / 6 m** (wysokość słupów po zamontowaniu, ponad teren)

---

### 3.2 Opcja montażu słupów (KROK 2)

| Opcja | Opis | Koszt dodatkowy |
|---|---|---|
| **Montaż na stałe w betonie** | Rekomendowane, bez dodatkowych elementów | 0 zł |
| **Tuleje montażowe** | Słupy wkładane w tuleje — łatwiejszy demontaż | 233 zł brutto / szt. |

> Informacja wyświetlana klientowi — rekomendacja montażu na stałe.
> Nie uwzględniamy kosztu betonu ani samego montażu.

---

### 3.3 Automatyczne obliczanie słupów i zastrzałów

**Zasady rozmieszczenia słupów:**
- Odległość między 1. i 2. słupem oraz między ostatnim a przedostatnim: **3 m**
- Odległość między pozostałymi (pośrednimi) słupami: **max. 5,5 m**
- Aplikacja automatycznie oblicza potrzebną liczbę słupów na podstawie długości ściany

**Zastrzały:**
- Montowane przy 1. i 2. słupie oraz przy ostatnim i przedostatnim (po 1 zastrzale na parę skrajnych słupów)
- Liczba zastrzałów = 2 × liczba wolnych końców ścian (wg tabeli kształtów powyżej)
- **Długość odcinka:** dla każdej ściany prostej osobno, jeśli długość przekracza **30 m**, dolicza się **+2 zastrzały** na każde rozpoczęte **30 m** powyżej pierwszych 30 m (np. 31 m → +2, 61 m → +4 względem długości tej ściany; suma liczy się z bazy kształtu i dodatków ze wszystkich ścian)

**Ceny słupów (brutto):**
| Wysokość | Cena brutto |
|---|---|
| 4 m | 526 zł |
| 5 m | 631 zł |
| 6 m | wg aktualnego cennika |

**Ceny zastrzałów (brutto):**
| Wysokość | Cena brutto |
|---|---|
| 6 m | ~390 zł netto (~480 zł brutto) |

> Zastrzały mają tę samą wysokość co słupy — należy pobierać odpowiednią cenę.

---

### 3.4 Wybór siatki (KROK 3)

Klient wybiera siatkę z listy produktów ze sklepu (tak jak na stronie):
https://sklep.siatki-kramer.pl/siatki-na-pilkochwyty/

Aplikacja pobiera/przechowuje listę dostępnych siatek z parametrami:
- Nazwa / typ siatki
- Cena za mkw. (netto/brutto)

**Obliczenie ilości siatki:**
```
Powierzchnia siatki [mkw.] = Suma (długość każdej ściany × wysokość ściany)
```

**Przykład z kalkulatora:**
Siatka polipropylenowa PP, oczko 10×10 cm, śr. sznurka 3 mm → **10 zł/mkw. netto**

---

### 3.5 Automatyczne obliczanie akcesoriów

Na podstawie liczby słupów i wymiarów aplikacja automatycznie wylicza:

| Akcesorium | Zasada obliczania | Cena jednostkowa (netto) |
|---|---|---|
| **Linka stalowa 3 mm** | Długość = obwód całego układu (suma długości ścian) | 2 zł/mb |
| **Śruby oczkowe cynkowane** | 2 szt. × liczba słupów | 3,50–5 zł/szt. brutto |
| **Karabińczyki cynkowane** | wg powierzchni siatki (przelicznik z kalkulatora) | 0,50 zł/szt. netto |
| **Śruby rzymskie + zaciski (zestaw)** | 2 zestawy (na całą konstrukcję) | 50 zł/zestaw netto |
| **Tuleje montażowe** (jeśli wybrano) | 1 szt. × liczba słupów | 190–233 zł/szt. |
| **Transport** | Stała kwota (lub wg lokalizacji) | ~1400 zł netto |

> Przelicznik karabińczyków z przykładu: dla 144 mkw. siatki użyto 281.6 szt. → ~1.95 szt./mkw.

---

### 3.6 Dwa typy wyceny (KROK 4 — wybór przez klienta)

Klient wybiera co ma zawierać wycena:

| Opcja | Zawartość |
|---|---|
| **1. Tylko siatka + akcesoria + dostawa** | Siatka, linka, śruby, karabińczyki, transport — bez słupów i zastrzałów. Często potrzebne do złożenia wniosku w Gminie. |
| **2. Kompletna wycena** | Słupy + zastrzały + siatka + akcesoria + transport |

---

### 3.7 Dane klienta i generowanie oferty (KROK 5)

Formularz danych klienta:
- Imię i nazwisko / Nazwa firmy
- Adres e-mail
- Numer telefonu (opcjonalnie)
- Adres / miejscowość (opcjonalnie — wpływa na transport)

Po zatwierdzeniu:
1. System generuje **unikalny numer oferty** (np. `KR-2024-00123`)
2. Generowany jest **plik PDF** z wyszczególnieniem:
   - Danych klienta i firmy (Siatki Kramer)
   - Numeru oferty i daty
   - Tabeli elementów: nazwa, ilość, cena jedn., wartość netto
   - Podsumowania: razem netto, VAT 23%, razem brutto
   - **Przycisku / linku do zamówienia**
   - **Disclaimeru:** _"Wycena jest orientacyjna i nie stanowi oferty w rozumieniu przepisów prawa"_
3. PDF jest **wysyłany na e-mail klienta**
4. PDF jest **dostępny do pobrania bezpośrednio w przeglądarce**

---

## 4. Struktura kalkulacji (format tabeli oferty)

Na podstawie pliku Excel — przykładowa kalkulacja gotowego piłkochwytu:

| Nazwa towaru | Wys. [m] | Dł./Ilość | Suma [mkw.] | Cena jedn. (netto) | Wartość netto |
|---|---|---|---|---|---|
| Siatka polipropylenowa PP, oczko 10×10 cm, śr. 3 mm | 4 | 18 mb × 2 | 144 mkw. | 10,00 zł | 1 440,00 zł |
| Słup stalowy 80×80/3mm, cynk+lakier RAL 6005 | 5 | 12 szt. | — | 580,00 zł | 6 960,00 zł |
| Zastrzał stalowy 60×40/2mm, cynk+lakier RAL 6005 | 6 | 4 szt. | — | 390,00 zł | 1 560,00 zł |
| Tuleje montażowe cynkowane | — | 12 szt. | — | 190,00 zł | 2 280,00 zł |
| Linka stalowa 3 mm | — | 88 mb | — | 2,00 zł | 176,00 zł |
| Śruby rzymskie + zaciski cynkowane (zestaw) | — | 2 szt. | — | 50,00 zł | 100,00 zł |
| Karabińczyki cynkowane | — | 281,6 szt. | — | 0,50 zł | 140,80 zł |
| Śruby oczkowe cynkowane | — | 24 szt. | — | 3,50 zł | 84,00 zł |
| Transport | — | — | — | — | 1 400,00 zł |
| **Razem netto** | | | | | **14 140,80 zł** |
| **Razem brutto (VAT 23%)** | | | | | **17 393,18 zł** |

> Uwaga z arkusza: **odstęp między słupami nie może być większy niż 5,5 m**

---

## 5. Mapa projektu (roadmap)

### Etap 1 — Projekt i architektura
- [ ] Wybór technologii frontend (React/Vue/Next.js lub prosty HTML+JS)
- [ ] Wybór technologii backend (Node.js/PHP/Python + framework)
- [ ] Wybór hostingu (Vercel, VPS, hosting współdzielony przy WordPress)
- [ ] Wybór bazy danych (numery ofert, historia)
- [ ] Projekt UI/UX — formularz krokowy (wizard), wizualne wybory kształtów

### Etap 2 — Frontend (kalkulator)
- [ ] Krok 1: Wybór kształtu (wizualne ikonki) + podanie długości i wysokości każdej ściany
- [ ] Krok 2: Wybór opcji montażu (beton / tuleje)
- [ ] Krok 3: Wybór siatki z listy
- [ ] Krok 4: Wybór zakresu wyceny (siatka+akcesoria / kompletna)
- [ ] Krok 5: Formularz danych klienta
- [ ] Podgląd kalkulacji na żywo (live preview tabeli z sumami)
- [ ] Przycisk "Generuj ofertę"

### Etap 3 — Backend (logika + generowanie PDF)
- [ ] Endpoint API przyjmujący dane z formularza
- [ ] Silnik kalkulacyjny (obliczenia ilości słupów, akcesoriów, sum)
- [ ] Generowanie PDF (biblioteka: PDFKit, wkhtmltopdf, Puppeteer, FPDF)
- [ ] Nadawanie numerów ofert (sekwencyjne, zapis do bazy)
- [ ] Wysyłka e-mail z PDF (SMTP / SendGrid / Resend)
- [ ] Link do zamówienia w e-mailu

### Etap 4 — Integracja i testy
- [ ] Testy kalkulatora (graniczne przypadki: minimalna/maksymalna liczba słupów)
- [ ] Testy generowania PDF
- [ ] Testy wysyłki e-mail
- [ ] Testy na urządzeniach mobilnych

### Etap 5 — Wdrożenie
- [ ] Osadzenie na stronie siatki-kramer.pl
- [ ] Konfiguracja domeny / subdomeny
- [ ] Ustawienie SMTP / konta e-mail nadawcy
- [ ] Monitoring błędów

---

## 6. Ważne reguły biznesowe (dla silnika kalkulacyjnego)

1. **Minimalna liczba słupów na ścianę:** obliczana z długości i zasad odstępów
2. **Odstęp skrajny:** zawsze 3 m (1.↔2. i przedostatni↔ostatni słup)
3. **Odstęp pośredni:** max 5,5 m — algorytm musi równomiernie rozłożyć słupy
4. **Zastrzały:** zawsze 2 na wolny koniec prostej ściany
5. **Śruby oczkowe:** 2 szt. × liczba słupów
6. **VAT:** 23%
7. **Disclaimer prawny** musi pojawić się w każdej wygenerowanej ofercie
8. **Oferta nie uwzględnia montażu** — tylko materiały i transport

---

## 7. Inspiracje i referencje

- Sklep Siatki Kramer: https://sklep.siatki-kramer.pl/siatki-na-pilkochwyty/
- Przykładowy słup 6m: https://sklep.siatki-kramer.pl/product/slup-stalowy-pilkochwytu-wysokosci-6-m-80x80x3-mm-ocynkowany-malowany-proszkowo/
- Przykładowy zastrzał: https://sklep.siatki-kramer.pl/product/zastrzal-stalowy-pilkochwytu-wysokosci-6-m-60x40x2-mm-ocynkowany-malowany-proszkowo/
- Wzór oferty e-mail: plik "przykładowa oferta Bagan" (wspomniany w briefie, do dostarczenia)

---

## 8. Osadzenie w iframe (WordPress / Vercel)

Generator może być wyświetlany w `<iframe>` na stronie WordPress. Aby **wysokość iframe dopasowywała się do treści** (bez podwójnego scrolla), strona rodzica i aplikacja w iframe muszą używać **tej samej wersji** biblioteki [iframe-resizer](https://www.npmjs.com/package/iframe-resizer):

| Strona | Skrypt / pakiet |
|--------|-------------------|
| WordPress (rodzic) | `iframeResizer.js` (np. z CDN w tej samej wersji co poniżej) |
| Ta aplikacja (Vite/React) | npm: `iframe-resizer` **^4.3.9** — skrypt child ładowany w `main.jsx` |

**Konfiguracja rodzica:** przy inicjalizacji `iFrameResize` ustaw `checkOrigin` tak, aby zawierał dokładny origin frontendu (np. produkcyjny URL na Vercelu). Dzięki temu `postMessage` z wysokością będzie akceptowany tylko z zaufanego źródła.

**CSP / nagłówki:** w `frontend/vercel.json` ustawiono `Content-Security-Policy: frame-ancestors *`, aby strona mogła być osadzana w iframe. W produkcji możesz zawęzić `frame-ancestors` do domeny WordPressa (np. `https://siatki-kramer.pl`), jeśli nie potrzebujesz osadzać aplikacji z innych hostów.

Po wdrożeniu weryfikuj działanie na urządzeniach mobilnych (kroki 1–4, obrót ekranu).

---

## 9. Otwarte pytania / do ustalenia

- [ ] Hostowanie: czy generator jest częścią WordPressa czy osobną aplikacją?
- [ ] Skąd pobierana jest aktualna lista siatek i ich ceny? (API sklepu, ręczna lista, CMS?)
- [ ] Czy koszty transportu są stałe czy zależą od lokalizacji klienta?
- [ ] Cena zastrzałów dla wysokości 4m i 5m (w pliku tylko 6m)
- [ ] Wzór PDF oferty do zaprojektowania — dostarczyć przykład od Bagan
- [ ] Konto e-mail nadawcy i konfiguracja SMTP
- [ ] Czy historia ofert ma być dostępna w panelu admina?

---

*Dokumentacja wygenerowana na podstawie plików: "Gotowy piłkochwyt kalkulator.xlsx" oraz "Gotowy piłkochwyt - generator ofert.docx"*
*Data: 2026-03-25*
