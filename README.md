# Rec Center Room Setups

To-scale floor plans for every table and chair setup in the meeting rooms at the UToledo Student Recreation Center: Maple, Willow, and Oak (Full Oak, Oak, the Double Meeting Room, Hickory and Sycamore).

- [Room Setups page](index.html)
- [Printable setup checklist](checklist.html) (4 letter pages, in setup order, with boxes to check off)

## What's in here

| File | What it is |
|---|---|
| `index.html` | The Room Setups page |
| `checklist.html` | The printable checklist |
| `scripts/` | The Python scripts that draw the floor plans and build both pages |

## Changing a setup

Every floor plan is drawn by the scripts in `scripts/`:

- `gen.py` draws the standard setups (Banquet, Lecture, Classroom and the rest).
- `gen_ideas.py` draws the newer setups (Center Floor, Long Table Dinner, Workshop Stations).
- `assemble.py` puts the plans into the page.
- `checklist.py` makes the checklist from the counts on the page.

After a change, rebuild both pages with Python 3 (nothing else to install):

    python3 scripts/build_site.py

Then upload the new `index.html` and `checklist.html` here.

## Notes

- Plans are drawn to scale from the Facilities floor plans. Rectangle tables are 6 ft by 30 in, and round tables are 5 ft across.
- Table and chair counts are based on the Event Space Capacities sheet.
- The fonts (Archivo and Public Sans) are under the SIL Open Font License. Their license files are in `scripts/`.
