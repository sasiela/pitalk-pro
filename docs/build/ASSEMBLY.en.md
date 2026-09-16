# PiTalk Pro assembly

[Polski — illustrated guide](ASSEMBLY.md) · [Photo index](../../photos/README.md)

Follow the prototype author's sequence: **assemble the front first**, then the rear enclosure. Work with power disconnected. Prepare four M3×12 LCD screws, four spacers, two M3 nuts and two M3×12 lower closure screws, two wires approximately 10 cm each, heat-shrink tubing and hot glue. Spacer length still needs a recorded measurement.

## Front panel

1. Place the four printed button caps in their slots from inside the front. Check free movement. [Photo](../../photos/IMG_3595.jpeg)
2. Insert four M3×12 screws through the front, with their threads facing the LCD mounting side.
3. Place the LCD board over the screws, with the display facing the window. Align its buttons with the caps. [Photo](../../photos/IMG_3597.jpeg)
4. Align the LCD and gently tighten the screws. Do not distort the board or jam the buttons. [Photo](../../photos/IMG_3598.jpeg)
5. Screw the four spacers onto the exposed threads behind the LCD. Set the completed front aside. [Photo](../../photos/IMG_3601.jpeg)

## Rear enclosure

1. Solder two wires, approximately 10 cm each, to the two PTT button terminals. Insulate each joint separately with heat-shrink tubing. [Photo](../../photos/IMG_3604.jpeg)
2. Fit the PTT button into its side recess in the rear enclosure, with the wires inside. [Photo](../../photos/IMG_3608.jpeg)
3. Secure the button body with hot glue. Keep glue away from the moving plunger and check that it returns when released. [Photo](../../photos/IMG_3611.jpeg)
4. Identify physical header pins 37 and 39. Gently bend them toward the centre of the Raspberry Pi board, as on the prototype, leaving clearance for the PiTFT connector. Do not bend neighbouring pins. [Photo](../../photos/IMG_3613.jpeg)
5. Solder one PTT wire to physical pin 37 (GPIO26) and the other to pin 39 (GND). The photo uses red for 37 and black for 39. Insulate each joint separately with heat-shrink; check for adjacent-pin shorts. [Close-up](../../photos/IMG_3615.jpeg)
6. Before inserting the Pi, install any optional small USB accessories in the lower sockets of the USB stacks, closest to the PCB: Bluetooth dongle, mouse/keyboard receiver or USB storage. Leave space and a port for the sound adapter.
7. Place the Raspberry Pi in the enclosure and align its ports. Route the PTT wires clear of the board supports and front closure. [Photo](../../photos/IMG_3617.jpeg)
8. Insert the two M3 nuts into the lower nut pockets, aligned with the closure screw holes.
9. Insert the prepared microSD card through the access opening. [Access opening](../../photos/IMG_3618.jpeg)
10. Install the USB sound adapter in its intended free port. Check enclosure and connector clearance. [Adapter before fitting](../../photos/IMG_3619.jpeg)
11. Fit the completed front assembly. Align the PiTFT header correctly with the Pi pins and keep the wires clear; do not offset the connector by a row or pin.
12. Tighten the two lower M3×12 screws into the nuts. Tighten gradually without deforming the print. Check all buttons and ports.

## Pin numbering and checks

37 and 39 are **physical header numbers**, not BCM numbers: 37 is GPIO26 and 39 is GND. See the [Raspberry Pi 3 B Rev 1.2 schematic](https://www.raspberrypi.org/documentation/hardware/raspberrypi/schematics/rpi_SCH_3b_1p2_reduced.pdf). Confirm orientation before soldering. With power disconnected, check that PTT is open when released and closes when pressed.

The photo series does not show every operation. There are no separate photos of inserting optional USB accessories, nuts, fitting the audio adapter or closing the finished enclosure. These steps follow the author's written sequence. The photos remain unmodified.
