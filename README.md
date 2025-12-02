# MayaLint

**Check your 3D models for problems before you submit them.**

MayaLint finds common issues in your Maya models - like flipped normals, overlapping vertices, and missing UVs - so you can fix them before your teacher or client sees them.

---

## Installation (5 minutes)

### Step 1: Download

Click the green **Code** button above, then click **Download ZIP**.

![Download ZIP](https://img.shields.io/badge/1-Download%20ZIP-green?style=for-the-badge)

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

Copy the `mayaLint` folder (the one with the Python files inside) into your Maya scripts folder.

Your scripts folder should now look like this:
```
scripts/
  mayaLint/
    mayaLint_UI.py
    mayaLint_commands.py
    mayaLint_list.py
    __init__.py
    __version__.py
```

### Step 5: Restart Maya

Close Maya completely and reopen it.

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

The mayaLint folder is in the wrong place. Make sure:
- It's directly inside the `scripts` folder
- You copied `mayaLint` (not `modelChecker-main`)
- Restart Maya after copying

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
