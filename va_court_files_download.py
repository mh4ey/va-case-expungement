"""
This code downloads data from https://virginiacourtdata.org/ website
and stages the files locally in a folder for next
"""

import os
import shutil
import pandas as pd
from io import BytesIO
from urllib.request import urlopen
from tempfile import NamedTemporaryFile
from shutil import unpack_archive
from zipfile import ZipFile


# ref https://mkyong.com/python/python-how-to-list-all-files-in-a-directory/
def getFilelist(directory):
    files = []
    for root, dir_names, file_names in os.walk(directory):
        for file in file_names:
            if ".csv" in file:
                files.append(os.path.join(root, file))
    return files


def delete_file(filename):
    if os.path.isfile(filename):
        os.remove(filename)
        print(f"{filename} file removed successfully!")
    else:
        print(f"{filename} file does not exist!")


def remove_folder(path):

    # removing the folder
    if not shutil.rmtree(path):

        # success message
        print(f"{path} is removed successfully")

    else:

        # failure message
        print(f"Unable to delete the {path}")


def download_zip_file(file_urls, path):
    for zip_url_key in file_urls.keys():
        zip_file_url = file_urls[zip_url_key]
        print(f"downloading file {zip_file_url} ")
        with urlopen(zip_file_url) as zipresp:
            with ZipFile(BytesIO(zipresp.read())) as zfile:
                zfile.extractall(path)
                

circut_court_files = {
    "2020": "https://s3.amazonaws.com/virginia-court-data/circuit_criminal_2020_anon_SQYRXB.zip",
    "2019": "https://s3.amazonaws.com/virginia-court-data/circuit_criminal_2019_anon_8JMX4R.zip",
    "2018": "https://s3.amazonaws.com/virginia-court-data/circuit_criminal_2018_anon_1Y613I.zip",
    "2017": "https://s3.amazonaws.com/virginia-court-data/circuit_criminal_2017_anon_B9BUKQ.zip",
    "2016": "https://s3.amazonaws.com/virginia-court-data/circuit_criminal_2016_anon_HMVIZY.zip",
    "2015": "https://s3.amazonaws.com/virginia-court-data/circuit_criminal_2015_anon_1WMI7Q.zip",
    "2014": "https://s3.amazonaws.com/virginia-court-data/circuit_criminal_2014_anon_P2L0Y4.zip",
    "2013": "https://s3.amazonaws.com/virginia-court-data/circuit_criminal_2013_anon_1FOA9N.zip",
    "2012": "https://s3.amazonaws.com/virginia-court-data/circuit_criminal_2012_anon_Y6DBO7.zip",
    "2011": "https://s3.amazonaws.com/virginia-court-data/circuit_criminal_2011_anon_P928SU.zip",
    #"2010": "https://s3.amazonaws.com/virginia-court-data/circuit_criminal_2010_anon_LK0BM4.zip",
    #"2009": "https://s3.amazonaws.com/virginia-court-data/circuit_criminal_2009_anon_TIBLMH.zip",
}


district_court_files = {
    "2020": "https://s3.amazonaws.com/virginia-court-data/district_criminal_2020_anon_PFP3JS.zip",
    "2019": "https://s3.amazonaws.com/virginia-court-data/district_criminal_2019_anon_I24Z9B.zip",
    "2018": "https://s3.amazonaws.com/virginia-court-data/district_criminal_2018_anon_S72VOG.zip",
    "2017": "https://s3.amazonaws.com/virginia-court-data/district_criminal_2017_anon_QCO2KE.zip",
    "2016": "https://s3.amazonaws.com/virginia-court-data/district_criminal_2016_anon_C4703U.zip",
    "2015": "https://s3.amazonaws.com/virginia-court-data/district_criminal_2015_anon_WZ57WS.zip",
    "2014": "https://s3.amazonaws.com/virginia-court-data/district_criminal_2014_anon_5IDVZ7.zip",
    "2013": "https://s3.amazonaws.com/virginia-court-data/district_criminal_2013_anon_5IBSOL.zip",
    "2012": "https://s3.amazonaws.com/virginia-court-data/district_criminal_2012_anon_F6G5KD.zip",
    "2011": "https://s3.amazonaws.com/virginia-court-data/district_criminal_2011_anon_1JEKQB.zip",
    
}



# collections.namedtuple to construct a simple class to represent individual cards.

va_court_files = {"circuit": circut_court_files, "district": district_court_files}


