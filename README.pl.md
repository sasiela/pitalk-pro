# PiTALK PRO

**Projekt terminala radiowego na Raspberry Pi z własną obudową do druku 3D.**

[English](README.md) · [Pliki STL](stl/) · [Film z polskim lektorem](Video/PiTalk-Pro-z-lektorem.mp4)

[![Panel sterowania PiTALK PRO — przejdź do filmu](docs/images/control-panel.jpg)](Video/PiTalk-Pro-z-lektorem.mp4)

## O projekcie

PiTALK PRO łączy Raspberry Pi 3 Model B, ekran Adafruit PiTFT 2,2″ i kartę dźwiękową USB Sabrent w obudowie inspirowanej klasycznymi radiotelefonami. Obok ekranu znajdują się cztery przyciski. Osobny front, wentylacja, ozdobne pokrętła i antena tworzą kompletny zestaw części do druku.

Repozytorium zawiera obecnie **modele STL i film prezentacyjny**. Kod aplikacji, firmware i instrukcja instalacji oprogramowania nie są częścią tego wydania.

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
- Cztery śruby stożkowe M3 mocujące część ekranową; długość należy dobrać do rzeczywistych dystansów ekranu.
- Zewnętrzne zasilanie Raspberry Pi; projekt nie przewiduje wewnętrznego akumulatora.

Przed zakupem zamienników sprawdź wymiary. Pokrętła i antena są **ozdobne**. Mocowania enkoderów EC11 i zewnętrzny układ PTT nie są częścią aktualnego zestawu.

## Druk i montaż

Projekt rozwijano na Creality K1, korzystając z PLA i CR-PETG. Repozytorium nie zawiera gotowego profilu drukarki ani G-code.

1. Sprawdź orientację i podpory w slicerze. Korpus drukuj dnem na stole. STL frontu V38 jest ustawiony płaską stroną przednią na stole — sprawdź podgląd pierwszej warstwy oraz fakturę płyty.
2. Zwróć uwagę na podpory pod dachami kieszeni nakrętek, kołnierzami przycisków i ozdobnymi częściami. Najpierw wydrukuj jedną nakładkę i sprawdź jej ruch.
3. Oczyść części i wykonaj przymiarkę bez kleju. Wsuń nakrętki przed elektroniką. Kieszenie mają 5,5 × 2,6 mm; ewentualny klej nie może dostać się do gwintu.
4. Zamontuj boczny przycisk, Raspberry Pi, ekran z dystansami oraz kartę audio. Poprowadź przewody poza otworami i mocowaniami.
5. Włóż cztery nakładki od środka frontu. Muszą poruszać się swobodnie i nie naciskać stale przycisków ekranu.
6. Przyłóż front i delikatnie skręć obudowę. Dolne śruby to M3×12. Nie dociągaj na siłę i sprawdź, czy pozostałe śruby nie dochodzą do dna dystansów.
7. Dopasuj i przyklej ozdobne pokrętła oraz antenę. Przed uruchomieniem sprawdź przewody, dostęp do złączy i działanie przycisków.

Dno ma **40 szczelin 6,6 × 2,6 mm, R1**, w ośmiu rzędach po pięć. Korpus V32 ma wzmocnione mocowania nakrętek połączone ze ściankami. Nakładki V11 mają wysokość 3,5 mm i zaokrąglenie góry R0,6.

## Uwagi i zgłoszenia

W [zgłoszeniu na GitHub](https://github.com/sasiela/pitalk-pro/issues) podaj wersję części, drukarkę, materiał, wysokość warstwy oraz zdjęcie lub pomiar problemu.
