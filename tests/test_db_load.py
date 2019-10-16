import unittest
import asynctest
import asyncio
from testfixtures import TempDirectory
from beacon_api.utils.db_load import BeaconDB


class Variant:
    """Variant Class.

    Mock this for Variant calculations.
    """

    def __init__(self, ALT, REF, INF, call_rate, var_type, num_called, is_sv=False):
        """Initialize class."""
        self.INFO = INF
        self.ALT = ALT
        self.REF = REF
        self.call_rate = call_rate
        self.var_type = var_type
        self.num_called = num_called
        self.is_sv = is_sv


class INFO:
    """INFO CLass.

    Mock this for storing VCF info.
    """

    def __init__(self, AC, VT, AN, AF, SVTYPE=None):
        """Initialize class."""
        self.AC = AC
        self.VT = VT
        self.AN = AN
        self.AF = AF
        self.SVTYPE = SVTYPE

    def get(self, key):
        """Inside `__getitem__` method."""
        return getattr(self, key)


class Transaction:
    """Class Transaction.

    Mock this from asyncpg.
    """

    def __init__(self, *args, **kwargs):
        """Initialize class."""
        pass

    async def __aenter__(self):
        """Initialize class."""
        pass

    async def __aexit__(self, *args):
        """Initialize class."""
        pass


class Statement(Transaction):
    """Class Transaction.

    Mock this from asyncpg.
    """

    def __init__(self, query, accessData):
        """Initialize class."""
        self.accessData = accessData
        pass

    async def fetch(self, *args, **kwargs):
        """Mimic fetch."""
        if self.accessData:
            return self.accessData
        else:
            return []


class Connection:
    """Class Connection.

    Mock this from asyncpg.
    """

    def __init__(self, accessData=None):
        """Initialize class."""
        self.accessData = accessData
        pass

    async def fetch(self, *args, **kwargs):
        """Mimic fetch."""
        return [{"table_name": "DATATSET1"}, {"table_name": "DATATSET2"}]

    async def execute(self, query, *args):
        """Mimic execute."""
        return []

    async def close(self):
        """Mimic close."""
        pass

    async def __aenter__(self):
        """Initialize class."""
        pass

    async def __aexit__(self, *args):
        """Initialize class."""
        pass

    @asyncio.coroutine
    def prepare(self, query):
        """Mimic prepare."""
        return Statement(query, self.accessData)

    def transaction(self, *args, **kwargs):
        """Mimic transaction."""
        return Transaction(*args, **kwargs)


class ConnectionException:
    """Class Connection with Exception.

    Mock this from asyncpg.
    """

    def __init__(self):
        """Initialize class."""
        pass

    def transaction(self, *args, **kwargs):
        """Mimic transaction."""
        return Transaction(*args, **kwargs)

    async def execute(self, query, *args):
        """Mimic execute."""
        return Exception

    @asyncio.coroutine
    def prepare(self, query):
        """Mimic prepare."""
        return Exception


