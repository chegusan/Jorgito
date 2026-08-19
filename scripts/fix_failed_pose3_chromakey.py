"""Surgical fix: reprocess ``failed`` pose 3 through the despill-augmented
chroma-key pipeline, then rebuild ONLY the ``failed`` row.

Addendum #4 (docs/phase_results/PHASE_2B_HATCH_PET_RESULT.md) flagged that
pose 3's raw generation includes a soft drop-shadow that
``atlas.remove_background(chroma_key=None, threshold=90.0)`` didn't fully
key out, leaving a small green patch under the feet in row columns 2 and 3
(the two columns using pose 3). Poses 1/2 were already clean -- not
reprocessed here.

No new ``imagegen.generate()`` call: reuses the already-committed raw image
at ``assets/keyframes/raw_single_pose/failed_pose3.png``. Pure Pillow --
no network, no ``HERMES_HOME``.

Usage:
    /home/chegusan/.hermes/hermes-agent/venv/bin/python3 \\
        scripts/fix_failed_pose3_chromakey.py
"""

from __future__ import annotations

from pose_sequence import reprocess_pose
from build_failed_row import main as rebuild_failed_row


def main() -> None:
    out_path = reprocess_pose("failed", "pose3")
    print(f"\nreprocessed pose3 -> {out_path}")
    print("\nrebuilding failed row from reprocessed poses...")
    rebuild_failed_row()


if __name__ == "__main__":
    main()
