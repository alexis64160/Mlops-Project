./scripts/hard_reset.sh
deactivate
./scripts/initialize.sh
source ./scripts/configure.sh
./scripts/start.sh
uv pip install pytest ipython
pytest tests/test_postgres.py 
python dsdc/data/mock.py
python dsdc/data/ingest.py
python dsdc/data/extract_text.py
python dsdc/data/process_text.py
python dsdc/data/process_image.py
python dsdc/data/compute_embeddings.py
python dsdc/models/train.py

