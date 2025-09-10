import csv
import re
from pathlib import Path
from dsdc import PROJECT_ROOT, CONFIG

# Remplace ce chemin par celui du fichier CSV généré
CSV_PATH = PROJECT_ROOT/CONFIG.paths.rvl_csv  # ← à adapter

def test_rvl_csv_format():
    assert CSV_PATH.exists(), f"CSV file does not exist at {CSV_PATH}"

    with CSV_PATH.open() as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = list(reader)

    # ✅ Test 1: nombre de lignes
    assert len(rows) == 400_000, f"Expected 400,000 rows, found {len(rows)}"

    # ✅ Préparation regex pour test 2
    doc_id_pattern = re.compile(r"^[a-z]{3}[a-z0-9]{5}$")

    for i, row in enumerate(rows):
        assert len(row) == 3, f"Row {i+1} does not have 3 columns: {row}"

        doc_id = row[0]
        filename = row[1]
        label_str = row[2]

        # ✅ Test 2: doc_id format
        assert doc_id_pattern.match(doc_id), f"Invalid document_id format at row {i+1}: {doc_id}"

        # ✅ Test 3: label
        try:
            label = int(label_str)
        except ValueError:
            assert False, f"Label is not an integer at row {i+1}: {label_str}"
        assert 0 <= label <= 15, f"Label out of range at row {i+1}: {label}"