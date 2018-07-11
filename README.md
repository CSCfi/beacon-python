# beacon-python


## Preparing datasets and adding them to the database
Adding line numbering to the files. The numbering must be continuous, thats why NR+72 because the first dataset has 72 rows

```
$ awk '{printf "%s;%s\n", NR,$0}' dataset1.csv > dataset1_.csv
$ awk '{printf "%s;%s\n", NR+72,$0}' dataset2.csv > dataset2_.csv
$ awk '{printf "%s;%s\n", NR+161,$0}' dataset3.csv > dataset3_.csv
```

In the python shell we create the tables with SQLAlchemy. (If you create them separately some of the functions won't work.)

```python
>>>from beacon_api.beacon_database import db, load_dataset_table
>>>db.create_all()
```

Then we fill the table "genomes" with the datasets.

```
$ sqlite3 beaconDatabase.db
sqlite> .separator ";"
sqlite> .import set1.csv genomes
sqlite> .import set2.csv genomes
sqlite> .import set3.csv genomes
```
Then we check for the right values to fill in the beacon_dataset_table, variantCount and callCount.

```
$ awk -F ';' '{SUM+=$10}END{print SUM}' set1.csv			(variantCount=6966)
$ awk -F ';' '{SUM+=$11}END{print SUM}' set1.csv			(callCount=360576)
$ 
$ awk -F ';' '{SUM+=$10}END{print SUM}' set2.csv			(variantCount=16023)
$ awk -F ';' '{SUM+=$11}END{print SUM}' set2.csv			(callCount=445712)
$ 
$ awk -F ';' '{SUM+=$10}END{print SUM}' set3.csv			(variantCount=20952)
$ awk -F ';' '{SUM+=$11}END{print SUM}' set3.csv			(callCount=1206928)
```

Lastly we fill the beacon_dataset_table with meata data in the python shell.

```python
>>>load_dataset_table(‘DATASET1’, ‘example dataset number 1’, 'GRCh38', 'v1', 6966, 360576, 1, 'externalUrl', 'PUBLIC', 'authorised')
>>>load_dataset_table(‘DATASET2’, ‘example dataset number 2’, 'GRCh38', 'v1', 16023, 445712, 1, 'externalUrl', 'PUBLIC', 'authorised')
>>>load_dataset_table(‘DATASET3’, ‘example dataset number 3’, 'GRCh38', 'v1', 20952, 1206928, 1, 'externalUrl', 'PUBLIC', 'authorised')

```
