"""Download a small subset of CT volumes from the TotalSegmentator dataset.

Uses HTTP range requests (via `remotezip`) against the official Zenodo
"small subset" archive (102 cases, 3.2GB) so only the requested number of
`ct.nii.gz` files is transferred instead of the whole zip.

Source: https://zenodo.org/records/10047263
(Full 1228-case dataset: https://zenodo.org/records/10047292)

Usage:
    python scripts/download_totalseg_subset.py --n-cases 25 --out-dir data/totalseg_subset
"""

import argparse
import os

from remotezip import RemoteZip

DATASET_URL = (
    "https://zenodo.org/records/10047263/files/"
    "Totalsegmentator_dataset_small_v201.zip?download=1"
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n-cases", type=int, default=25)
    parser.add_argument(
        "--out-dir",
        default=os.path.join(os.path.dirname(__file__), "..", "data", "totalseg_subset"),
    )
    args = parser.parse_args()
    out_dir = os.path.abspath(args.out_dir)
    os.makedirs(out_dir, exist_ok=True)

    with RemoteZip(DATASET_URL) as zf:
        case_ids = sorted(
            {n.split("/")[0] for n in zf.namelist() if n.startswith("s") and "/" in n}
        )
        selected = case_ids[: args.n_cases]
        print(f"{len(case_ids)} cases available in archive, downloading {len(selected)}")

        total_bytes = 0
        for i, case_id in enumerate(selected, 1):
            entry = f"{case_id}/ct.nii.gz"
            case_dir = os.path.join(out_dir, case_id)
            os.makedirs(case_dir, exist_ok=True)
            dest = os.path.join(case_dir, "ct.nii.gz")
            if os.path.exists(dest):
                print(f"[{i}/{len(selected)}] {case_id} already downloaded, skipping")
                continue

            info = zf.getinfo(entry)
            data = zf.read(entry)
            with open(dest, "wb") as f:
                f.write(data)
            total_bytes += info.file_size
            print(f"[{i}/{len(selected)}] {case_id} -> {dest} ({info.file_size / 1e6:.1f} MB)")

    print(f"Done. Total downloaded: {total_bytes / 1e9:.2f} GB -> {out_dir}")


if __name__ == "__main__":
    main()
