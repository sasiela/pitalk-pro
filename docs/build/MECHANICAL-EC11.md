# EC11 mechanical revision — V39 body / V42 front

Updated: 2026-09-26. Units: mm. This is the latest CAD revision, not a fully validated assembled release.

## Files and compatible parts

- [Body V39 STL](../../stl/ec11-v39-v42/01_Body_V39.stl) / [STEP](../../step/ec11-v39-v42/01_Body_V39.step).
- [Front V42 STL](../../stl/ec11-v39-v42/02_Front_Panel_V42.stl) / [STEP](../../step/ec11-v39-v42/02_Front_Panel_V42.step).
- Reuse [V11 caps](../../stl/03_Button_Cap_V11_Print_4.stl), four prints, and the existing [antenna base](../../stl/06_Antenna_Base.stl) and [70 mm decorative antenna](../../stl/07_Decorative_Antenna_70mm.stl).
- Previous decorative knobs are legacy parts. A matching encoder knob is not included.

## Geometry

The upper body and front extend by 8 mm. PCB supports, display position and existing screw axes stay in place. The upper walls are continuous; the antenna-side bulge reaches the upper edge. The old microSD opening is closed. There is one EC11 position and one antenna position; the middle decorative-knob position is removed.

Encoder reference supplied by the builder: body 12 × 12 × 5, depth including terminals 10, shaft plus threaded section 20. The mounting hole is Ø7.2; verify the actual threaded bush, washer and nut before assembly. The nominal 10 mm envelope reaches 1.7 mm into the PCB footprint, so clearance to real components and wiring must be checked in the complete assembly. Shaft flat, usable shaft length and push travel still need confirmation for the knob.

| Feature | Dimensions |
| --- | --- |
| Rear holes through four existing PCB supports | Ø3.4 |
| Rear countersinks | Ø6.4 at surface, depth 2.2 |
| Rear screw-axis rectangle | 58 × 49 |
| Bottom vents | 40 slots, 8 rows × 5; 6.6 × 2.6, R1 |
| Bottom vent placement | Centered between the four rear screw axes |
| Above-screen vents | 2 rows × 3; 6.6 × 2.6, R1 |
| Above-screen row pitch / material gap | 6 / 3.4 |

## Assembly differences / różnice montażowe

The [illustrated assembly guide](ASSEMBLY.en.md) describes the earlier prototype. For this revision:

1. Trial-fit the encoder and its retaining nut before installing the electronics. Check terminal insulation and clearance to both Pi and display HAT.
2. Insert the microSD before closing the enclosure; there is no external card slot.
3. Rear M3 screws must mate with suitable threaded spacers. Select screw length from the actual assembled stack; the existing M3×12 front screws do not establish the required rear length.
4. Reuse the established front fasteners and V11 caps. Check free button travel after closing.
5. Encoder wiring and software support are not provided by this mechanical change.

Po polsku: montuj V39 z V42. Przymierz enkoder przed elektroniką, sprawdź izolację i kolizje pinów, a kartę microSD włóż przed zamknięciem. Długość tylnych śrub M3 dobierz do rzeczywistych gwintowanych dystansów. Stare pokrętła są ozdobne; nowa gałka i podłączenie EC11 wymagają dopracowania.

## Verification

- Builder confirmed that the 20 mm upper-body test print fitted.
- CAD checks: valid single solids, STEP reimport successful, 40 body vents and six upper-front vents open, no body/front intersection in the checked assembly.
- Full V39/V42 physical assembly, rear fasteners, encoder clearance with soldered wires, and encoder operation remain unverified.
- Check orientation and supports in the slicer; these files do not include a validated print profile.
