from dsdc.image.preprocess import preprocess, PREPROCESSOR_NAME
from dsdc.db.crud import get_document_list, get_processed_image_list, add_processed_images
from dsdc import CONFIG
import logging

if __name__ == "__main__":
    documents = get_document_list()
    document_ids = set(map(lambda x:x.id, documents))
    processed_images = get_processed_image_list()
    # TODO: Ajouter le processeur dans la requete (si le calcul a été fait avec un processeur plus ancien, 
    # on pourra souhaiter refaire le calcul)
    processed_image_ids = set(map(lambda x:x.document_id, processed_images))
    to_process = sorted(list(document_ids - processed_image_ids))
    
    documents = [d for d in documents if d.id in to_process]
    document_ids = list(map(
        lambda x: x.id,
        documents
    ))
    original_files = list(map(
        lambda x:CONFIG.paths.raw/x.original_file,
        documents
        ))

    output_paths = list(map(
        lambda doc: CONFIG.paths.processed/doc.id[0]/doc.id[1]/doc.id/"image.png",
        documents
    ))

    for document_id, original_file, output_path in zip(document_ids, original_files, output_paths):
        preprocess(document_id, original_file, output_path)
    logging.info(f"{len(document_ids)} images were successfully preprocessed.")
    add_processed_images(list(zip(
            document_ids,
            list(map(lambda p:p.relative_to(CONFIG.paths.processed), output_paths)),
            [PREPROCESSOR_NAME] * len(document_ids)
        )))
