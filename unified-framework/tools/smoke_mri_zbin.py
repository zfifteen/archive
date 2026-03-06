def series_uid_of(ds):
    return getattr(ds, "SeriesInstanceUID", "unknown")

def iter_slices_with_meta(dicom_dir):
    files = sorted(glob.glob(os.path.join(dicom_dir, "**", "*.dcm"), recursive=True))
    for fp in files:
        try:
            ds = pydicom.dcmread(fp, force=True)
            arr = ds.pixel_array.astype(np.float32)
            slope = float(getattr(ds, "RescaleSlope", 1.0))
            inter = float(getattr(ds, "RescaleIntercept", 0.0))
            arr = arr * slope + inter
            yield series_uid_of(ds), arr, ds
        except Exception:
            continue

def group_by_series_then_shape(dicom_dir):
    groups = {}  # (series_uid, shape) -> list of (arr, ds)
    total = 0
    for uid, arr, ds in iter_slices_with_meta(dicom_dir):
        total += 1
        key = (uid, arr.shape)
        groups.setdefault(key, []).append((arr, ds))
    return groups, total

def pick_t2_like(uids_to_slices):
    # prefer a series with larger EchoTime if available
    def te_of(ds):
        try:
            return float(getattr(ds, "EchoTime", 0.0))
        except Exception:
            return 0.0
    scored = []
    for (uid, shape), items in uids_to_slices.items():
        tes = [te_of(ds) for (_, ds) in items]
        scored.append(((uid, shape), np.median(tes) if tes else 0.0, len(items)))
    # sort by EchoTime desc, then by slice count desc
    scored.sort(key=lambda t: (t[1], t[2]), reverse=True)
    return [x[0] for x in scored]  # ordered keys
