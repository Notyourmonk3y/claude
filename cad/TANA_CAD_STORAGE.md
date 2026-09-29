# Build: CAD Storage in Tana Brain

Paste this whole file into Claude Code on the PC that runs Tana Brain (tanabrain.com).

---

Add a **CAD Storage** feature to Tana Brain, and let Tana send CAD files in my personal chat.

## 1. Get the files
- `git clone https://github.com/Notyourmonk3y/claude` (or `git pull` if already cloned).
- Copy `cad/` into the Tana project as `cad-storage/landa-park/`
  (`landa_park_plat.dxf`, `landa_park_plat_preview.png`, `landa_park_plat_report.txt`,
  `landa_park_plat.py`, `landa_park_plat.svg`).
- Copy `.claude/skills/plat-to-cad/` into the Tana project's `.claude/skills/`.

## 2. CAD Storage page
- Add a **CAD Storage** page to Tana Brain's navigation, available on phone and desktop.
- Show one card per job folder in `cad-storage/`: job name, date, preview image, and a
  **Download** button for each file (DXF, DWG, PDF, PNG, TXT).
- Add an **Upload** button that takes plat photos, PDFs, DXF and DWG files and saves them
  into a job folder. Add a **New job** button that makes a folder.
- Serve the files only to me, behind the site's existing login.

## 3. Files in personal chat
- When Tana finishes a CAD job, save the output to `cad-storage/<job>/` and post a chat
  message with the preview image and download links for every file.
- Let me attach plat photos in personal chat. When I send photos with "draw this plat in
  polylines" (or "plat to CAD"), run the `plat-to-cad` skill on them and post the results
  back into the chat.
- Add a **CAD** quick button in the chat. It pre-fills "Draw this plat in polylines and label
  the street names" and opens the photo picker.

## 4. Check it
- Restart Tana and open CAD Storage. Download the Landa Park DXF and open it.
- In personal chat, send one plat photo with "draw this plat in polylines". Confirm the
  files come back in chat and appear in CAD Storage.
- Commit when everything works.
