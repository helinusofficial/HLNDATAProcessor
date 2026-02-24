import pymssql

class SqlServerSrv:
    def __init__(self, server='localhost', database='YourDatabase', username='sa', password='sa'):
        self.server = server
        self.database = database
        self.username = username
        self.password = password
        self.conn = None

    def connect(self):
        try:
            # اتصال مستقیم بدون نیاز به درایورهای کثیف ODBC
            self.conn = pymssql.connect(
                server=self.server,
                user=self.username,
                password=self.password,
                database=self.database,
                charset='utf8'
            )
            print("Connected via pymssql (Direct TDS).")
        except Exception as e:
            print(f"Connection failed: {e}")
            raise

    def insert_with_stored_procedure(self, sp_name, article):
        if not self.conn:
            self.connect()

        cursor = self.conn.cursor()
        sql = f"""
        EXEC {sp_name} 
            @ArtTitle=%s, @PubDate=%s, @ArtLanguage=%s, @Pmid=%s, @BankId=%s, @BankNo=%s, 
            @ArtDoi=%s, @ArtType=%s, @JournalTitle=%s, @JournalAbbrev=%s, @ArtPublisher=%s, 
            @ArtVolume=%s, @ArtIssue=%s, @ArtFpage=%s, @ArtPageRange=%s, @ArtAuthors=%s, 
            @ArtKeywords=%s, @ArtPdfLink=%s, @ArtFileName=%s, @CorrEmail=%s, 
            @ArtAbstract=%s, @ArtBody=%s, @MeshTerms=%s, @ArtReferences=%s, @ArtAffiliations=%s, 
            @OrcidIds=%s, @FundingGrant=%s, @FundingId=%s, @EthicsStatement=%s, 
            @CorrespondingAuthor=%s, @ArtLicense=%s, @PubHistory=%s, @CustomMeta=%s
        """
        params = (
            article.ArtTitle,
            article.PubDate,
            article.ArtLanguage,
            article.Pmid,
            article.BankId,
            article.BankNo,
            article.ArtDoi,
            article.ArtType,
            article.JournalTitle,
            article.JournalAbbrev,
            article.ArtPublisher,
            article.ArtVolume,
            article.ArtIssue,
            article.ArtFpage,
            article.ArtPageRange,
            article.ArtAuthors,
            article.ArtKeywords,
            article.ArtPdfLink,
            article.ArtFileName,
            article.CorrEmail,
            article.ArtAbstract or "",
            article.ArtBody or "",      # بدنه اصلی مقاله (NVARCHAR MAX)
            article.MeshTerms or "",
            article.ArtReferences or "",
            article.ArtAffiliations or "",
            article.OrcidIds or "",
            article.FundingGrant or "",
            article.FundingId or "",
            article.EthicsStatement or "",
            article.CorrespondingAuthor or "",
            article.ArtLicense or "",
            article.PubHistory or "",
            article.CustomMeta or ""
        )

        try:
            cursor.execute(sql, params)
            new_id = None
            row = cursor.fetchone()
            if row:
                new_id = row[0]

            self.conn.commit()
            return new_id

        except Exception as e:
            if self.conn:
                self.conn.rollback()
            print(f"Database Error: {e}")
            if article.ArtBody:
                print(f"Failed to send Body. Length: {len(article.ArtBody)}")
            raise
        finally:
            cursor.close()

    def close(self):
        if self.conn:
            self.conn.close()
            print("Connection closed.")