from Bio import Entrez, SeqIO
from Bio.SeqFeature import FeatureLocation

def fetch_exon_sequence(transcript_id, exon_number):
    """
    Retrieve the specified exon sequence and coordinate offsets.
    Supports:
      • Explicit exon features with qualifier "number"
      • Fallback: splitting a joined CDS into parts
    Returns (seq_str, cds_start_abs, exon_start_abs).
    """
    handle = Entrez.efetch(
        db="nucleotide",
        id=transcript_id,
        rettype="gb",
        retmode="text"
    )



    record = SeqIO.read(handle, "genbank")

    # Locate the CDS feature
    cds_feature = next(f for f in record.features if f.type == "CDS")
    cds_start_abs = int(cds_feature.location.start)

    # 1) Try explicit exon features
    exon_feats = [
        f for f in record.features
        if f.type == "exon"
           and f.qualifiers.get("number", [""])[0] == str(exon_number)
    ]
    if exon_feats:
        feat = exon_feats[0]
        exon_seq = feat.location.extract(record.seq)
        exon_start_abs = int(feat.location.start)
        return str(exon_seq), cds_start_abs, exon_start_abs

    # 2) Fallback to splitting the joined CDS
    parts = cds_feature.location.parts
    if exon_number <= len(parts):
        part = parts[exon_number - 1]
        # part may be a FeatureLocation
        start = int(part.start)
        end   = int(part.end)
        exon_seq = record.seq[start:end]
        return str(exon_seq), cds_start_abs, start

    # If neither method found the exon, raise
    raise ValueError(f"Exon {exon_number} not found in {transcript_id}")
