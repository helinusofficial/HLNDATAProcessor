import os
import sys
import time
import numpy as np
import random
import logging
import torch
from ProcessDataSrv import ProcessDataSrv
from SqlServerSrv import SqlServerSrv
from datetime import datetime

def main():
    # Output and logging
    start_time = time.time()

    code_name = "process"
    base_output_path = r"./"
    input_folder = r"\\192.168.1.22\c$\NCBI-E-utilities\PMC_BreastCancer_XML"

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
    logging.info(f"Started on: {datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")

    logging.info("Connecting to SQl Server...")
    db = SqlServerSrv(server='.',database='HLNLLMBreastDB', username='sa', password='sa')
    db.connect()
    logging.info("Connected")
    logging.info("Start to reading files....")

    if not os.path.exists(input_folder):
        logging.error(f"Error: Folder '{input_folder}' not found!")
        return

    file_paths = []
    for root, dirs, files in os.walk(input_folder):
        for f in files:
            if f.endswith('.xml'):
                full_path = os.path.join(root, f)
                file_paths.append(full_path)

    total_files = len(file_paths)
    logging.info(f"Total files found: {total_files}")
    logging.info("Processing started linearly...")
    nonTarget_Count=0
    doubleDOI_Count=0
    error_Count=0
    target_Count=0
    nobody_Count=0
    noabs_Count=0
    for index, path in enumerate(file_paths, 1):
        try:
            article_model = ProcessDataSrv.process_file(path)
            if article_model and article_model.NonTarget:
                nonTarget_Count += 1
                continue
            if article_model and (not article_model.ArtBody or article_model.ArtBody.strip() == ''):
                nobody_Count += 1
                continue
            if article_model and (not article_model.ArtAbstract or article_model.ArtAbstract.strip() == ''):
                noabs_Count += 1
                continue
            new_id = db.insert_with_stored_procedure('InsertData', article_model)
            if new_id<=0:
                if new_id ==-1:
                    doubleDOI_Count+=1
                    logging.error(f"Double DOI: {path}")
                else:
                    error_Count+=1
                    logging.error(f"Error processing file: {path}")
            else:
                target_Count += 1

            if (index + 1) % 100 == 0:
                logging.info(f"[{index}/{total_files}] Processed - Target:{target_Count}   error:{error_Count}   "
                             f"doubleDOI:{doubleDOI_Count}   NonTarget:{nonTarget_Count}    nobody_Count:{nobody_Count}"
                             f"    noabs_Count:{noabs_Count}")
        except Exception as e:
            logging.error(f"Error processing file {path}: {str(e)}")
            continue

    db.close()
    logging.info("--- Processing Completed Successfully ---")
    logging.info(f"Total:{total_files} Target:{target_Count}    error:{error_Count}   "
                 f"doubleDOI:{doubleDOI_Count}    NonTarget:{nonTarget_Count}    nobody_Count:{nobody_Count}"
                 f"    noabs_Count:{noabs_Count}")
    end_time = time.time()
    elapsed = end_time - start_time
    minutes = int(elapsed // 60)
    seconds = elapsed % 60
    logging.info(f"Execution time: {minutes}:{seconds:.2f}")

if __name__ == "__main__":
    main()