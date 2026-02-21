import os
from ProcessDataSrv import ProcessDataSrv
from SqlServerSrv import SqlServerSrv


def main():
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
            if article_model.Animal:
                continue

            new_id = db.insert_with_stored_procedure('InsertData', 'Hello World')


            if index % 100 == 0 or index == total_files:
                print(f"[{index}/{total_files}] Processed: {article_model.ArtTitle[:50]}...")

            # اینجا جایی است که می‌توانی مدل را به SQL بفرستی
            # SaveToSql(article_model)

        except Exception as e:
            print(f"Error processing file {path}: {str(e)}")
            continue

    print("--- Processing Completed Successfully ---")


if __name__ == "__main__":
    main()