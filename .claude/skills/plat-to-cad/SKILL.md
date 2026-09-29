---
name: plat-to-cad
description: Turn photos or scans of a recorded plat / subdivision map into a CAD drawing with closed polylines per lot, street lines and labeled street names (DXF that opens in AutoCAD). Use when the user says "draw this plat", "plat to CAD", "poly lines", "dwg" or sends plat photos.
---

# Plat to CAD

The user sends plat photos and says something short like "draw this plat up in polylines".
Do the whole job without asking unless a number is truly unreadable.

1. **Read the plat.** List every bearing, lot frontage, lot depth, lot line length, block and
   lot number, street name, and the scale. Mark any value you can't read as "?".
2. **Solve the geometry before drawing.** Pick an origin (a street intersection or plat corner).
   Use bearings for street lines. Lots with the same depth along one street are rectangles
   perpendicular to it (for example N 26-59 W vs S 63-01 W). Check that plat lengths agree:
   parallel lot lines between two streets grow by a constant amount per 100'. When a
   handwritten number doesn't fit, try the similar-looking digit (3↔2, 8↔6) that makes it close.
   If a street width isn't shown, scale it from the plat.
3. **Write a Python script** that follows `cad/26-0234_landa-park-highlands/landa_park_plat.py`. It must produce:
   - a `.dxf`: one closed polyline per lot on `LOTS`, street lines on `STREETS`, street names
     on `STREET-NAME`, lot numbers on `LOT-NUM`, plat dimensions on `DIM`, block labels on `BLOCK`
   - an `.svg` preview
   - a report with the area of every lot, computed vs. plat lengths, and every assumption
4. **Run it and look at the preview** before you call it done. Fix lots that overlap or
   leave gaps.
5. **Deliver:** send the DXF, preview and report. Put the files in the project `cad/`
   folder, one subfolder per job. Keep it short: say what was drawn and list only the
   assumptions the user should check.

Tell the user that AutoCAD opens the `.dxf` directly and can SAVEAS `.dwg`.
