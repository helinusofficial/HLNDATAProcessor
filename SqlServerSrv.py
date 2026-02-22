import pyodbc


class SqlServerSrv:
    def __init__(self, server='localhost', database='YourDatabase', username='sa', password='sa'):
        # رشته اتصال مستقیم برای pyodbc
        self.conn_str = (
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"UID={username};"
            f"PWD={password};"
            "TrustServerCertificate=yes;"
        )
        self.conn = None

    def connect(self):
        try:
            self.conn = pyodbc.connect(self.conn_str)
            print("Connected directly via pyodbc.")
        except Exception as e:
            print(f"Connection failed: {e}")
            raise

    def insert_with_stored_procedure(self, sp_name, article):
        if not self.conn:
            self.connect()

        cursor = self.conn.cursor()

        # استاندارد ODBC CALL - دقیقا ۳۳ علامت سوال مطابق SP شما
        sql = f"{{CALL {sp_name} (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)}}"

        # ترتیب پارامترها رو بر اساس آخرین SP که دادی چک کردم، دقیقه.
        params = (
            article.ArtTitle, article.PubDate, article.ArtLanguage, article.Pmid,
            article.BankId, article.BankNo, article.ArtDoi, article.ArtType,
            article.JournalTitle, article.JournalAbbrev, article.ArtPublisher,
            article.ArtVolume, article.ArtIssue, article.ArtFpage, article.ArtPageRange,
            article.ArtAuthors, article.ArtKeywords, article.ArtPdfLink, article.ArtFileName,
            article.CorrEmail,
            # شروع فیلدهای سنگین (MAX)
            article.ArtAbstract, article.ArtBody, article.MeshTerms,
            article.ArtReferences, article.ArtAffiliations, article.OrcidIds,
            article.FundingGrant, article.FundingId, article.EthicsStatement,
            article.CorrespondingAuthor, article.ArtLicense, article.PubHistory,
            article.CustomMeta
        )

        try:
            cursor.execute(sql, params)

            # --- اصلاح مهم اینجاست ---
            # اگر SP چندین مرحله اجرا داشته باشه، باید بریم سراغ نتیجه‌ای که شامل SELECT هست
            new_id = None

            # رد کردن پیغام‌های Row count (مثل 1 row affected) برای رسیدن به SELECT اصلی
            while cursor.description is None and cursor.nextset():
                pass

            if cursor.description:
                row = cursor.fetchone()
                if row:
                    new_id = row[0]

            self.conn.commit()
            return new_id

        except Exception as e:
            if self.conn:
                self.conn.rollback()
            print(f"SP Execution Error: {e}")
            raise
        finally:
            cursor.close()

    def close(self):
        if self.conn:
            self.conn.close()
            print("Connection closed.")