class DatabaseTestCase(asynctest.TestCase):
    """Test database operations."""

    def setUp(self):
        """Initialise BeaconDB object."""
        self._db = BeaconDB()
        self._dir = TempDirectory()
        self.data = """##fileformat=VCFv4.0
        ##fileDate=20090805
        ##source=myImputationProgramV3.1
        ##reference=1000GenomesPilot-NCBI36
        ##phasing=partial
        ##INFO=<ID=NS,Number=1,Type=Integer,Description="Number of Samples With Data">
        ##INFO=<ID=AN,Number=1,Type=Integer,Description="Total number of alleles in called genotypes">
        ##INFO=<ID=AC,Number=.,Type=Integer,Description="Allele count in genotypes, for each ALT allele, in the same order as listed">
        ##INFO=<ID=DP,Number=1,Type=Integer,Description="Total Depth">
        ##INFO=<ID=AF,Number=.,Type=Float,Description="Allele Frequency">
        ##INFO=<ID=AA,Number=1,Type=String,Description="Ancestral Allele">
        ##INFO=<ID=DB,Number=0,Type=Flag,Description="dbSNP membership, build 129">
        ##INFO=<ID=H2,Number=0,Type=Flag,Description="HapMap2 membership">
        ##FILTER=<ID=q10,Description="Quality below 10">
        ##FILTER=<ID=s50,Description="Less than 50% of samples have data">
        ##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">
        ##FORMAT=<ID=GQ,Number=1,Type=Integer,Description="Genotype Quality">
        ##FORMAT=<ID=DP,Number=1,Type=Integer,Description="Read Depth">
        ##FORMAT=<ID=HQ,Number=2,Type=Integer,Description="Haplotype Quality">
        ##ALT=<ID=DEL:ME:ALU,Description="Deletion of ALU element">
        ##ALT=<ID=CNV,Description="Copy number variable region">
        #CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT	NA00001	NA00002	NA00003
        19	111	.	A	C	9.6	.	.	GT:HQ	0|0:10,10	0|0:10,10	0/1:3,3
        19	112	.	A	G	10	.	.	GT:HQ	0|0:10,10	0|0:10,10	0/1:3,3
        20	14370	rs6054257	G	A	29	PASS	NS=3;DP=14;AF=0.5;DB;H2	GT:GQ:DP:HQ	0|0:48:1:51,51	1|0:48:8:51,51	1/1:43:5:.,.
        chrM 15011 . T C . PASS . GT:GQ:DP:RO:QR:AO:QA:GL 1:160:970:0:0:968:31792:-2860.58,0 1:160:970:0:0:968:31792:-2860.58,0"""
        self.datafile = self._dir.write('data.csv', self.data.encode('utf-8'))

    def tearDown(self):
        """Close database connection after tests."""
        self._dir.cleanup_all()

    @asynctest.mock.patch('beacon_api.utils.db_load.asyncpg.connect')
    async def test_rchop(self, db_mock):
        """Test rchop for SVTYPE."""
        db_mock.return_value = Connection()
        await self._db.connection()
        result = self._db._rchop('INS:ME:LINE1', ":LINE1")
        self.assertEqual('INS:ME', result)
        result_no_ending = self._db._rchop('INS', ":LINE1")
        self.assertEqual('INS', result_no_ending)

    @asynctest.mock.patch('beacon_api.utils.db_load.asyncpg.connect')
    async def test_handle_type(self, db_mock):
        """Test handle type."""
        db_mock.return_value = Connection()
        await self._db.connection()
        result = self._db._handle_type(1, int)
        self.assertEqual([1], result)
        result_tuple = self._db._handle_type((0.1, 0.2), float)
        self.assertEqual([0.1, 0.2], result_tuple)

    @asynctest.mock.patch('beacon_api.utils.db_load.asyncpg.connect')
    async def test_bnd_parts(self, db_mock):
        """Test breakend parsing parts."""
        db_mock.return_value = Connection()
        await self._db.connection()
        result = self._db._bnd_parts('[CHR17:31356925[N', '126_2')
        self.assertEqual(('chr17', 31356925, True, True, 'N', True, '126_2'), result)

    @asynctest.mock.patch('beacon_api.utils.db_load.asyncpg')
    async def test_connection(self, db_mock):
        """Test database URL fetching."""
        await self._db.connection()
        db_mock.connect.assert_called()

    @asynctest.mock.patch('beacon_api.utils.db_load.asyncpg.connect')
    async def test_check_tables(self, db_mock):
        """Test checking tables."""
        db_mock.return_value = Connection()
        await self._db.connection()
        db_mock.assert_called()
        result = await self._db.check_tables(['DATATSET1', 'DATATSET2'])
        # No Missing tables
        assert result == []

    @asynctest.mock.patch('beacon_api.utils.db_load.LOG')
    @asynctest.mock.patch('beacon_api.utils.db_load.asyncpg.connect')
    async def test_create_tables(self, db_mock, mock_log):
        """Test creating tables."""
        sql = """CREATE TABLE IF NOT EXISTS beacon_data_table (
            id SERIAL,
            dataset_id VARCHAR(200),
            PRIMARY KEY (id));"""
        db_mock.return_value = Connection()
        await self._db.connection()
        db_mock.assert_called()
        sql_file = self._dir.write('sql.init', sql.encode('utf-8'))
        await self._db.create_tables(sql_file)
        # Should assert logs
        mock_log.info.assert_called_with('Tables have been created')

    @asynctest.mock.patch('beacon_api.utils.db_load.LOG')
    @asynctest.mock.patch('beacon_api.utils.db_load.asyncpg.connect')
    async def test_create_tables_exception(self, db_mock, mock_log):
        """Test creating tables exception."""
        db_mock.return_value = ConnectionException()
        await self._db.connection()
        await self._db.create_tables('sql.init')
        log = "AN ERROR OCCURRED WHILE ATTEMPTING TO CREATE TABLES -> [Errno 2] No such file or directory: 'sql.init'"
        mock_log.error.assert_called_with(log)

    @asynctest.mock.patch('beacon_api.utils.db_load.LOG')
    @asynctest.mock.patch('beacon_api.utils.db_load.asyncpg.connect')
    @asynctest.mock.patch('beacon_api.utils.db_load.VCF')
    async def test_load_metadata(self, mock_vcf, db_mock, mock_log):
        """Test load metadata."""
        metadata = """{"name": "ALL.chrMT.phase3_callmom-v0_4.20130502.genotypes.vcf",
            "datasetId": "urn:hg:exampleid",
            "description": "Mitochondrial genome from the 1000 Genomes project",
            "assemblyId": "GRCh38",
            "createDateTime": "2013-05-02 12:00:00",
            "updateDateTime": "2013-05-02 12:00:00",
            "version": "v0.4",
            "externalUrl": "smth",
            "accessType": "PUBLIC"}"""
        db_mock.return_value = Connection()
        await self._db.connection()
        db_mock.assert_called()
        metafile = self._dir.write('data.json', metadata.encode('utf-8'))
        vcf = asynctest.mock.MagicMock(name='samples')
        vcf.samples.return_value = [1, 2, 3]
        await self._db.load_metadata(vcf, metafile, self.datafile)
        # Should assert logs
        mock_log.info.mock_calls = [f'Parsing metadata from {metafile}',
                                    'Metadata has been parsed']

    @asynctest.mock.patch('beacon_api.utils.db_load.LOG')
    @asynctest.mock.patch('beacon_api.utils.db_load.asyncpg.connect')
    async def test_load_metadata_exception(self, db_mock, mock_log):
        """Test load metadata error."""
        db_mock.return_value = ConnectionException()
        await self._db.connection()
        vcf = asynctest.mock.MagicMock(name='samples')
        vcf.samples.return_value = [1, 2, 3]
        await self._db.load_metadata(vcf, 'meta.are', 'datafile')
        log = "AN ERROR OCCURRED WHILE ATTEMPTING TO PARSE METADATA -> [Errno 2] No such file or directory: 'meta.are'"
        mock_log.error.assert_called_with(log)

    @asynctest.mock.patch('beacon_api.utils.db_load.LOG')
    @asynctest.mock.patch('beacon_api.utils.db_load.asyncpg.connect')
    async def test_load_datafile(self, db_mock, mock_log):
        """Test load_datafile."""
        db_mock.return_value = Connection()
        vcf = asynctest.mock.MagicMock(name='samples')
        vcf.return_value = [{'record': 1}, {'record': 2}, {'records': 3}]
        vcf.samples.return_value = [{'record': 1}, {'record': 2}, {'records': 3}]
        await self._db.connection()
        db_mock.assert_called()
        await self._db.load_datafile(vcf, self.datafile, 'DATASET1')
        # Should assert logs
        mock_log.info.mock_calls = [f'Read data from {self.datafile}',
                                    f'{self.datafile} has been processed']

    @asynctest.mock.patch('beacon_api.utils.db_load.LOG')
    @asynctest.mock.patch('beacon_api.utils.db_load.asyncpg.connect')
    async def test_insert_variants(self, db_mock, mock_log):
        """Test load_datafile."""
        db_mock.return_value = Connection()
        await self._db.connection()
        db_mock.assert_called()
        await self._db.insert_variants('DATASET1', ['C'])
        # Should assert logs
        mock_log.info.mock_calls = [f'Received 1 variants for insertion to DATASET1',
                                    'Insert variants into the database']

    @asynctest.mock.patch('beacon_api.utils.db_load.LOG')
    @asynctest.mock.patch('beacon_api.utils.db_load.asyncpg.connect')
    async def test_close(self, db_mock, mock_log):
        """Test database URL close."""
        db_mock.return_value = Connection()
        await self._db.connection()
        await self._db.close()
        mock_log.info.mock_calls = ['Mark the database connection to be closed',
                                    'The database connection has been closed']

    @asynctest.mock.patch('beacon_api.utils.db_load.LOG')
    @asynctest.mock.patch('beacon_api.utils.db_load.asyncpg.connect')
    async def test_unpack(self, db_mock, mock_log):
        """Test database URL fetching."""
        db_mock.return_value = Connection()
        await self._db.connection()
        inf1 = INFO((1), 'i', 3, None)
        variant_1 = Variant(['C'], 'T', inf1, 0.7, 'indel', 3)
        result = self._db._unpack(variant_1)
        self.assertEqual(([0.3333333333333333], [1], ['SNP'], ['C'], 3, []), result)
        inf2 = INFO(1, 'M', 3, None)
        variant_2 = Variant(['AT', 'A'], 'ATA', inf2, 0.7, 'mnp', 3)
        result = self._db._unpack(variant_2)
        self.assertEqual(([0.3333333333333333], [1], ['DEL', 'DEL'], ['AT', 'A'], 3, []), result)
        inf3 = INFO((1), 'S', 3, 0.5)
        variant_3 = Variant(['TC'], 'T', inf3, 0.7, 'snp', 3)
        result = self._db._unpack(variant_3)
        self.assertEqual(([0.5], [1], ['INS'], ['TC'], 3, []), result)
        inf4 = INFO((1), '<INS:ME>', 3, None, 'BND')
        variant_4 = Variant(['TC'], 'T', inf4, 0.7, 'snp', 3)
        result = self._db._unpack(variant_4)
        self.assertEqual(([0.3333333333333333], [1], ['SNP'], ['TC'], 3, []), result)
        inf5 = INFO((1), 'S', 3, None, '<INS:ME>')
        variant_5 = Variant(['TC'], 'T', inf5, 0.7, 'ins', 3)
        result5 = self._db._unpack(variant_5)
        self.assertEqual(([0.3333333333333333], [1], ['INS'], ['TC'], 3, []), result5)

    @asynctest.mock.patch('beacon_api.utils.db_load.LOG')
    @asynctest.mock.patch('beacon_api.utils.db_load.asyncpg.connect')
    async def test_chunks(self, db_mock, mock_log):
        """Test database URL fetching."""
        db_mock.return_value = Connection()
        await self._db.connection()
        variant = [(1, 2), (2, 3)]
        result = self._db._chunks(variant, 1)
        lines = []
        for i in result:
            lines.append(list(i))
        self.assertEqual([[(1, 2)], [(2, 3)]], lines)


if __name__ == '__main__':
    unittest.main()
