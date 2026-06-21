# Mesh Versioning

A Blender 4.2+ add-on that gives a mesh object a git-like history of named
snapshots. Box-model something, **commit** a version, keep editing (loop cuts for
a sub-d cage), commit again, and freely **checkout** any earlier snapshot.

## How it works

Each commit copies the object's **Mesh datablock** (`obj.data`) into a new
datablock kept alive with a *fake user*, and stores a pointer to it on the object.
Checkout assigns a fresh **copy** of a snapshot back into `obj.data`, so the
snapshot itself is never mutated by later edits. Everything serializes into the
`.blend`.

**Snapshot scope:** mesh geometry only — verts/edges/faces plus UVs, vertex
colors, and creases that live on the mesh. Modifiers (Subdivision Surface),
material slots, and object transform stay on the live object and persist across
checkouts, which is exactly what a sub-d cage workflow wants.

## Install

Blender → Edit → Preferences → Get Extensions → **Install from Disk…** and pick
this folder (or a zip of it). The panel appears in the 3D viewport sidebar
(press <kbd>N</kbd>) under the **Versions** tab.

## Usage

1. Select a mesh object, in **Object Mode**.
2. **+** (Commit) — name and save the current mesh as a version.
3. Keep modeling, commit again.
4. Select a version and **Checkout** to load it (discards uncommitted edits).
5. **Update** amends the selected version with the current mesh; **Rename** and
   **−** (Delete) manage the list.

The radio icon marks the version currently checked out.

## Notes

- Operators require **Object Mode** — you can't swap mesh data mid-edit.
- Every commit is a full mesh copy, so the `.blend` grows with history. Deleting a
  version releases its fake user so it's reclaimed on the next save / orphan purge.

## Out of scope (v1)

Modifier/material snapshotting, branching history, version diffing, and per-version
thumbnails.