def cleanup(dir_path):
    print(f"Deleting downloaded files from {dir_path}")
    files = glob.glob(dir_path +'/*.csv', recursive=True)
    for f in files:
        try:
            os.remove(f)
        except OSError as e:
            print("Error: %s : %s" % (dir_path, e.strerror))
    try:
        print(f"\nDeleting file download staging directory {dir_path}")
        os.rmdir(dir_path)
    except OSError as e:
        print("Error: %s : %s" % (dir_path, e.strerror))

def download_va_court_files(court_type):

    court_files = va_court_files[court_type]

    # BASE_DIR and DOWNLOAD_DATA are setup from setup.py
    # staging directory for downloads
    stage_dir = DOWNLOAD_DATA + court_type

    path = os.path.join(stage_dir)
    print(f"{court_type} court file download path : {path}")

    # remove existing files
    try:
        remove_folder(path)
    except FileNotFoundError:
        print(f"directory does not exist")

    # creating staging folder
    os.makedirs(path)
    print(f"download directory {path} created")

    # download the files
    print(f"start {court_type} court files download...")
    download_zip_file(court_files, path)
    print(f"{court_type} court files download is complete...")


def download_and_merge_court_data(court_type):

    # creating staging folder
    try:
        os.makedirs(PROCESSED_PATH)
        print(f"data directory: {PROCESSED_PATH} created")

    except FileExistsError:
        print("data directory already existis, files will be deleted")

    if court_type == "circuit":

        # remove existing files
        delete_file(PROCESSED_PATH + CIRCUIT_CT_FILENAME)

        # download circuit court files
        download_va_court_files(court_type)

        # Load Circuit Court data
        circuit_column_mapping = {
            "person_id": "person_id",
            "OffenseDate": "offense_date",
            "DispositionCode": "final_disposition",
            "fips": "fips",
            "Sex": "gender",
            "Race": "race",
            "Class": "class",
            "ChargeType": "charge_type",
            "AmendedChargeType": "ammended_charge_type"
        }

        # select new columns that are not mapped to None
        circuit_columns = [
            c
            for c in circuit_column_mapping.keys()
            if circuit_column_mapping[c] != None
        ]

        # Load all circuit court files into dataframe, concat dataframes and save the merged dataset as csv file
        circuit_ct_files = getFilelist(CIRCUIT_CT_PATH)
        print(f"Number of Circuit Court files: {len(circuit_ct_files)}")

        circuit_ct_df_list = []
        for filename in circuit_ct_files:
            circuit_ct_df_list.append(
                pd.read_csv(filename, parse_dates=["HearingDate"])
            )

        circuit_df = pd.concat(circuit_ct_df_list)

        circuit_df = circuit_df[circuit_columns].rename(columns=circuit_column_mapping)

        circuit_df.to_csv(
            PROCESSED_PATH + "circuit_court_2011_2020.csv.gz",
            index=False,
            compression="gzip",
            header=True,
            quotechar='"',
            doublequote=True,
            line_terminator="\n",
        )
    elif court_type == "district":
        # remove existing files
        delete_file(PROCESSED_PATH + DISTRICT_CT_FILENAME)

        # download circuit court files
        download_va_court_files(court_type)

        district_column_mapping = {
            "person_id": "person_id",
            "OffenseDate": "offense_date",
            "FinalDisposition": "final_disposition",
            "fips": "fips",
            "Gender": "gender",
            "Race": "race",
            "Class": "class",
            "CaseType": "charge_type",
            "AmendedCharge": "ammended_charge_type"
            
        }

        # select new columns that are not mapped to None
        district_columns = [
            c
            for c in district_column_mapping.keys()
            if district_column_mapping[c] != None
        ]

        # Load all circuit court files into dataframe, concat dataframes and save the merged dataset as csv file
        district_ct_files = getFilelist(DISTRICT_CT_PATH)
        print(f"Number of District Court files: {len(district_ct_files)}")

        district_ct_df_list = []
        for filename in district_ct_files:
            district_ct_df_list.append(
                pd.read_csv(filename, parse_dates=["HearingDate"])
            )

        district_df = pd.concat(district_ct_df_list)

        district_df = district_df[district_columns].rename(
            columns=district_column_mapping
        )

        district_df.to_csv(
            PROCESSED_PATH + "district_court_2011_2020.csv.gz",
            index=False,
            compression="gzip",
            header=True,
            quotechar='"',
            doublequote=True,
            line_terminator="\n",
        )
    else:
        print(f"Invalid court type, please use 'circuit or 'district' as input")
    stage_dir = DOWNLOAD_DATA + court_type
    cleanup(stage_dir)

print("VA file download script loaded!")
