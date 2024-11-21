import sys
import csv
from .dedup import write_tsv, clean_and_normalize, generate_minhash_signature, generate_shingles, track_memory_and_time
from .dedup import lsh_banding, find_candidate_pairs
from .dedup import UnionFind
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def read_tsv_no_headers(file_path: str):
    """
    Reads a TSV file without headers and assigns the first column as 'id' and the second as 'text'.
    :param file_path: Path to the TSV file.
    :return: List of dictionaries with keys 'id' and 'text'.
    """
    data = []
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter='\t')
        for row in reader:
            if len(row) >= 2:  # Ensure both 'id' and 'text' columns are present
                data.append({'id': row[0], 'text': row[1]})
            elif len(row) == 1:  # Handle rows with only text (no id)
                data.append({'id': str(len(data) + 1), 'text': row[0]})  # Assign auto-generated id
    return data

def remove_exact_duplicates(documents):
    """
    Removes exact duplicate documents from the collection.
    :param documents: List of documents.
    :return: Deduplicated list of documents.
    """
    unique_docs = {}
    duplicates = []

    for doc in documents:
        if doc['text'] not in unique_docs:
            unique_docs[doc['text']] = doc
        else:
            duplicates.append(doc)

    print(f"Processed {len(unique_docs)} unique documents and found {len(duplicates)} duplicates.")  # Debugging
    return list(unique_docs.values()), duplicates

@track_memory_and_time
def nearest_neighbor_search(file_path, output_path, query, num_hashes=300, num_bands=50, rows_per_band=2):
    # Step 1: Read the documents without headers
    logging.info("Starting deduplication process...")
    documents = read_tsv_no_headers(file_path)
    # print(documents)
    # Step 2: Remove exact duplicates
    unique_docs, removed_duplicates = remove_exact_duplicates(documents)
    logging.info(f"Removed {len(removed_duplicates)} exact duplicates.")

    # Step 3: Clean and normalize documents
    for doc in unique_docs:
        doc['text'] = clean_and_normalize(doc['text'])
    

    # Step 4: Compute Minhash signatures for each document
    logging.info("\nGenerating shingles and computing Minhash signatures...")
    for doc in unique_docs:
        doc['shingle'] = generate_shingles(doc['text'])
        doc['minhash'] = generate_minhash_signature(doc['shingle'], num_hashes)
        # print(f"Document {doc['id']} shingles: {shingles}")
        # print(f"Document {doc['id']} MinHash: {doc['minhash']}")



    # Step 5: LSH banding to find candidate pairs
    logging.info("\nFinding candidate pairs with LSH banding...")
    signatures = [doc['minhash'] for doc in unique_docs]
    # candidates = lsh_banding(signatures, num_bands, rows_per_band)

    # Step 6: Process the query
    logging.info("\nProcessing the query...")
    query_cleaned = clean_and_normalize(query)
    query_shingle = generate_shingles(query_cleaned)
    query_signature = generate_minhash_signature(query_shingle, num_hashes)

    query_candidates = lsh_banding(signatures + [query_signature], num_bands, rows_per_band)
    logging.info(f"Query candidates after LSH: {query_candidates}")

    # Step 6: Cluster candidate documents using Union-Find
    # print("\nClustering documents using Union-Find...")
    uf = UnionFind(len(unique_docs) + 1)
    for doc1, doc2 in query_candidates:
        uf.union(doc1, doc2)

    # make sure query and document are in the same cluster
    find = False 
    query_doc_id = len(unique_docs)  # The ID of the Query document can be set to the length of the document list
    for doc_id in range(len(unique_docs)):  # iterate ID
        if uf.find(doc_id) == uf.find(query_doc_id):  # make sure query and document are in the same cluster
            #print(f"Document {doc_id} belongs to the same cluster as the query")
            logging.info(f"Best match for the query from {doc_id}")
            logging.info(unique_docs[doc_id]['text'])
            find = True
            # return unique_docs[doc_id]['text']
    if not find:
        logging.info(f'There is no similarity between query and documents.')

    with open(output_path, 'w') as f:
        f.write(unique_docs[doc_id]['text'])

        if removed_duplicates:
            for dup in removed_duplicates:
                f.write(dup['id'] + "\n")


