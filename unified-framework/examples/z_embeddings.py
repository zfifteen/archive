"""

This script accepts a range n - nmax and wraps each integer from n-nmax in a
DiscreetZetaShift object then save it's self attributes to a sqlite database.`z_embeddings.db`.

need to import domain

"""
import sqlite3
import argparse
import time
from domain import DiscreteZetaShift


def main():
    parser = argparse.ArgumentParser(
        description="Generate and save DiscreteZetaShift embeddings to a SQLite database."
    )
    parser.add_argument("n_start", type=int, help="The starting integer of the range.")
    parser.add_argument("n_max", type=int, help="The ending integer of the range.")
    parser.add_argument("--db_name", type=str, default="z_embeddings.db", help="Database file name.")
    args = parser.parse_args()

    conn = sqlite3.connect(args.db_name)
    cursor = conn.cursor()

    # Create table. The attribute 'a' is the same as 'n'.
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS z_embeddings (
                                                               num INTEGER PRIMARY KEY, b REAL, c REAL, z REAL, D REAL, E REAL, F REAL,
                                                               G REAL, H REAL, I REAL, J REAL, K REAL, L REAL, M REAL, N REAL, O REAL
                   )
                   ''')

    batch_size = 100
    batch = []

    print(f"Generating embeddings for range [{args.n_start}, {args.n_max}] into {args.db_name}")

    start_time = time.time()
    last_print_time = start_time

    d_zeta_shift = DiscreteZetaShift(args.n_start)

    for n in range(args.n_start, args.n_max + 1):
        try:
            attributes = d_zeta_shift.attributes

            # Convert mpmath numbers to standard floats for SQLite
            # The order of insertion must match the table schema.
            row = (
                int(attributes['a']),
                float(attributes['b']), float(attributes['c']), float(attributes['z']),
                float(attributes['D']), float(attributes['E']), float(attributes['F']),
                float(attributes['G']), float(attributes['H']), float(attributes['I']),
                float(attributes['J']), float(attributes['K']), float(attributes['L']),
                float(attributes['M']), float(attributes['N']), float(attributes['O'])
            )
            batch.append(row)

            if len(batch) >= batch_size:
                cursor.executemany('INSERT OR REPLACE INTO z_embeddings VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', batch)
                conn.commit()
                batch = []

            current_time = time.time()
            if current_time - last_print_time >= 30:
                elapsed_time = current_time - start_time
                progress = (n - args.n_start + 1) / (args.n_max - args.n_start + 1) * 100
                print(f"Progress: {n}/{args.n_max} ({progress:.2f}%), Time elapsed: {elapsed_time:.2f} sec")
                last_print_time = current_time

            d_zeta_shift = d_zeta_shift.unfold_next()

        except Exception as e:
            print(f"Error processing n={n}: {e}")

    # Insert remaining items
    if batch:
        cursor.executemany('INSERT OR REPLACE INTO z_embeddings VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', batch)
        conn.commit()

    conn.close()
    print("Done.")


if __name__ == "__main__":
    main()