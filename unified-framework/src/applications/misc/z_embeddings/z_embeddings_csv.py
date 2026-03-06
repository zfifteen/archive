"""

This script accepts a range n - nmax and wraps each integer from n-nmax in a
DiscreetZetaShift object then save it's self attributes to a CSV file.`z_embeddings.csv`.

need to import domain

"""
import csv
import argparse
import time
import os
from core.domain import DiscreteZetaShift


def main():
    parser = argparse.ArgumentParser(
        description="Generate and save DiscreteZetaShift embeddings to a CSV file."
    )
    parser.add_argument("n_start", type=int, help="The starting integer of the range.")
    parser.add_argument("n_max", type=int, help="The ending integer of the range.")
    parser.add_argument("--csv_name", type=str, default="z_embeddings.csv", help="CSV file name.")
    args = parser.parse_args()

    batch_size = 100
    batch = []
    records_per_file = 100000
    records_in_current_file = 0
    file_counter = 1
    base_name, extension = os.path.splitext(args.csv_name)

    print(f"Generating embeddings for range [{args.n_start}, {args.n_max}] into {base_name}_<n>{extension} (rolled every {records_per_file} records)")

    start_time = time.time()
    last_print_time = start_time

    d_zeta_shift = DiscreteZetaShift(args.n_start)

    current_csv_name = f"{base_name}_{file_counter}{extension}"
    csvfile = open(current_csv_name, 'w', newline='')
    csv_writer = csv.writer(csvfile)

    header = [
        'num', 'b', 'c', 'z', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L',
        'M', 'N', 'O'
    ]
    csv_writer.writerow(header)

    for n in range(args.n_start, args.n_max + 1):
        try:
            if records_in_current_file >= records_per_file:
                if batch:
                    csv_writer.writerows(batch)
                    batch = []
                csvfile.close()

                file_counter += 1
                records_in_current_file = 0
                current_csv_name = f"{base_name}_{file_counter}{extension}"
                print(f"Rolling over to new file: {current_csv_name}")
                csvfile = open(current_csv_name, 'w', newline='')
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow(header)

            attributes = d_zeta_shift.attributes

            # The order of insertion must match the header.
            row = (
                int(attributes['a']),
                float(attributes['b']), float(attributes['c']), float(attributes['z']),
                float(attributes['D']), float(attributes['E']), float(attributes['F']),
                float(attributes['G']), float(attributes['H']), float(attributes['I']),
                float(attributes['J']), float(attributes['K']), float(attributes['L']),
                float(attributes['M']), float(attributes['N']), float(attributes['O'])
            )
            batch.append(row)
            records_in_current_file += 1

            if len(batch) >= batch_size:
                csv_writer.writerows(batch)
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
        csv_writer.writerows(batch)
    
    csvfile.close()

    print("Done.")


if __name__ == "__main__":
    main()