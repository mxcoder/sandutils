import logging
import sys
from os import path

import numpy as np
import pandas as pd


def preview_df(df):
    logging.debug(df.attrs["name"])
    logging.debug(df.head(5).to_markdown())


def main(f_gsm, f_lte, f_umts):
    gsm_index = "BTSNAME"
    gsm_suffix = "_gsm"
    original_gsm_df = pd.read_csv(f_gsm, usecols=["BSCNAME","BTSNAME","CELLNAME(*)","MCC","MNC","LAC(*)","CI(*)","ISMOCN","OPERATOR","VENDOR"])
    original_gsm_df.drop_duplicates(inplace=True)
    original_gsm_df.set_index(gsm_index, drop=False, inplace=True)

    lte_index = "ENODEBNAME"
    lte_suffix = "_lte"
    original_lte_df = pd.read_csv(f_lte, usecols=["ENODEBNAME","CELLNAME(*)","MCC","MNC","ENODEBID","LOCALCELLID","TAC","CELLID","PCI"])
    original_lte_df.drop_duplicates(inplace=True)
    original_lte_df.set_index(lte_index, drop=False, inplace=True)

    umts_index = "NODEBNAME"
    umts_suffix = "_umts"
    original_umts_df = pd.read_csv(f_umts, usecols=["RNCNAME","NODEBNAME","CELLNAME(*)","MCC","MNC","RNCID(*)","LAC","CI(*)","ISMOCN","OPERATOR","VENDOR"])
    original_umts_df.drop_duplicates(inplace=True)
    original_umts_df.set_index(umts_index, drop=False, inplace=True)

    sheets = []

    # GSM to UMTS
    gsm_umts = pd.merge(original_gsm_df, original_umts_df, how="left", left_index=True, right_index=True, suffixes=(gsm_suffix, umts_suffix))
    gsm_umts.attrs["name"] = "GSM-UMTS"
    preview_df(gsm_umts)
    sheets.append(gsm_umts)

    # UMTS to GSM
    umts_gsm_df = pd.merge(original_umts_df, original_gsm_df, how="left", left_index=True, right_index=True, suffixes=(umts_suffix, gsm_suffix))
    umts_gsm_df.attrs["name"] = "UMTS-GSM"
    preview_df(umts_gsm_df)
    sheets.append(umts_gsm_df)

    # LTE to UMTS
    lte_umts_df = pd.merge(original_lte_df, original_umts_df, how="left", left_index=True, right_index=True, suffixes=(lte_suffix, umts_suffix))
    lte_umts_df.attrs["name"] = "LTE-UMTS"
    preview_df(lte_umts_df)
    sheets.append(lte_umts_df)

    # UMTS to LTE
    umts_lte_df = pd.merge(original_umts_df, original_lte_df, how="left", left_index=True, right_index=True, suffixes=(umts_suffix, lte_suffix))
    umts_lte_df.attrs["name"] = "UMTS-LTE"
    preview_df(umts_lte_df)
    sheets.append(umts_lte_df)

    # LTE to GSM
    lte_gsm_df = pd.merge(original_lte_df, original_gsm_df, how="left", left_index=True, right_index=True, suffixes=(lte_suffix, gsm_suffix))
    lte_gsm_df.attrs["name"] = "LTE-GSM"
    preview_df(lte_gsm_df)
    sheets.append(lte_gsm_df)

    # GSM to LTE
    gsm_lte_df = pd.merge(original_gsm_df, original_lte_df, how="left", left_index=True, right_index=True, suffixes=(gsm_suffix, lte_suffix))
    gsm_lte_df.attrs["name"] = "GSM-LTE"
    preview_df(gsm_lte_df)
    sheets.append(gsm_lte_df)

    return sheets


def writeBook(sheets, filename_or_stream):
    # https://github.com/PyCQA/pylint/issues/3060 pylint: disable=abstract-class-instantiated
    writer = pd.ExcelWriter(filename_or_stream, engine="xlwt")
    for sheet in sheets:
        sheet.to_excel(writer, sheet_name=sheet.attrs["name"], index=False, encoding="UTF-8")
    writer.save()


if __name__ == "__main__":
    if not len(sys.argv) == 4:
        print("Invalid arguments: filename\nUsage: main.py [gsm.csv] [lte.csv] [umts.csv]")
        exit(1)

    umts_filename = sys.argv.pop()
    lte_filename = sys.argv.pop()
    gsm_filename = sys.argv.pop()

    if not path.exists(gsm_filename):
        print(f"Can't find filename: {gsm_filename}")
        exit(1)
    if not path.exists(lte_filename):
        print(f"Can't find filename: {lte_filename}")
        exit(1)
    if not path.exists(umts_filename):
        print(f"Can't find filename: {umts_filename}")
        exit(1)

    try:
        print("Matching neighbour cells on files")

        gsm_file = open(gsm_filename, "r")
        lte_file = open(lte_filename, "r")
        umts_file = open(umts_filename, "r")

        sheets = main(gsm_file, lte_file, umts_file)
        writeBook(sheets, "output.xls")
        # for sheet in sheets:
        #     sheet.to_csv(f'matched_{sheet.attrs["name"]}.csv', index=False, encoding="UTF-8")

        print("Exported sheets as book: output.xls")

    except Exception:
        logging.exception("Error while matching")
