from beacon_api.beacon_database import *


#Some hard coded data for the querys, some are taken from the beacon_dicts.py
#These will be implemented later to thake the data from a database
refname = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11','12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', 'X', 'Y']
datasetresponses = ['ALL', 'HIT', 'MISS', 'NONE']
assembliIds = ['GRCh37', 'GRCh38', 'grch37', 'grch38']
Bases = ['A', 'C', 'G', 'T', '*', 'N']
variantTypes = ['DEL', 'INS', 'DUP', 'INV', 'CNV', 'DUP:TANDEM', 'DEL:ME', 'INS:ME']
Beacon = constructor()
BeaconDataset = Beacon['dataset']
datasetIds_list = []
for dset in BeaconDataset:
    datasetIds_list.append(dset['id'])


'''The `position()` function checks the values of the position parameters (start, startMin, startMax, end, endMain, endMax)
and returns a positon list `pos` that depending on the submitted parameters, either have one, two or four items.
'''

def position(start, end, startMin, startMax, endMin, endMax):
    pos = []
    if start != 0:
        if end != 0:
            # start --> end
            pos.append(start)
            pos.append(end)
            return pos
        else:
            # only start
            pos.append(start)
            return pos
    # fuzzy bounderies
    if startMin != 0 and startMax != 0 and endMin != 0 and endMax != 0:
        pos.append(startMin)
        pos.append(startMax)
        pos.append(endMin)
        pos.append(endMax)
        return pos

'''The `allelFind()` function queries the database with the submitted parameters and checks if it finds the allele in the right place.
It returns `True` if found and `False`if not. It also returns the object to the row that was queried in the database.'''

def allelFind(chromosome, position, allel):
    q_obj = Beacon_data_table
    q_obj_chrm = q_obj.query.filter_by(chromosome=chromosome).all()   #list
    if not q_obj_chrm:
        return None, q_obj.query.filter_by(chromosome=1).all()[0] # expecting that there will allways be chromosome 1 and just returns it as dummy

    for q_chrom in q_obj_chrm:
        # only start
        if len(position) == 1:
            if q_chrom.start == position[0]:
                if q_chrom.alternate == allel:
                    return True, q_chrom
        # start --> end
        elif len(position) == 2:
            if q_chrom.start == position[0] and q_chrom.end == position[1]:
                if q_chrom.alternate == allel:
                    return True, q_chrom
        # startMin ... startMax --> endMin .. endMax
        elif len(position) == 4:
            startRange = range(position[0], position[1]+1)
            endRange = range(position[2], position[3]+1)
            if q_chrom.start in startRange and q_chrom.end in endRange:
                if q_chrom.alternate == allel:
                    return True, q_chrom


    return False, q_chrom

'''The `datasetAllelResponseBuilder()` function calls the `allelFind()` function and receives the answer to the exist parameter
and the database object to the row in the database. If `exists == False` the function sets the variant_cnt, sample_cnt,
call_cnt and frequensy to 0. And if `exists == True` the function gets the parameter values from the database.'''

def datasetAllelResponseBuilder(datasetId, referencename, pos, alternateBases):
    error = None
    j = 0
    for i in BeaconDataset:
        if datasetId in i['id']:
            break
        j += 1
    exists, queryRow = allelFind(referencename, pos, alternateBases)

    if exists == False:
        queryRow.variant_cnt, queryRow.sample_cnt, queryRow.call_cnt, queryRow.frequency = 0,0,0,0 # does not alter the database only the representation
    elif exists == None:
        queryRow.variant_cnt, queryRow.sample_cnt, queryRow.call_cnt, queryRow.frequency = 0,0,0,0 # does not alter the database only the representation
        error = 'Chromosome maching referenceName={}, not found in dataset'.format(referencename)
    datasetAllelResponse = {
        'datasetId': datasetId,
        'exists': exists,
        'frequency': queryRow.frequency,
        'variantCount': queryRow.variant_cnt,
        'callCount': queryRow.call_cnt,
        'sampleCount': queryRow.sample_cnt,
        'note': BeaconDataset[j]['description'],
        'externalUrl': BeaconDataset[j]['externalUrl'],
        'info': BeaconDataset[j]['info'],
        'error': error
    }
    return datasetAllelResponse