if __name__ == '__main__':
    # setting
    num_hashes = 300
    num_bands = 50
    rows_per_band = 2
    
    # # test nearest_neighbor_search 
    # best_match = nearest_neighbor_search(file_path, query, num_hashes, num_bands, rows_per_band)
    # print(f"Best match for the query from {file_path}: {best_match}")

    query = 'PHOTO: JESSICA HROMAS WE ALL EXPECTED SOMEAMUSING TWEETS DURING LAST NIGHT\'SFINAL EPISODE OF THE BACHELOR AU , BUT I DOUBT ANY OF US EXPECTED MOST OF THOSE AMUSING TWEETS TO COME FROM NSW PREMIER MIKE BAIRD. AND YET, THIS IS A THING THAT HAPPENED. JUST AS THE SEASON FINALE WAS GETTING UNDERWAY, BAIRD TWEETEDTHAT HE WAS STUCK AT HOME "WITH THE MAN-FLU", AND THAT HIS DAUGHTERS HAD COMANDEERED THE TV TO FIND OUT WHETHER BACHIE SAM WOULD GIVE HIS FINAL ROSE TOSNEZANA OR LANA. BACHELOR SAM WOOD AND NEW LOVE, SNEZANA MARKOSKI. '
    if len(sys.argv) != 3:
        logging.error("Usage: python lsh_case2.py <input_file> <output_file>")
        sys.exit(1)
    input_file = sys.argv[1]
    output_file = sys.argv[2]

    nearest_neighbor_search(input_file, output_file, query, num_hashes, num_bands, rows_per_band)

    # 300
    # query = 'UPDATED: 2015-09-23 11:51:27 PESSIMISM ABOUT US-CHINA RELATIONS SEEMS TO BE PERMEATING THE AIR RECENTLY. MANY OBSERVERS ON BOTH SIDES HAVE RUNG ALARM BELLS ABOUT GROWING TENSION IN THE RELATIONSHIP, ESPECIALLY OVER CYBERSECURITY, THE SOUTH CHINA SEA, AND STOCK MARKET TURMOIL. WHAT HAS GONE WRONG? HOW CAN THE TWO COUNTRIES MOVE THIS VITAL RELATIONSHIP FORWARD? IN 1940, KENNETH WHERRY, MAYOR OF PAWNEE CITY, NEBRASKA, SAID, "WITH GOD\'S HELP, WE WILL LIFT SHANGHAI UP AND UP, EVER UP, UNTIL IT IS JUST LIKE KANSAS CITY." IF WHERRY, WHO BECAME A US SENATOR LATER, WERE STILL ALIVE TODAY, HE WOULD BE SURPRISED TO LEARN THAT MODERN SHANGHAI REMAINS DIFFERENT FROM KANSAS CITY, BUT IT IS PROBABLY KANSAS CITY THAT NEEDS TO BE LIFTED UP IN TERMS OF DEVELOPMENT NOW. AMERICANS HAVE A MISSIONARY IMPULSE TO CHANGE CHINA, EITHER BY CHRISTIANIZING IT IN THE 19TH CENTURY OR DEMOCRATIZING IT IN THE 21ST CENTURY. FROM THE VERY BEGINNING OF INTERACTIONS, THE UNITED STATES HAS BEEN DEALING WITH CHINA FROM A POSITION OF STRENGTH; IT IS ILL-PREPARED TO LIVE WITH A NATION AS BIG AND ALMOST AS POWERFUL AS ITSELF. CHINA\'S METEORIC RE-EMERGENCE AS A GLOBAL POWER BY THE EARLY 21ST CENTURY IS TRULY STUNNING TO AMERICANS AND EVEN TO MANY CHINESE. THE US ECONOMY SUFFERED SERIOUSLY IN THE 2008-2009 FINANCIAL CRISIS, FROM WHICH IT IS STILL RECOVERING. MEANWHILE, THE CHINESE ECONOMY HAS CONTINUED TO CHARGE FORWARD, AND AFTER OVERTAKING JAPAN AS THE WORLD\'S SECOND-LARGEST ECONOMY IN 2010, IT IS POISED TO TAKE THE TOP SPOT SOON. THE GLOBAL POWER STRUCTURE HAS CHANGED FUNDAMENTALLY. THE AMERICAN CONCERN ABOUT CHINA\'S RISING POWER REFLECTS AMERICANS\' LACK OF CONFIDENCE IN THEIR COMPETITION WITH CHINA. THE REALITY IS THAT CHINA REMAINS A DEVELOPING COUNTRY DESPITE A LARGE ECONOMY. ACCORDING TO PREMIER LI KEQIANG, 200 MILLION CHINESE STILL LIVE IN POVERTY. CHINA FACES TREMENDOUS DOMESTIC CHALLENGES, INCLUDING A WIDENING INCOME GAP, AN AGING POPULATION, RAMPANT CORRUPTION AND A DETERIORATING ENVIRONMENT. THE UNITED STATES REMAINS FAR AHEAD OF CHINA, ESPECIALLY IN TECHNOLOGY AND INNOVATION. THE TWO ECONOMIES AND SOCIETIES ARE COMPLEMENTARY IN MANY ASPECTS. A RECENT STUDY BY THE NATIONAL COMMITTEE ON US-CHINA RELATIONS AND THE RHODIUM GROUP REVEALS THAT FROM 2000 TO 2014, CHINESE FIRMS SPENT NEARLY $46 BILLION ON NEW ESTABLISHMENTS AND ACQUISITIONS IN THE US. CHINESE-AFFILIATED COMPANIES DIRECTLY EMPLOY MORE THAN 80,000 AMERICANS. IF THE US CONTINUES TO WELCOME CHINA\'S BOOMING INVESTMENT, IT COULD RECEIVE BETWEEN $100 BILLION TO $200 BILLION FROM CHINA BY 2020, WHICH WOULD ADD BETWEEN 200,000 AND 400,000 FULL-TIME JOBS IN THE US. CHINA IS THE LARGEST TRADING PARTNER OF A GROWING NUMBER OF COUNTRIES, FROM ASIA TO AFRICA AND FROM LATIN AMERICA TO THE MIDDLE EAST. A TRADE REGIME WITHOUT CHINA\'S PARTICIPATION IS UNLIKELY TO SUCCEED. CHINA-LED NEW INITIATIVES SUCH AS THE ASIAN INFRASTRUCTURE INVESTMENT BANK (AIIB) COMPLEMENT THE WORK OF THE WORLD BANK AND ASIAN DEVELOPMENT BANK. "PIVOT" AND "NEW TYPE OF GREAT POWER RELATIONS" ARE ATTEMPTS BY THE UNITED STATES AND CHINA, RESPECTIVELY, TO HANDLE THE COMPLICATED RELATIONSHIP, BUT THEY ARE POORLY DEFINED AND LARGELY MISUNDERSTOOD BY THE OTHER SIDE. AMERICANS GENERALLY BELIEVE THAT CHINA HAS BECOME MORE ASSERTIVE IN FOREIGN POLICY AND INTENDS TO REPLACE THE US IN GLOBAL AFFAIRS. MANY CHINESE GENUINELY THINK THE UNITED STATES IS TRYING TO BLOCK CHINA\'S RISE. LACK OF TRUST HAS BEEN IDENTIFIED AS THE OUTSTANDING PROBLEM BETWEEN THE TWO COUNTRIES. BUT HOW TO BUILD TRUST? GOING FORWARD, THE TWO COUNTRIES MUST FIRST READJUST THEIR MENTALITY. FOR CHINA, THE PRIORITY REMAINS AT HOME. CHINESE LEADERS MUST RESIST THE TEMPTATION TO FLEX MUSCLES ABROAD. IT IS NOT TIME TO ABANDON DENG XIAOPING\'S DICTUM OF LYING LOW AND FOCUSING ON GROWTH. THE UNITED STATES, ON THE OTHER HAND, MUST BE REALISTIC AND REMOVE IDEOLOGICAL LENSES TO OVERCOME THE "CHINA FEAR". IT MUST ALSO REIN IN ITS SMALLER ALLIES IN ASIA SO AS TO AVOID CONFLICTS THAT WILL DRAG THE US AND CHINA INTO DIRECT CONFRONTATION. CHINA AND THE UNITED STATES ARE JOINED AT THE HIP. THERE IS NO BAD BLOOD BETWEEN THEM. THEY CANNOT AFFORD TO ALLOW HARDLINERS OR PROTECTIONISTS TO INTERFERE WITH THE GENERALLY COOPERATIVE RELATIONSHIP. DISAGREEMENT ON CERTAIN ISSUES AND OCCASIONAL QUARRELS ARE PART OF THE NORMAL LIFE IN A RELATIONSHIP. MUTUAL ACCOMMODATION AND APPRECIATION WILL ENHANCE PERSONAL RELATIONS AS WELL AS RELATIONS BETWEEN NATIONS. ZHIQUN ZHU IS A PROFESSOR OF POLITICAL SCIENCE AND INTERNATIONAL RELATIONS AT BUCKNELL UNIVERSITY IN LEWISBURG, PENNSYLVANIA. (CHINA DAILY USA 09/23/2015 PAGE12)'
    # 'nearest_neighbor_search' took 362.73 seconds and used 28.45 MB of memory.

    # 1000
    # query = 'PHOTO: JESSICA HROMAS WE ALL EXPECTED SOMEAMUSING TWEETS DURING LAST NIGHT\'SFINAL EPISODE OF THE BACHELOR AU , BUT I DOUBT ANY OF US EXPECTED MOST OF THOSE AMUSING TWEETS TO COME FROM NSW PREMIER MIKE BAIRD. AND YET, THIS IS A THING THAT HAPPENED. JUST AS THE SEASON FINALE WAS GETTING UNDERWAY, BAIRD TWEETEDTHAT HE WAS STUCK AT HOME "WITH THE MAN-FLU", AND THAT HIS DAUGHTERS HAD COMANDEERED THE TV TO FIND OUT WHETHER BACHIE SAM WOULD GIVE HIS FINAL ROSE TOSNEZANA OR LANA. BACHELOR SAM WOOD AND NEW LOVE, SNEZANA MARKOSKI. '
    # 'nearest_neighbor_search' took 1100.74 seconds and used 90.56 MB of memory.