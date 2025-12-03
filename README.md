# MayaLint

**Check your 3D models for problems before you submit them.**

MayaLint finds common issues in your Maya models - like flipped normals, overlapping vertices, and missing UVs - so you can fix them before your teacher or client sees them.

---

## Installation (5 minutes)

### Step 1: Download

Click the green button below to download MayaLint:

[![Download ZIP](https://img.shields.io/badge/1-Download%20ZIP-green?style=for-the-badge)](https://github.com/rayiskander2406/mayalint/archive/refs/heads/main.zip)

### Step 2: Unzip

Find the downloaded file (usually in your Downloads folder) and unzip it.

You should see a folder called `modelChecker-main` with a `mayaLint` folder inside.

### Step 3: Find your Maya scripts folder

**Mac:**
1. Open Finder
2. Press `Cmd + Shift + G`
3. Paste this path: `~/Library/Preferences/Autodesk/maya/scripts`
4. Press Enter

**Windows:**
1. Open File Explorer
2. Go to: `Documents > maya > scripts`

### Step 4: Copy the mayaLint folder

> **Important:** Copy the **entire `mayaLint` folder** - not the individual `.py` files inside it. The folder structure matters!

Drag the `mayaLint` folder into your Maya scripts folder.

**Correct** - your scripts folder should look like this:
```
scripts/
  mayaLint/           <-- the folder
    __init__.py
    __version__.py
    mayaLint_UI.py
    mayaLint_commands.py
    mayaLint_list.py
```

**Wrong** - don't copy loose files like this:
```
scripts/
  mayaLint_UI.py      <-- won't work!
  mayaLint_commands.py
  ...
```

### Step 5: Restart Maya

Close Maya completely and reopen it.

---

## Verify Your Installation (Optional)

Want to make sure everything is working? Run our validation script to test all 42 checks.

### How to run the validation:

1. In Maya, go to **Windows > General Editors > Script Editor**
2. Click the **Python** tab
3. Copy the entire contents of [`scripts/validate_installation.py`](scripts/validate_installation.py)
4. Paste it into the Script Editor
5. Press **Ctrl+Enter** (or click Execute All)

### What it does:

- Creates test geometry with deliberate defects (flipped normals, missing UVs, etc.)
- Runs all 42 checks against the test geometry
- Reports PASS/FAIL for each check
- Cleans up after itself

### Expected output:

```
============================================================
VALIDATION SUMMARY
============================================================
Total checks tested: 42
  Passed:  42
  Failed:  0
Duration: ~30 seconds
============================================================
SUCCESS! All 42 checks validated - mayaLint is ready to use!
============================================================
```

If any checks fail, the script will tell you which ones and provide troubleshooting hints.

---

## How to Use

### First time setup (create a button)

1. In Maya, go to **Windows > General Editors > Script Editor**
2. Click the **Python** tab at the bottom
3. Paste this code:

```python
from mayaLint import mayaLint_UI
mayaLint_UI.UI.show_UI()
```

4. Select all the code you just pasted
5. Go to **File > Save Script to Shelf**
6. Name it "MayaLint" and click OK

Now you have a button on your shelf!

### Running checks

1. Click your MayaLint button
2. Select the objects you want to check (or leave empty to check everything)
3. Click **Run All Checks**
4. Fix any red issues that appear

---

## What does it check?

MayaLint checks for 42 different problems. The most important ones are:

| Problem | Why it matters |
|---------|----------------|
| **Flipped Normals** | Makes faces look black in renders |
| **Overlapping Vertices** | Causes weird shading |
| **Missing UVs** | Textures won't work |
| **Non-Manifold Edges** | Breaks 3D printing and game engines |
| **Ngons** | Can cause problems with subdivision |

See [CHECKS.md](CHECKS.md) for the full list.

---

## Troubleshooting

### "No module named mayaLint"

This usually means the folder structure is wrong. Check that:
1. You copied the **`mayaLint` folder itself** (not just the `.py` files inside it)
2. The folder is directly inside `scripts/` (not nested in another folder)
3. You restarted Maya after copying

Go back to Step 4 and check your folder structure matches the "Correct" example.

### The window doesn't open

Try running this in the Script Editor to see the error:
```python
import mayaLint
print(mayaLint.__file__)
```

### Checks are slow

Select fewer objects, or run checks one category at a time.

---

## Credits

MayaLint is based on [modelChecker](https://github.com/JakobJK/modelChecker) by:
- **Jakob Kousholt** - Software Engineer
- **Niels Peter Kaagaard** - Senior Modeler, Weta Digital

This version adds 15 additional checks for students.

---

## License

MIT License - free to use, modify, and share.
