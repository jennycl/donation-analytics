# Donation Analytics

This is the donation-analytics challenge for the Insight Data Science challenge.

## Prerequisites

Python 2.7.13

Numpy

### Installing

Install Numpy:
```
python -m pip install --user numpy
```
## Running donation-analytics.py

1. Make sure Numpy is installed:
```
python -m pip install --user numpy
```
2. Run script
```
./run.sh
```
## Running tests

Go to insight_testsuite, run:

```
./run_tests.sh
```
## Data structure and methods used

A set is used to determine if a donor is a repeat donor.

The data/records is stored as a dictionary of dictionaries.

A tuple (CMTE_ID, ZIP_CODE) is used as keys and the values is a dictionary using year as the key and a list of the amounts as the value:

```
{ (CMTE_ID, ZIP_CODE) : { YEAR: [TRANSACTION_AMT]} }

Example:

{ (C00177436, 02895) : { 2018: [250, 333, 384],
                        2016: [130, 200, 250],
                        2017: [300, 200, 230]  } ,

 (C00384516, 02816) : { 2018: [150, 300, 244],
                        2016: [120],
                        2017: [300, 200]  }
}
```

Numpy is used to calculate nearest-rank percentiles.

Percentiles are calculated using Numpy's Percentile method, input being the list of transaction amounts for a certain year.

Total amounts donated are calculated by summing up the list of transaction amounts for a certain year.

## Run-through of the steps in main()

Data is taken in line by line (like a stream).
The record is checked for validity, making sure to ignore any records that has invalid fields.
Once we have the fields we need, we go through the following logic to update the data structure and give output:

```
if the donor (identified by a unique donor id of name and zipcode) is a repeat donor AND if the year in the record is the most recent calendar year:
    Calculate percentile using Numpy's Percentile method
    Calculate the total number of transactions by counting the number of entries of the list of amounts
    Calculate the total amount donated by adding the entries of the list of amounts
    Output CMTE_ID, ZIP, Year, percentile, total, and total amount donated
else:
    Add record to data structure but do not output

```

## Authors
* ** Jenny Liang **

## Questions

Please email jenny.liang@nyu.edu
