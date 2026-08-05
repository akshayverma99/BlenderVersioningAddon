# Blender Versioning

A Blender 4.2+ alternative to saving copies of objects by duplicating them 


## How to install

1. Click the green **Code** button above and choose **Download ZIP**.
2. In Blender, go to Edit > Preferences > Get Extensions > **Install from Disk...**
   and pick the zip.
3. The panel appears in the 3D viewport sidebar (press <kbd>N</kbd>) under the
   **Versions** tab.

## How to use

1. Select a mesh object in **Object Mode**.
2. **+** (Commit) names and saves the current mesh as a version.
3. Keep modeling, commit again.
4. Select a version and **Checkout** to load it (this discards uncommitted edits).
5. **Update** amends the selected version with the current mesh; **Rename** and
   **−** (Delete) manage the list.

The radio icon marks the version currently checked out.

## Limitations

- Snapshots only cover mesh data. Modifiers, materials, and object transform stay
  on the live object and aren't saved or restored.
- The add-on only works in Object Mode.
- Each commit is a full copy of the mesh, so the `.blend` grows with your history.
