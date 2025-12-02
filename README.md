<h1 align="center">mayaLint - Academic Extension</h1>

<p align="center">
  <strong>A Maya plugin for validating 3D models against academic and professional quality standards</strong>
</p>

<p align="center">
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a> •
  <a href="#available-checks">Available Checks</a> •
  <a href="#academic-extension">Academic Extension</a> •
  <a href="#documentation">Documentation</a>
</p>

---

## About This Project

This is an **Academic Extension** of the original [modelChecker](https://github.com/JakobJK/modelChecker) plugin by Jakob Kousholt, specifically enhanced for digital design students to self-evaluate their 3D models before submission.

The extension adds new quality checks commonly required in academic evaluations, such as flipped normals detection, overlapping vertices, and more.

### Credits

This project is built upon the excellent work of:

- **[Jakob Kousholt](https://www.linkedin.com/in/jakobjk/)** - Original Author, Software Engineer
- **[Niels Peter Kaagaard](https://www.linkedin.com/in/niels-peter-kaagaard-146b8a13)** - Original Author, Senior Modeler at Weta Digital

Original repository: [github.com/JakobJK/modelChecker](https://github.com/JakobJK/modelChecker)

---

## Installation

### Step 1: Download

Download this repository:
- Click the green **"Code"** button above
- Select **"Download ZIP"**
- Extract the ZIP file

### Step 2: Locate Your Maya Scripts Folder

Find your Maya scripts directory based on your operating system:

**macOS:**
```
/Users/<YourUsername>/Library/Preferences/Autodesk/maya/scripts/
```
> **Tip:** The Library folder is hidden by default. In Finder, press `Cmd + Shift + G` and paste the path above (replace `<YourUsername>` with your actual username).

**Windows:**
```
C:\Users\<YourUsername>\Documents\maya\scripts\
```

**Linux:**
```
~/maya/scripts/
```

### Step 3: Copy Files

Copy the `mayaLint` folder (the one containing `mayaLint_UI.py`) into your Maya scripts directory.

Your folder structure should look like:
```
maya/
└── scripts/
    └── mayaLint/
        ├── mayaLint_UI.py
        ├── mayaLint_commands.py
        ├── mayaLint_list.py
        └── ...
```

### Step 4: Create a Shelf Button in Maya

1. **Open Maya**

2. **Open the Script Editor**
   - Go to `Windows` → `General Editors` → `Script Editor`

3. **Create the script**
   - Click on the **Python** tab
   - Paste the following code:

   ```python
   from mayaLint import mayaLint_UI
   mayaLint_UI.UI.show_UI()
   ```

4. **Create a shelf button**
   - Select all the code you just pasted
   - Go to `File` → `Save Script to Shelf...`
   - Enter a name (e.g., "MayaLint")
   - Click OK

5. **Done!** You now have a shelf button to launch mayaLint.

### Troubleshooting

**"No module named mayaLint" error:**
- Make sure the `mayaLint` folder is directly inside the `scripts` folder
- Make sure you copied the inner `mayaLint` folder, not the outer repository folder
- Restart Maya after installing

**Plugin doesn't appear:**
- Check that all `.py` files are present in the mayaLint folder
- Verify you're using a compatible Maya version (2022+)

---

## Usage

### Running Checks

There are three ways to run the checks:

1. **Selection Mode** - Select objects in Object Mode, then run checks on selection only
2. **Hierarchy Mode** - Enter a root node name in the UI to check an entire hierarchy
3. **Scene Mode** - Leave selection empty and root node blank to check the entire scene

### Understanding Results

- **Green checkmark** - Check passed, no issues found
- **Red X with count** - Issues found, click to see details
- **Select Errors** - Click to select the problematic components in Maya

### Best Practices for Students

1. Run checks **before** submitting your project
2. Fix **Flipped Normals** and **Overlapping Vertices** first - these cause render issues
3. Review the error list and understand why each issue matters
4. Some checks (like Triangles) may be acceptable depending on your assignment

---

## Available Checks

### Original Checks (27)

| Category | Checks |
|----------|--------|
| **Naming** | Trailing Numbers, Duplicated Names, Shape Names, Namespaces |
| **General** | Layers, History, Shaders, Unfrozen Transforms, Uncentered Pivots, Parent Geometry, Empty Groups |
| **Topology** | Triangles, Ngons, Open Edges, Poles, Hard Edges, Lamina, Zero Area Faces, Zero Length Edges, Non-Manifold Edges, Starlike |
| **UVs** | Self Penetrating UVs, Missing UVs, UV Range, Cross Border, On Border |

### Academic Extension Checks (New)

| Check | Category | Description |
|-------|----------|-------------|
| **Flipped Normals** | Topology | Detects faces pointing inward that render black or cause lighting issues |
| **Overlapping Vertices** | Topology | Finds vertices at the same position that cause shading artifacts |

*More checks coming soon: Poly Count Limit, Missing Textures, Default Materials, Scene Units, UV Distortion, and more.*

---

## Academic Extension

This extension was created to help digital design students validate their work against common academic evaluation criteria.

### Why These Checks Matter

| Issue | Impact on Grade | How to Fix |
|-------|-----------------|------------|
| Flipped Normals | Major - causes black faces in renders | Select faces → Mesh Display → Reverse |
| Overlapping Vertices | Major - causes shading artifacts | Edit Mesh → Merge → Merge Vertices |
| Missing UVs | Major - textures won't apply | UV → Automatic or Planar Projection |
| Non-Manifold Edges | Moderate - export/boolean issues | Mesh → Cleanup |
| Ngons | Varies - can cause subdivision issues | Mesh Tools → Multi-Cut to add edges |

### Recommended Workflow

1. **Model** your object
2. **Run mayaLint** with all checks enabled
3. **Fix critical issues** (Flipped Normals, Overlapping Vertices, Non-Manifold)
4. **Review other warnings** and fix as needed
5. **Re-run checks** to verify fixes
6. **Submit** your clean model

---

## Documentation

For detailed documentation on each check, including:
- How each check works
- Known limitations
- How to fix issues in Maya

See: **[CHECKS.md](./CHECKS.md)**

---

## Compatibility

- **Maya 2022** and newer (Python 3)
- **Maya 2020-2021** may work but are untested
- **Maya 2019** and older (Python 2) are not supported

---

## License

This project is licensed under the [MIT License](https://rem.mit-license.org/), same as the original modelChecker.

---

## Acknowledgments

Special thanks to **Jakob Kousholt** and **Niels Peter Kaagaard** for creating and open-sourcing the original modelChecker plugin. Their work has helped countless artists validate their 3D models.

If you find this tool useful, consider supporting the original authors on [Gumroad](https://jakejk.gumroad.com/l/htZYj).
