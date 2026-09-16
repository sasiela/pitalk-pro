# PiTALK PRO

**Projekt terminala radiowego na Raspberry Pi z własną obudową do druku 3D.**

[English](README.md) · [Pliki STL](stl/) · [Film z polskim lektorem](Video/PiTalk-Pro-z-lektorem.mp4)

[![Panel sterowania PiTALK PRO — przejdź do filmu](docs/images/control-panel.jpg)](Video/PiTalk-Pro-z-lektorem.mp4)

## Zbuduj własne urządzenie

To wspólne miejsce dla całego projektu: obudowy, elektroniki, kodu, konfiguracji i wiedzy potrzebnej do budowy. Zacznij od [dokumentacji](docs/README.md), [przewodnika budowy](docs/build/README.md), [listy części](docs/build/HARDWARE.md) i [statusu kompletności](docs/project/READINESS.md).

**Stan: działający prototyp, odtwarzalność w przygotowaniu.** Instalacja od czystego systemu oraz rozruch obrazu alpha na nowej karcie wymagają jeszcze testów. Nie ma jeszcze zweryfikowanego obrazu publicznego wydania. [Jak uzupełniać projekt](CONTRIBUTING.md).

## O projekcie

PiTALK PRO łączy Raspberry Pi 3 Model B, ekran Adafruit PiTFT 2,2″ i kartę dźwiękową USB Sabrent w obudowie inspirowanej klasycznymi radiotelefonami. Obok ekranu znajdują się cztery przyciski. Osobny front, wentylacja, ozdobne pokrętła i antena tworzą kompletny zestaw części do druku.

Repozytorium zawiera **modele STL, materiały prezentacyjne i eksport kodu oprogramowania**. Dokumentacja do dalszej pracy znajduje się w [pakiecie przekazania](docs/handoff/START-HERE.md). Oprogramowanie i narzędzia obrazu są wersją rozwojową, jeszcze nie zatwierdzonym wydaniem firmware.

Projekt był dopasowywany na podstawie kolejnych wydruków. Aktualny zestaw to **korpus V32, płaski front V38 i nakładki V11**. Ostateczne pasowanie zależy od konkretnej elektroniki i dokładności drukarki.

## Części do druku

| Część | Plik | Liczba sztuk |
| --- | --- | ---: |
| Korpus V32 | [Body](stl/01_Body_V32.stl) | 1 |
| Płaski front V38 | [Flat front](stl/02_Flat_Front_Panel_V38.stl) | 1 |
| Nakładka przycisku V11 | [Button cap](stl/03_Button_Cap_V11_Print_4.stl) | **4** |
| Pokrętło 1 | [Knob 1](stl/04_Control_Knob_1.stl) | 1 |
| Pokrętło 2 | [Knob 2](stl/05_Control_Knob_2.stl) | 1 |
| Podstawa anteny | [Antenna base](stl/06_Antenna_Base.stl) | 1 |
| Antena ozdobna 70 mm | [Antenna](stl/07_Decorative_Antenna_70mm.stl) | 1 |

**7 plików, 10 drukowanych części.** Jednostki: milimetry. Cały zestaw można pobrać przez **Code → Download ZIP**.

## Elektronika i mocowania

- Raspberry Pi **3 Model B**.
- Adafruit **PiTFT 2,2″ 240 × 320 HAT**, z czterema przyciskami.
- Karta audio USB Sabrent zgodna z prototypem, obudowa około **34 × 23 × 10 mm**.
- Przycisk chwilowy typu PBS-110 o wymiarach zgodnych z prototypem.
- Na dole: **2 śruby stożkowe M3×12** i **2 nakrętki M3 o wymiarach 5 mm między płaskimi bokami × 2 mm grubości**.
- Cztery śruby stożkowe M3×12 do LCD i cztery dystanse; długość dystansów wymaga uzupełnienia pomiarem.
- Zewnętrzne zasilanie Raspberry Pi; projekt nie przewiduje wewnętrznego akumulatora.

Przed zakupem zamienników sprawdź wymiary. Pokrętła i antena są **ozdobne**. Mocowania enkoderów EC11 i zewnętrzny układ PTT nie są częścią aktualnego zestawu.

## Druk i montaż

Projekt rozwijano na Creality K1, korzystając z PLA i CR-PETG. Repozytorium nie zawiera gotowego profilu drukarki ani G-code.

Przed montażem oczyść wydruki i sprawdź pasowanie nakładek. Korpus drukuj dnem na stole; orientację frontu i podpory sprawdź w slicerze.

**[Pełna instrukcja montażu ze zdjęciami](docs/build/ASSEMBLY.md)** — zaczynamy od frontu:

1. Włóż cztery nakładki przycisków w sloty frontu.
2. Umieść cztery śruby M3×12, przyłóż LCD i przykręć śruby.
3. Przykręć cztery dystanse; odłóż gotowy front.
4. Przylutuj do PTT dwa przewody po 10 cm i zaizoluj luty koszulkami termokurczliwymi.
5. Zamontuj PTT w tylnej części obudowy i zabezpiecz go gorącym klejem.
6. Odegnij do środka fizyczne piny 37 i 39 Raspberry Pi. Przylutuj przewody PTT i osłoń połączenia koszulkami, zgodnie z pełną instrukcją.
7. Włóż opcjonalne dongle do dolnych portów USB, zanim umieścisz Pi w obudowie.
8. Włóż Raspberry Pi, następnie dwie nakrętki M3 i kartę microSD.
9. Zainstaluj kartę dźwiękową USB.
10. Załóż gotowy front i dokręć dwie dolne śruby M3×12.

Dno ma **40 szczelin 6,6 × 2,6 mm, R1**, w ośmiu rzędach po pięć. Korpus V32 ma wzmocnione mocowania nakrętek połączone ze ściankami. Nakładki V11 mają wysokość 3,5 mm i zaokrąglenie góry R0,6.

## Uwagi i zgłoszenia

W [zgłoszeniu na GitHub](https://github.com/sasiela/pitalk-pro/issues) podaj wersję części, drukarkę, materiał, wysokość warstwy oraz zdjęcie lub pomiar problemu.

## Kod i dokumentacja projektu

Dodano aktualny eksport kodu i dokumentację do dalszej pracy w Cursorze: [Zacznij tutaj](docs/handoff/START-HERE.md), [oprogramowanie](software/README.md). To snapshot i eksperymentalne narzędzia obrazu, nie zatwierdzone wydanie firmware.
