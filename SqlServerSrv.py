from sqlalchemy import create_engine, text

class SqlServerSrv:
    def __init__(self, server='localhost', database='YourDatabase', username='sa', password='sa'):
        self.connection_string = (
            f"mssql+pyodbc://{username}:{password}@{server}/{database}"
            "?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes"
        )
        self.engine = None

    def connect(self):
        try:
            self.engine = create_engine(self.connection_string)
            print("Connected to SQL Server successfully via SQLAlchemy.")
        except Exception as e:
            print(f"Error connecting to SQL Server: {e}")
            raise

    def insert_with_stored_procedure(self, sp_name, article):
        if self.engine is None:
            self.connect()
        params = {
            "ArtTitle": article.ArtTitle,
            "PubDate": article.PubDate,
            "ArtLanguage": article.ArtLanguage,
            "Pmid": article.Pmid,
            "BankId": article.BankId,
            "BankNo": article.BankNo,
            "ArtDoi": article.ArtDoi,
            "ArtType": article.ArtType,
            "JournalTitle": article.JournalTitle,
            "JournalAbbrev": article.JournalAbbrev,
            "ArtPublisher": article.ArtPublisher,
            "ArtVolume": article.ArtVolume,
            "ArtIssue": article.ArtIssue,
            "ArtFpage": article.ArtFpage,
            "ArtPageRange": article.ArtPageRange,
            "ArtAuthors": article.ArtAuthors,
            "ArtKeywords": article.ArtKeywords,
            "ArtPdfLink": article.ArtPdfLink,
            "ArtFileName": article.ArtFileName,
            "CorrEmail": article.CorrEmail,
            # فیلدهای جدول دوم
            "ArtAbstract": article.ArtAbstract,
            "ArtBody": article.ArtBody,
            "MeshTerms": article.MeshTerms,
            "ArtReferences": article.ArtReferences,
            "ArtAffiliations": article.ArtAffiliations,
            "OrcidIds": article.OrcidIds,
            "FundingGrant": article.FundingGrant,
            "FundingId": article.FundingId,
            "EthicsStatement": article.EthicsStatement,
            "CorrespondingAuthor": article.CorrespondingAuthor,
            "ArtLicense": article.ArtLicense,
            "PubHistory": article.PubHistory,
            "CustomMeta": article.CustomMeta
        }

        with self.engine.connect() as conn:
            try:
                placeholders = ", ".join([f"@{k}=:{k}" for k in params.keys()])
                sql = text(f"EXEC {sp_name} {placeholders}")

                result = conn.execute(sql, params)
                new_id = result.scalar()

                conn.commit()
                return new_id
            except Exception as e:
                conn.rollback()
                print(f"Error executing stored procedure: {e}")
                raise

    def close(self):
        """
        Close the database connection.
        """
        if self.engine:
            self.engine.dispose()
            self.engine = None
            print("Connection closed.")