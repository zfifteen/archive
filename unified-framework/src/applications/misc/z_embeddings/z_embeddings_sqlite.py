#!/usr/bin/env python3
import argparse
import sqlite3
import time 
from core.domain import DiscreteZetaShift

def main():
    parser = argparse.ArgumentParser(
        description="Generate DiscreteZetaShift embeddings and store in SQLite."
    )
    parser.add_argument("n_start", type=int, help="The starting integer of the range.")
    parser.add_argument("n_max", type=int, help="The ending integer of the range.")
    parser.add_argument("--db_name", type=str, default="z_embeddings.db",
                        help="SQLite database file name.")
    parser.add_argument("--table_name", type=str, default="z_embeddings",
                        help="Table name in the database.")
    parser.add_argument("--batch_size", type=int, default=100,
                        help="Number of rows to insert per transaction.")
    args = parser.parse_args()

    conn = sqlite3.connect(args.db_name)
    cur = conn.cursor()

    # Drop and recreate table
    cur.execute(f"DROP TABLE IF EXISTS {args.table_name}")
    cur.execute(f"""
        CREATE TABLE {args.table_name} (
            num INTEGER PRIMARY KEY,
            b   REAL, c   REAL, z   REAL,
            D   REAL, E   REAL, F   REAL,
            G   REAL, H   REAL, I   REAL,
            J   REAL, K   REAL, L   REAL,
            M   REAL, N   REAL, O   REAL
        )
    """)
    conn.commit()

    insert_sql = f"""
        INSERT INTO {args.table_name}
        (num,b,c,z,D,E,F,G,H,I,J,K,L,M,N,O)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    print(f"Storing embeddings for range [{args.n_start}, {args.n_max}] "
          f"into {args.db_name}/{args.table_name}")

    start_time = time.time()
    last_print = start_time
    batch = []

    # initialize the object
    d_zeta = DiscreteZetaShift(args.n_start)

    for n in range(args.n_start, args.n_max + 1):
        try:
            attrs = d_zeta.attributes
            row = (
                int(attrs['a']),
                float(attrs['b']), float(attrs['c']), float(attrs['z']),
                float(attrs['D']), float(attrs['E']), float(attrs['F']),
                float(attrs['G']), float(attrs['H']), float(attrs['I']),
                float(attrs['J']), float(attrs['K']), float(attrs['L']),
                float(attrs['M']), float(attrs['N']), float(attrs['O'])
            )
            batch.append(row)

            # insert batch
            if len(batch) >= args.batch_size:
                cur.executemany(insert_sql, batch)
                conn.commit()
                batch.clear()

            # periodic progress
            now = time.time()
            if now - last_print >= 30:
                elapsed = now - start_time
                pct = (n - args.n_start + 1) / (args.n_max - args.n_start + 1) * 100
                print(f"Progress: {n}/{args.n_max} ({pct:.2f}%), elapsed {elapsed:.1f}s")
                last_print = now

            # advance to next
            d_zeta = d_zeta.unfold_next()

        except Exception as e:
            # computation errors are logged and skipped
            print(f"Error at n={n}: {e}")

    # insert any remaining rows
    if batch:
        cur.executemany(insert_sql, batch)
        conn.commit()

    conn.close()
    print("Done.")

if __name__ == "__main__":
    main()