import sys
import re
import datetime
from sets import Set
import numpy as np
from collections import namedtuple

def main():

    #field name and index from FEC data dictionary
    data_dict = {
      "CMTE_ID": 0,
      "AMNDT_IND": 1,
      "RPT_TP": 2,
      "TRANSACTION_PGI": 3,
      "IMAGE_NUM": 4,
      "TRANSACTION_TP":5,
      "ENTITY_TP":6,
      "NAME":7,
      "CITY":8,
      "STATE":9,
      "ZIP_CODE":10,
      "EMPLOYER":11,
      "OCCUPATION":12,
      "TRANSACTION_DT":13,
      "TRANSACTION_AMT":14,
      "OTHER_ID":15,
      "TRAN_ID":16,
      "FILE_NUM":17,
      "MEMO_CD":18,
      "MEMO_TEXT":19,
      "SUB_ID":20
    }

    #data structures used
    transaction_history = {}
    donor_history = Set([])
    most_current_cal_year = {}

    output_file = open('./output/repeat_donors.txt', 'w')
    percentile_file = open('./input/percentile.txt', 'r')
    itcont = open('./input/itcont.txt', 'r')
    percentile_calc = int(percentile_file.readline())

    #read as if from stream
    for line in itcont:
        new_donor = re.split("\|", line)

        #validate record
        if is_valid_record(data_dict, new_donor) == False:
            print ("failed", new_donor[data_dict.get("NAME")])
            continue

        print ("success", new_donor[data_dict.get("NAME")])
        #clean record
        new_donor = get_first_five_digits_zip_code(data_dict, new_donor)
        new_donor = to_datetime_object(data_dict, new_donor)
        new_donor_id = create_unique_donor_id(data_dict, new_donor)

        # get information needed from record
        recipient = new_donor[data_dict.get("CMTE_ID")]
        zip_code = new_donor[data_dict.get("ZIP_CODE")]
        year = new_donor[data_dict.get("TRANSACTION_DT")]
        donation_amount = new_donor[data_dict.get("TRANSACTION_AMT")]

        if recipient not in most_current_cal_year:
            most_current_cal_year[recipient] = year

        # check if repeat donor
        if new_donor_id in donor_history:
            #check if year is most current
            if year >= most_current_cal_year[recipient]:


                most_current_cal_year[recipient] = year

                record_key = namedtuple('record_key', 'CMTE_ID ZIP_CODE')
                temp_key = record_key(CMTE_ID=recipient, ZIP_CODE =zip_code)

                year_dict = transaction_history[temp_key]

                if year not in year_dict:
                    year_dict[year] = [int(donation_amount)]
                    percentile = np.percentile(year_dict[year], percentile_calc, interpolation="nearest")
                    output_file.write(recipient + "|" + zip_code + "|" + str(year) + "|" + str(percentile) + "|" + str(donation_amount) + "|" + str(1) +"\n")
                else:
                    year_dict[year].append(int(donation_amount))
                    amt_trans = len(year_dict[year])
                    percentile = np.percentile(year_dict[year], percentile_calc, interpolation="nearest")
                    output_file.write(recipient + "|" + zip_code + "|" + str(year) + "|" + str(percentile) + "|" + str(sum(year_dict[year])) + "|" + str(amt_trans)+"\n")
            else:
                create_new_record(recipient, zip_code, donation_amount, year, transaction_history)
        else:
            print("added as new user:", new_donor_id)
            donor_history.add(new_donor_id)
            create_new_record(recipient, zip_code, donation_amount, year, transaction_history)

    percentile_file.close()
    itcont.close()
    output_file.close()

def create_new_record(recipient, zip_code, donation_amount, year, transaction_history):
    record_key = namedtuple('record_key', 'CMTE_ID ZIP_CODE')
    new_key = record_key(CMTE_ID=recipient, ZIP_CODE =zip_code)
    new_value = {}

    val = [int(donation_amount)]
    new_value[year] = val
    transaction_history[new_key] = new_value


def create_unique_donor_id(data_dict, arr):
    donor_name = arr[data_dict.get("NAME")]
    donor_name = re.sub(r'\s+', '', donor_name)
    donor_name = re.sub(r',', '', donor_name)
    donor_zip_code = arr[data_dict.get("ZIP_CODE")]
    donor_id = donor_name + donor_zip_code
    return donor_id


def to_datetime_object(data_dict, arr):
    date = arr[data_dict.get("TRANSACTION_DT")]
    date_object = datetime.datetime.strptime(date, '%m%d%Y')
    arr[data_dict.get("TRANSACTION_DT")] = date_object.year
    return arr

def get_first_five_digits_zip_code(data_dict, arr):
    zip_code = str(arr[data_dict.get("ZIP_CODE")])
    arr[data_dict.get("ZIP_CODE")]= zip_code[:5]
    return arr

def append_new_row(df, data_dict, impt_fields, arr):
    new_row = pd.DataFrame([create_new_row(data_dict, impt_fields, arr)], columns=impt_fields)
    df = df.append(new_row, ignore_index=True)
    return df

def get_repeat_donors(df):

    current_year = df["TRANSACTION_DT"].max()
    return True

def get_percentiles(df):
    return True

def create_new_row(data_dict, impt_fields, arr):
    new_row = []
    for i in range(0, len(impt_fields)):
        new_row.append(arr[data_dict.get(impt_fields[i])])
    return new_row

def get_index(data_dict, field):
    if field in data_dict:
        return data_dict.get(field)
    else:
        return -1

def field_is_empty(data_dict, arr, field):
    index  = get_index(data_dict, field)
    if index == -1:
        return True
    if index >= len(arr):
        return True
    if arr[index] == '':
        return True
    return False

def is_valid_OTHER_ID(data_dict, arr):
    return field_is_empty(data_dict, arr, "OTHER_ID")

def is_valid_TRANSACTION_DT(data_dict, arr):
    if field_is_empty(data_dict, arr, "TRANSACTION_DT"):
        return False

    if len(str(arr[data_dict.get("TRANSACTION_DT")])) != 8:
        return False

    try:
        index = get_index(data_dict, "TRANSACTION_DT")
        DT = arr[index]
        is_valid_datetime = datetime.datetime(int(DT[4:]),int(DT[:2]), int(DT[2:4]))
        return True

    except ValueError:
        return False

def is_valid_ZIP_CODE(data_dict, arr):
    if field_is_empty(data_dict, arr, "ZIP_CODE"):
        return False
    zip_code = arr[get_index(data_dict, "ZIP_CODE")]
    if len(zip_code) < 5:
        return False
    return zip_code.isdigit()

def is_valid_NAME(data_dict, arr):
    if field_is_empty(data_dict, arr, "NAME"):
        return False
    return bool(re.match(r"^[a-zA-Z, ]+$", arr[get_index(data_dict, "NAME")]))

def is_valid_CMTE_ID(data_dict, arr):
    return not field_is_empty(data_dict, arr, "CMTE_ID")

def is_valid_TRANSACTION_AMT(data_dict, arr):
    return not field_is_empty(data_dict, arr, "TRANSACTION_AMT")

def is_valid_record(data_dict, arr):
    return (is_valid_CMTE_ID(data_dict, arr)
            and is_valid_NAME(data_dict, arr)
            and is_valid_ZIP_CODE(data_dict, arr)
            and is_valid_TRANSACTION_DT(data_dict, arr)
            and is_valid_TRANSACTION_AMT(data_dict, arr)
            and is_valid_OTHER_ID(data_dict, arr)
           )

main()
