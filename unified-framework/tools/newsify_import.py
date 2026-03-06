#!/usr/bin/env python3
"""Import RSS feeds into Newsify from CSV using Newsify's pending-add pipeline."""

from __future__ import annotations

import argparse
import csv
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Import feeds from CSV into Newsify (macOS) with category->folder mapping."
    )
    parser.add_argument("csv_path", type=Path, help="Path to CSV with Category, Feed Name, RSS URL columns.")
    parser.add_argument(
        "--db-path",
        type=Path,
        default=Path.home()
        / "Library/Containers/com.synsion.Newsify/Data/Library/Application Support/Newsify.sqlite",
        help="Path to Newsify.sqlite",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and calculate changes, but rollback instead of committing.",
    )
    args = parser.parse_args()

    csv_path: Path = args.csv_path.expanduser().resolve()
    db_path: Path = args.db_path.expanduser().resolve()
    dry_run: bool = args.dry_run

    if not csv_path.exists():
        print(f"ERROR: CSV not found: {csv_path}", file=sys.stderr)
        return 1
    if not db_path.exists():
        print(f"ERROR: DB not found: {db_path}", file=sys.stderr)
        return 1

    rows: list[tuple[str, str, str]] = []
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"Category", "Feed Name", "RSS URL"}
        if reader.fieldnames is None or not required.issubset(set(reader.fieldnames)):
            print(
                "ERROR: CSV must include headers: Category, Feed Name, RSS URL",
                file=sys.stderr,
            )
            return 1
        seen: set[tuple[str, str, str]] = set()
        for item in reader:
            category = (item.get("Category") or "").strip()
            feed_name = (item.get("Feed Name") or "").strip()
            rss_url = (item.get("RSS URL") or "").strip()
            if not category or not feed_name or not rss_url:
                continue
            key = (category, feed_name, rss_url)
            if key in seen:
                continue
            seen.add(key)
            rows.append(key)

    if not rows:
        print("No valid rows found in CSV; nothing to import.")
        return 0

    if not dry_run:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_path = db_path.with_name(f"{db_path.name}.bak-import-{stamp}")
        shutil.copy2(db_path, backup_path)
        print(f"Backup: {backup_path}")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = OFF")
    cur = conn.cursor()

    created_folders = 0
    inserted_feeds = 0
    linked_feeds = 0
    pending_links = 0

    try:
        conn.execute("BEGIN IMMEDIATE")

        category_to_folder_pk: dict[str, int] = {}
        category_to_folder_ordering: dict[str, str] = {}

        for category, _, _ in rows:
            if category in category_to_folder_pk:
                continue

            existing_folder = cur.execute(
                "SELECT Z_PK, ZORDERING FROM ZFOLDER WHERE ZTITLE = ? AND ZPROFILE = 1",
                (category,),
            ).fetchone()
            if existing_folder is not None:
                category_to_folder_pk[category] = int(existing_folder["Z_PK"])
                category_to_folder_ordering[category] = str(existing_folder["ZORDERING"] or "")
                continue

            next_folder_pk = int(cur.execute("SELECT COALESCE(MAX(Z_PK), 0) + 1 FROM ZFOLDER").fetchone()[0])
            next_folder_sort = int(
                cur.execute("SELECT COALESCE(MAX(ZSORTNUM), 0) + 1 FROM ZFOLDER").fetchone()[0]
            )
            folder_ordering = str(cur.execute("SELECT UPPER(HEX(RANDOMBLOB(4)))").fetchone()[0])
            folder_sortid = str(cur.execute("SELECT UPPER(HEX(RANDOMBLOB(4)))").fetchone()[0])

            cur.execute(
                """
                INSERT INTO ZFOLDER (
                    Z_PK, Z_ENT, Z_OPT, ZISPROTECTED,
                    ZLOCALSTARREDUNREADITEMCOUNT, ZLOCALSTARREDUNREADITEMCOUNTDELTA,
                    ZLOCALUNREADITEMCOUNT, ZLOCALUNREADITEMCOUNTDELTA,
                    ZREMOVEPENDING, ZSORTNUM, ZTAGDELETEPENDING, ZTITLECHANGEPENDING,
                    ZNAVIGATIONPROFILE, ZPROFILE, ZORDERING, ZSORTID, ZSOURCEID, ZTITLE
                ) VALUES (?, 5, 1, 0, 0, 0, 0, 0, 0, ?, 0, 0, 1, 1, ?, ?, ?, ?)
                """,
                (next_folder_pk, next_folder_sort, folder_ordering, folder_sortid, category, category),
            )
            category_to_folder_pk[category] = next_folder_pk
            category_to_folder_ordering[category] = folder_ordering
            created_folders += 1

        for category, feed_name, rss_url in rows:
            source_id = f"feed/{rss_url}"

            existing_feed = cur.execute(
                """
                SELECT Z_PK
                FROM ZFEED
                WHERE ZSOURCE = 'google-reader'
                  AND ZSOURCEID = ?
                ORDER BY Z_PK
                LIMIT 1
                """,
                (source_id,),
            ).fetchone()

            if existing_feed is None:
                folder_pk = category_to_folder_pk[category]
                folder_ordering = category_to_folder_ordering[category]
                folder_max_sort = cur.execute(
                    """
                    SELECT MAX(f.ZSORTNUM)
                    FROM ZFEED f
                    JOIN Z_1FOLDERS l ON l.Z_1FEEDS = f.Z_PK
                    WHERE l.Z_5FOLDERS = ?
                    """,
                    (folder_pk,),
                ).fetchone()[0]
                next_feed_sort = 0 if folder_max_sort is None else int(folder_max_sort) + 1

                parsed = urlparse(rss_url)
                site_url = f"{parsed.scheme}://{parsed.netloc}" if parsed.scheme and parsed.netloc else rss_url

                next_feed_pk = int(cur.execute("SELECT COALESCE(MAX(Z_PK), 0) + 1 FROM ZFEED").fetchone()[0])

                cur.execute(
                    """
                    INSERT INTO ZFEED (
                        Z_PK, Z_ENT, Z_OPT, ZADDPENDING,
                        ZLOCALSTARREDUNREADITEMCOUNT, ZLOCALSTARREDUNREADITEMCOUNTDELTA,
                        ZLOCALUNREADITEMCOUNT, ZLOCALUNREADITEMCOUNTDELTA, ZREMOVEPENDING,
                        ZSORTNUM, ZTITLECHANGEPENDING, ZNAVIGATIONPROFILE, ZPROFILE,
                        ZFEEDURL, ZIMAGE, ZLARGEIMAGE, ZLINK, ZSORTID, ZSOURCE, ZSOURCEID, ZTITLE
                    ) VALUES (?, 1, 1, 1, 0, 0, 0, 0, 0, ?, 0, NULL, 1, ?, '', '', '110', ?, 'google-reader', ?, ?)
                    """,
                    (next_feed_pk, next_feed_sort, site_url, folder_ordering, source_id, feed_name),
                )
                feed_pk = next_feed_pk
                inserted_feeds += 1
            else:
                feed_pk = int(existing_feed["Z_PK"])
                cur.execute("UPDATE ZFEED SET ZADDPENDING = 1 WHERE Z_PK = ?", (feed_pk,))

            folder_pk = category_to_folder_pk[category]

            has_link = cur.execute(
                "SELECT 1 FROM Z_1FOLDERS WHERE Z_1FEEDS = ? AND Z_5FOLDERS = ?",
                (feed_pk, folder_pk),
            ).fetchone()
            if has_link is None:
                cur.execute(
                    "INSERT INTO Z_1FOLDERS (Z_1FEEDS, Z_5FOLDERS) VALUES (?, ?)",
                    (feed_pk, folder_pk),
                )
                linked_feeds += 1

            has_pending_link = cur.execute(
                """
                SELECT 1
                FROM Z_1PENDINGADDEDFOLDERS
                WHERE Z_1PENDINGADDEDFEEDS = ? AND Z_5PENDINGADDEDFOLDERS = ?
                """,
                (feed_pk, folder_pk),
            ).fetchone()
            if has_pending_link is None:
                cur.execute(
                    """
                    INSERT INTO Z_1PENDINGADDEDFOLDERS
                    (Z_1PENDINGADDEDFEEDS, Z_5PENDINGADDEDFOLDERS)
                    VALUES (?, ?)
                    """,
                    (feed_pk, folder_pk),
                )
                pending_links += 1

        max_feed_pk = int(cur.execute("SELECT COALESCE(MAX(Z_PK), 0) FROM ZFEED").fetchone()[0])
        max_folder_pk = int(cur.execute("SELECT COALESCE(MAX(Z_PK), 0) FROM ZFOLDER").fetchone()[0])
        cur.execute("UPDATE Z_PRIMARYKEY SET Z_MAX = ? WHERE Z_ENT = 1", (max_feed_pk,))
        cur.execute("UPDATE Z_PRIMARYKEY SET Z_MAX = ? WHERE Z_ENT = 5", (max_folder_pk,))

        total_feeds = int(cur.execute("SELECT COUNT(*) FROM ZFEED").fetchone()[0])
        total_folders = int(cur.execute("SELECT COUNT(*) FROM ZFOLDER").fetchone()[0])
        total_pending = int(cur.execute("SELECT COUNT(*) FROM ZFEED WHERE ZADDPENDING = 1").fetchone()[0])

        if dry_run:
            conn.rollback()
            print("DRY RUN: changes rolled back.")
        else:
            conn.commit()
            print("Import committed.")

        print(f"Rows read: {len(rows)}")
        print(f"Folders created: {created_folders}")
        print(f"Feeds inserted: {inserted_feeds}")
        print(f"Folder links added: {linked_feeds}")
        print(f"Pending-folder links added: {pending_links}")
        print(f"Current totals -> feeds: {total_feeds}, folders: {total_folders}, add-pending feeds: {total_pending}")
        return 0
    except Exception as exc:  # noqa: BLE001
        conn.rollback()
        print(f"ERROR: import failed: {exc}", file=sys.stderr)
        return 1
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