'''The `checkParameters()` function valiates the submitted parameters values and checks if required parameters are missing.
It calls the appropriate BeaconError method if something is wrong.'''

def checkParameters(referenceName, start, startMin, startMax, end, endMin, endMax, \
                    referenceBases, alternateBases, assemblyId, datasetIds, includeDatasetResponses, error_):
    datasetAllelResponses = []

    pos = position(start, end, startMin, startMax, endMin, endMax)

    if referenceName == '0' or start == 0 or referenceBases == '0' or alternateBases == '0' or assemblyId == '0':

        #if an error occures the 'exists' must be 'null'
        for set in datasetAllelResponses:
            set['exists'] = None
        if referenceName == '0':
            error_.bad_request('Missing manadory parameter referenceName')
        if start == 0:
            if startMin == 0:
                error_.bad_request('Missing manadory parameter start or startMin')

        if referenceBases == '0':
            error_.bad_request('Missing manadory parameter referenceBases')
        if alternateBases == '0':
            error_.bad_request('Missing manadory parameter alternateBases')
        if assemblyId == '0':
            error_.bad_request('Missing manadory parameter assemblyId')

    if start < 0:
        error_.bad_request('Start is invalid')

    if startMin < 0:
        error_.bad_request('Startmin is invalid')

    if startMax < 0:
        error_.bad_request('Startmin is invalid')

    if endMin < 0:
        error_.bad_request('Endmin is invalid')

    if endMax < 0:
        error_.bad_request('Endmax is invalid')

    if end < 0:
        error_.bad_request('End is invalid')

    if referenceName not in refname:
        #if an error occures the 'exists' must be 'null'
        for set in datasetAllelResponses:
            set['exists'] = None
        error_.bad_request('referenceName not valid')

    if includeDatasetResponses not in datasetresponses:
        # if an error occures the 'exists' must be 'null'
        for set in datasetAllelResponses:
            set['exists'] = None
        error_.bad_request('IncludeDatasetResponses not valid')

    if assemblyId not in assembliIds:
        error_.bad_request('assemblyId not valid')

    for nucleotide1 in alternateBases:
        if nucleotide1 not in Bases:
            error_.bad_request('alternateBases not valid')

    for nucleotide2 in referenceBases:
        if nucleotide2 not in Bases:
            error_.bad_request('referenceBases not valid')

    if datasetIds:
        for set in datasetIds:
            if set not in datasetIds_list:
                error_.bad_request('Invalid datasetId')
            datasetAllelResponses.append(datasetAllelResponseBuilder(set, referenceName, pos, alternateBases))
    else:
        datasetIds = None
        datasetAllelResponses = None



    false_datasetAllelResponses = []
    true_datasetAllelResponses = []

    for response in datasetAllelResponses:
        if response['exists'] == False:
            false_datasetAllelResponses.append(response)
        elif response['exists'] == True:
            true_datasetAllelResponses.append(response)



    return datasetAllelResponses, true_datasetAllelResponses, false_datasetAllelResponses, includeDatasetResponses

'''The `checkifdatasetisTrue()` function checks the individual datasets and returns `True` if any of the datasets have 
`exists == True`.'''

def checkifdatasetisTrue(datasets):
    for value in datasets:
        if value['exists'] == True:
            return True
    return False

def checkInclude(includeDatasetResponses, alldatasets, trurdatasets, falsedatasets):
    if includeDatasetResponses == 'ALL':
        return alldatasets
    elif includeDatasetResponses == 'NONE':
        return []
    elif includeDatasetResponses == 'HIT':
        return trurdatasets
    elif includeDatasetResponses == 'MISS':
        return falsedatasets
