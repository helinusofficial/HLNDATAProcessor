import os
from ProcessDataSrv import ProcessDataSrv
from SqlServerSrv import SqlServerSrv
from datetime import datetime
import os
import sys
import time
import numpy as np
import random
import logging
import torch

def main():
    # Output and logging
    start_time = time.time()
    logging.info(f"Started on: {datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")

    code_name = "train_tinyllm"
    base_output_path = r"/"

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_path = os.path.join(base_output_path, f"{code_name}_Run_{timestamp}")
    os.makedirs(output_path, exist_ok=True)
    log_file_path = os.path.join(output_path, f"{code_name}_Log.txt")

    sys.stdout.reconfigure(encoding='utf-8')
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler(log_file_path, mode='w', encoding='utf-8')
    file_handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
    logger.addHandler(console_handler)
    random_state = 102
    random.seed(random_state)
    np.random.seed(random_state)
    torch.manual_seed(random_state)


    input_folder = r"D:\a"
    db = SqlServerSrv(server='.',database='HLNLLMBreastDB', username='sa', password='sa')
    db.connect()
    if not os.path.exists(input_folder):
        print(f"Error: Folder '{input_folder}' not found!")
        return

    file_paths = [
        os.path.join(input_folder, f)
        for f in os.listdir(input_folder)
        if f.endswith('.xml')
    ]

    total_files = len(file_paths)
    print(f"Total files found: {total_files}")
    print("Processing started linearly...")

    for index, path in enumerate(file_paths, 1):
        try:
            article_model = ProcessDataSrv.process_file(path)
            if article_model and article_model.NonTarget:
                print(f"NonTarget file {article_model.ArtFileName}")
                continue

            new_id = db.insert_with_stored_procedure('InsertData', article_model)
            if new_id<=0:
                print(f"Error processing file {path}")

            if index % 100 == 0 or index == total_files:
                print(f"[{index}/{total_files}] Processed: {article_model.ArtTitle[:50]}...")

        except Exception as e:
            print(f"Error processing file {path}: {str(e)}")
            continue

    print("--- Processing Completed Successfully ---")
    end_time = time.time()
    elapsed = end_time - start_time
    minutes = int(elapsed // 60)
    seconds = elapsed % 60
    logging.info(f"Execution time: {minutes}:{seconds:.2f}")

if __name__ == "__main__":
    main()