# Webcam nodes for NodeGraphQt

This module provides two nodes for webcam integration:

- **WebcamSelectorNode**: Lists available webcams and outputs the selected device index. Use this node to select which webcam to use in your workflow.
- **WebcamDisplayNode**: Displays the live feed from the selected webcam and allows saving PNG snapshots at a user-defined interval.

## Usage

1. Add a `WebcamSelectorNode` to your node graph. It will automatically detect available webcams and let you select one.
2. Connect its output (`webcam_index`) to the input of a `WebcamDisplayNode`.
3. The `WebcamDisplayNode` will show the live feed and allow you to save images.

## Features

- **Device selection**: Dynamically lists available webcams.
- **Live preview**: Shows real-time video from the selected webcam.
- **Snapshot saving**: Saves PNG images at a user-defined interval or on demand.
- **Tested on Linux**: Uses OpenCV and PySide6.

## Security & Robustness

- Only valid webcam indices are used.
- File dialogs are used for safe file saving.
- Handles webcam disconnects gracefully.

## Tests

- Test webcam detection and selection.
- Test live feed display and update.
- Test image saving at intervals and on demand.
- Test error handling for unavailable webcams.

---

See the node class docstrings for further details.
