import os
import re
from lxml import etree
from unstructured.cleaners.core import clean, clean_extra_whitespace
from datetime import datetime
from difflib import SequenceMatcher
from ArticleModel import ArticleModel
import copy

class ProcessDataSrv:
    ref_stop_pattern = r'\n\s*(references|reference list|bibliography|literature cited|acknowledgments)\s*\n'
    animal_keywords = [
        "mouse", "mice", "rat", "sprague dawley", "wistar", "long evans",
        "rabbit", "rabbits", "dog", "dogs", "cat", "cats", "zebrafish",
        "danio rerio", "frog", "xenopus", "salmon", "drosophila",
        "bee", "mosquito", "c. elegans", "caenorhabditis elegans",
        "saccharomyces cerevisiae", "guinea pig", "hamster", "gerbil",
        "ferret", "chicken", "quail", "duck", "xenopus laevis",
        "xenopus tropicalis", "pig", "minipig", "sheep", "goat", "cow",
        "calf", "horse", "bovine", "cattle", "ewe", "mare", "sow",
        "veterinary", "ruminant", "ovine", "caprine", "porcine",
        "heifer", "buffalo", "dairy"
    ]

    human_indicators = [
        "patient", "women", "woman", "clinical trial", "cohort", "participant", "volunteer", "biopsy", "human",
        "female","lactation", "breastfeeding", "mammography", "mastalgia", "gynecomastia" , "breast surgery",
        "maternal", "pregnancy", "menopause", "postmenopausal", "nulliparous"
    ]
    breast_keywords = ["breast", "mammary"]
    breast_context_words = [
        "cell", "cells", "gland", "glands", "epithelium", "epithelial",
        "lobule", "lobules", "duct", "ducts", "stroma", "stromal",
        "fibroblast", "fibroblasts", "adipocyte", "adipocytes",
        "myoepithelial", "myoepithelium", "lobular", "ductal",
        "mammary gland", "mammary tissue",
        # clinical words that need proximity to breast keyword
        "cancer", "tumor", "tumour", "biopsy",
    ]
    # words too general alone (patient, tissue) → check proximity
    general_words = ["patient", "patients", "tissue", "tissues"]
    human_breast_cells = ["mcf-7", "mcf7", "mda-mb-231", "t47d", "sk-br-3", "bt-474"]
    animal_breast_cells = ["4t1", "e0771", "mmt", "mtln3"]

    @staticmethod
    def process_file(file_path: str) -> ArticleModel:

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        try:
            parser = etree.XMLParser(recover=True, remove_comments=True)
            tree = etree.parse(file_path, parser=parser)
            root = tree.getroot()

            article = ArticleModel()
            article.BankNo = 1
            article.ArtFileName = os.path.basename(file_path)

            # --- Stage 1: Quick Extraction for Filtering ---
            title = ProcessDataSrv._get_text(root, ".//article-title")
            abstract_node = root.find(".//abstract")
            raw_abstract = " ".join(abstract_node.itertext()) if abstract_node is not None else ""
            kwds = ", ".join([k.text.strip() for k in root.xpath(".//kwd") if k.text])
            meshes = " | ".join([m.text.strip() for m in root.xpath(".//mesh-heading/descriptor-name") if m.text])

            check_zone = f"{title} {raw_abstract} {kwds} {meshes}".lower()

            # --- Stage 2: Refined Filtering (Anti-Fake Logic) ---
            abstract_text = raw_abstract.lower()
            title_text = title.lower()
            check_zone = f"{title_text} {abstract_text} {kwds.lower()} {meshes.lower()}"

            breast_matches = re.findall(r'\b(breast|mammary)\b', check_zone)
            breast_count = len(breast_matches)
            escaped_context = '|'.join(
                re.escape(word) for word in (ProcessDataSrv.breast_context_words + ProcessDataSrv.general_words))

            context_pattern = r'\b(breast|mammary)\b\s*(?:\w+\s+){0,5}\b(' + escaped_context + r')\b'
            context_match_nearby = re.search(context_pattern, check_zone, re.IGNORECASE)
            is_breast_related = False

            if re.search(r'\b(breast|mammary)\b', title_text):
                is_breast_related = True
            elif breast_count >= 2 and context_match_nearby:
                is_breast_related = True
            elif breast_count >= 1 and any(
                    re.search(rf'\b{re.escape(c.lower())}\b', check_zone) for c in ProcessDataSrv.human_breast_cells):
                is_breast_related = True

            has_human = any(re.search(rf'\b{re.escape(k.lower())}\b', check_zone) for k in ProcessDataSrv.human_indicators) or \
                        "humans" in meshes.lower()

            has_animal = any(re.search(rf'\b{re.escape(k.lower())}\b', check_zone) for k in ProcessDataSrv.animal_keywords) or \
                         any(re.search(rf'\b{re.escape(c.lower())}\b', check_zone) for c in
                             ProcessDataSrv.animal_breast_cells)

            article.NonTarget = False

            if not (is_breast_related and has_human) or has_animal:
                article.NonTarget = True
                return article

            # --- Stage 3: Full Metadata Extraction ---
            article.ArtTitle = title

            abstract_nodes = root.xpath(
                ".//abstract[not(@abstract-type='graphical') and not(@abstract-type='toc')]"
            )

            if abstract_nodes:
                all_paragraphs = []

                for main_abstract in abstract_nodes:
                    # --- Step 1: Collect paragraphs separately ---
                    paragraphs = main_abstract.xpath(".//p")
                    if not paragraphs:
                        # fallback: raw text if no <p> exists
                        raw_txt = " ".join(main_abstract.itertext()).strip()
                        if raw_txt:
                            paragraphs = [main_abstract]

                    for p in paragraphs:
                        # Step 2: Clean each paragraph individually
                        txt = " ".join(p.itertext()).strip()
                        if txt:
                            cleaned_p = clean(txt, extra_whitespace=True, dashes=True, bullets=False)
                            cleaned_p = ProcessDataSrv._filter_figure_references(cleaned_p)
                            cleaned_p = ProcessDataSrv._sanitize_string(cleaned_p)
                            cleaned_p = re.sub(r'[ \t]+', ' ', cleaned_p).strip()
                            # --- Step 2.5: Remove Keywords section from this paragraph ---
                            cleaned_p = re.split(r'\r?\n\s*(keywords?|key words?)\s*:', cleaned_p, flags=re.IGNORECASE)[
                                0].strip()

                            if cleaned_p:
                                # Step 3: Append Windows-style separator (\r\n\r\n)
                                all_paragraphs.append(cleaned_p)

                # Step 4: Join all paragraphs into one text
                final_text = "\r\n\r\n".join(all_paragraphs)
                article.ArtAbstract = final_text
            else:
                article.ArtAbstract = ""

            article.ArtKeywords =ProcessDataSrv._sanitize_string(kwds)
            article.MeshTerms = meshes

            article.JournalTitle = ProcessDataSrv._get_text(root, ".//journal-title")
            article.JournalAbbrev = ProcessDataSrv._get_text(
                root, ".//journal-id[@journal-id-type='nlm-ta'] | .//abbrev-journal-title"
            )
            article.ArtPublisher = ProcessDataSrv._get_text(root, ".//publisher-name")
            article.ArtDoi = ProcessDataSrv._get_text(root, ".//article-id[@pub-id-type='doi']")
            article.ArtType = root.get("article-type", "")
            article.ArtLanguage = ProcessDataSrv._get_text(root, ".//language") or "en"

            pmid = ProcessDataSrv._get_text(root, ".//article-id[@pub-id-type='pmid']")
            article.Pmid = int(pmid) if pmid.isdigit() else None

            pmc = ProcessDataSrv._get_text(root, ".//article-id[@pub-id-type='pmc']")
            if pmc:
                pmc_clean = re.sub(r'\D', '', pmc)
                if pmc_clean.isdigit():
                    article.BankId = int(pmc_clean)

            article.ArtVolume = ProcessDataSrv._get_text(root, ".//volume")
            article.ArtIssue = ProcessDataSrv._get_text(root, ".//issue")
            article.ArtFpage = ProcessDataSrv._get_text(root, ".//fpage")
            lpage = ProcessDataSrv._get_text(root, ".//lpage")
            if article.ArtFpage and lpage:
                article.ArtPageRange = f"{article.ArtFpage}-{lpage}"

            pub_date_nodes = root.xpath(
                ".//pub-date[@pub-type='ppub'] | .//pub-date[@pub-type='epub'] | .//pub-date"
            )
            if pub_date_nodes:
                node = pub_date_nodes[0]
                year = ProcessDataSrv._get_text(node, "year")
                month = ProcessDataSrv._get_text(node, "month")
                day = ProcessDataSrv._get_text(node, "day")
                if year.isdigit():
                    try:
                        m = int(month) if month and month.isdigit() and 1 <= int(month) <= 12 else 1
                        d = int(day) if day and day.isdigit() and 1 <= int(day) <= 31 else 1
                        article.PubDate = datetime(int(year), m, d)
                    except (ValueError, TypeError):
                        pass

            authors = []
            orcids = []
            for auth in root.xpath(".//contrib[@contrib-type='author']"):
                given = ProcessDataSrv._get_text(auth, './/given-names')
                sur = ProcessDataSrv._get_text(auth, './/surname')
                name = f"{given} {sur}".strip()
                if name:
                    authors.append(name)

                orcid = ProcessDataSrv._get_text(auth, ".//contrib-id[@contrib-id-type='orcid']")
                if orcid:
                    orcids.append(f"{name}: {orcid}")

                if auth.get("corresp") == "yes":
                    article.CorrespondingAuthor = name
                    email = ProcessDataSrv._get_text(auth, ".//email")
                    if not email:
                        email = ProcessDataSrv._get_text(root, ".//author-notes//email")
                    article.CorrEmail = email

            article.ArtAuthors = ", ".join(authors)
            article.OrcidIds = " || ".join(orcids)

            # Affiliations
            affs = [clean_extra_whitespace(" ".join(aff.itertext())) for aff in root.xpath(".//aff")]
            article.ArtAffiliations = " | ".join(filter(None, affs))

            # License & Ethics
            article.ArtLicense = ProcessDataSrv._get_text(root, ".//license//p")

            ethics = root.xpath(".//notes[@notes-type='ethics-statement'] | .//fn[@fn-type='ethics-statement']")
            if ethics:
                article.EthicsStatement = " ".join(ethics[0].itertext()).strip()

            # --- Section 1: Extract References (Global) ---
            all_refs = []
            for ref in root.xpath(".//ref"):
                ref_text = " ".join(ref.itertext()).strip()
                if ref_text:
                    # Using clean_extra_whitespace for single-line reference formatting
                    formatted_ref = clean_extra_whitespace(ref_text)
                    if formatted_ref not in all_refs:
                        all_refs.append(formatted_ref)

            article.ArtReferences = "\n".join(all_refs)
            article.ArtReferences = ProcessDataSrv._sanitize_string(article.ArtReferences)
            # --- Section 2: Process Body Text (Clean and Filtered) ---
            body_node = root.find(".//body")
            if body_node is not None:
                temp_body = copy.deepcopy(body_node)

                unwanted_query = """
                .//ref-list | .//ref | .//table-wrap | .//fig | .//ack | .//notes |
                .//sec[@sec-type='ref-list'] | .//sec[@sec-type='fn-group'] |
                .//sec[@sec-type='supplementary-material'] | .//formula | .//inline-formula
                """
                for node in temp_body.xpath(unwanted_query):
                    if node.getparent() is not None:
                        node.getparent().remove(node)

                raw_parts = []
                for sec in temp_body.xpath(".//sec"):
                    # Include title
                    title_text = " ".join(sec.xpath("./title//text()")).strip()
                    if title_text:
                        raw_parts.append(title_text)

                    for p in sec.xpath(".//p"):
                        txt = " ".join(p.itertext()).strip()
                        if txt:
                            cleaned_p = clean(
                                txt,
                                extra_whitespace=True,
                                dashes=True,
                                bullets=False
                            )
                            cleaned_p = ProcessDataSrv._filter_figure_references(cleaned_p)
                            cleaned_p = ProcessDataSrv._sanitize_string(cleaned_p)
                            cleaned_p = re.sub(r'[ \t]+', ' ', cleaned_p).strip()
                            cleaned_p = ProcessDataSrv._normalize_references(cleaned_p)
                            if cleaned_p:
                                raw_parts.append(cleaned_p)

                temp_full_text = "\r\n\r\n".join(raw_parts)

                ref_stop_pattern = r'\r?\n\s*(references|reference list|bibliography|literature cited|acknowledgments)\s*\r?\n'
                processed_text = re.split(ref_stop_pattern, temp_full_text, maxsplit=1, flags=re.IGNORECASE)[0]

                # Double newline normalization
                article.ArtBody = re.sub(r'(\r?\n)+', '\r\n\r\n', processed_text.strip())
            else:
                article.ArtBody = ""

            # Funding
            article.FundingGrant = " | ".join([f.text.strip() for f in root.xpath(".//funding-source") if f.text])
            article.FundingId = " | ".join([f.text.strip() for f in root.xpath(".//award-id") if f.text])

            article.ArtPdfLink = ProcessDataSrv._get_text(root, ".//self-uri[@content-type='pdf']/@href")

        except Exception as e:
            print(f"Error in ProcessDataSrv: {file_path} -> {e}")
            return None

        return article

    @staticmethod
    def _get_text(node, xpath: str) -> str:
        try:
            res = node.xpath(xpath)
            if res:
                if isinstance(res[0], etree._Element):
                    return " ".join(res[0].itertext()).strip()
                return str(res[0]).strip()
        except Exception:
            pass
        return ""

    @staticmethod
    def _filter_figure_references(text: str) -> str:
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return " ".join([
            s for s in sentences
            if not (
                    re.search(r'(?i)\b(Fig|Table|Tbl)\.?\s*\d+', s)
                    and len(s) < 65
            )
        ])

    @staticmethod
    def _sanitize_string(text: str) -> str:
        if not text:
            return ""
        # حذف کاراکترهای غیرچاپ‌شونده (Null byte و غیره) که SQL را خراب می‌کنند
        # فقط کاراکترهای بالای 31 (استاندارد) و خط جدید/تب رو نگه می‌داریم
        clean_text = "".join(ch for ch in text if ord(ch) > 31 or ch in "\n\r\t")
        return clean_text.strip()

    @staticmethod
    def _normalize_references(text: str) -> str:
        def fix_ref(match):
            ref = match.group()
            # remove spaces inside brackets
            ref = re.sub(r'\[\s*(.*?)\s*\]', r'[\1]', ref)
            ref = re.sub(r'\(\s*(.*?)\s*\)', r'(\1)', ref)
            # spaces around commas -> normalize
            ref = re.sub(r'\s*,\s*', ',', ref)
            # spaces around dash -> normalize
            ref = re.sub(r'\s*-\s*', '-', ref)
            # replace number sequences with space like "5 9" -> "5-9"
            ref = re.sub(r'(\d+)\s+(\d+)', r'\1-\2', ref)
            # multiple spaces -> single
            ref = re.sub(r'\s+', ' ', ref)
            return ref

        # anything inside [] or ()
        pattern = r'(\[[\w\-,\s.&]+\]|\([\w\-,\s.&]+\))'
        return re.sub(pattern, fix_ref, text)

    @staticmethod
    def _fuzzy_in(word, text, threshold=0.8):
        """Check if word approximately exists in text using fuzzy matching"""
        words = re.findall(r'\w+', text)
        for w in words:
            if SequenceMatcher(None, word, w).ratio() >= threshold:
                return True
        return False