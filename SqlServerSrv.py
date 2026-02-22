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

    def insert_with_stored_procedure(self, sp_name, articleModel):
        if self.engine is None:
            self.connect()

        # پارامترها به صورت tuple و به ترتیب SP
        params = (
            articleModel.ArtTitle,
            articleModel.PubDate,
            articleModel.ArtLanguage,
            articleModel.Pmid,
            articleModel.BankId,
            articleModel.BankNo,
            articleModel.ArtDoi,
            articleModel.ArtType,
            articleModel.JournalTitle,
            articleModel.JournalAbbrev,
            articleModel.ArtPublisher,
            articleModel.ArtVolume,
            articleModel.ArtIssue,
            articleModel.ArtFpage,
            articleModel.ArtPageRange,
            articleModel.ArtAuthors,
            articleModel.CorrespondingAuthor,
            articleModel.ArtAffiliations,
            articleModel.ArtLicense,
            articleModel.ArtPdfLink,
            articleModel.ArtFileName,
            articleModel.ArtKeywords,
            articleModel.PubHistory,
            articleModel.FundingGrant,
            articleModel.CustomMeta,
            articleModel.ArtReferences,
            articleModel.ArtAbstract,
            articleModel.ArtBody,
            articleModel.CorrEmail,
            articleModel.MeshTerms,
            articleModel.FundingId,
            articleModel.EthicsStatement,
            articleModel.OrcidIds
        )

        with self.engine.connect() as conn:
            trans = conn.begin()
            try:
                sql = "EXEC " + sp_name + " " + ",".join(["?"] * len(params))
                result = conn.execute(text(sql), params)
                new_id = result.scalar()
                trans.commit()
                return new_id
            except Exception as e:
                trans.rollback()
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