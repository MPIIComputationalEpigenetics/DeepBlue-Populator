class Type(object):
    STRING = "string"
    INTEGER = "integer"
    DOUBLE = "double"


SIMPLE = [
    ("AVG_METHYL_LEVEL", "Average methylation level in region", Type.DOUBLE),
    ("CHROMOSOME", "Chromosome", Type.STRING),
    ("START", "Start", Type.INTEGER),
    ("END", "End", Type.INTEGER),
    ("NAME", "Region name", Type.STRING),
    ("SCORE", "Region score", Type.DOUBLE),
    ("SIGNAL_VALUE", "Signal value", Type.DOUBLE),
    ("P_VALUE", "P value", Type.DOUBLE),
    ("Q_VALUE", "Q value", Type.DOUBLE),
    ("PEAK", "Region peak", Type.INTEGER),
    ("THICK_START", "Thick start", Type.INTEGER),
    ("THICK_END", "Thick end", Type.INTEGER),
    ("ITEM_RGB", "Item RGB", Type.STRING),
    ("BLOCK_COUNT", "Block count", Type.STRING),
    ("BLOCK_SIZES", "Block sizes", Type.STRING),
    ("BLOCK_STARTS", "Block starts", Type.STRING),
    ("LEVEL", "Level", Type.DOUBLE),
    ("SIGN_IF", "Sign if", Type.DOUBLE),
    ("SCORE_2", "Level", Type.DOUBLE),
    ("LENGTH", "Length", Type.INTEGER),
    ("NUM_CPG", "Number of CpGs in region", Type.INTEGER),
    ("NUM_GC", "Number of GCs dinucleotide in region", Type.INTEGER),
    ("MEDIAN_NON_CONVERTED_CPG", "Median number of non-converted reads at CpGs in region", Type.INTEGER),
    ("MEDIAN_CONVERTED_CPG", "Median number of converted reads at CpGs in region", Type.INTEGER),
    ("MEDIAN_TOTAL_CPG", "Median number of total reads at CpGs in region", Type.INTEGER),
    ("PER_CPG", "Per CPG", Type.DOUBLE),
    ("PER_GC", "Per GC", Type.DOUBLE),
    ("OBS_EXP", "Obs Exp", Type.DOUBLE),
    ("VALUE", "Value", Type.INTEGER),
    ("GENE_ID_ENSEMBL", "Gene Ensemble ID", Type.STRING),
    ("SPAN", "span", Type.INTEGER),
    ("COUNT", "count", Type.INTEGER),
    ("OFFSET", "offset", Type.INTEGER),
    ("FILE", "file", Type.STRING),
    ("LOWER_LIMIT", "Lower limit", Type.DOUBLE),
    ("DATA_RANGE", "Data range", Type.DOUBLE),
    ("VALID_COUNT", "Valid count", Type.INTEGER),
    ("SUM_DATA", "Sum data", Type.DOUBLE),
    ("SUM_SQUARES", "Sum squares", Type.DOUBLE),
    ("SW_SCORE", "SW score", Type.INTEGER),
    ("MILLI_DIV", "milliDiv", Type.INTEGER),
    ("MILLI_DEL", "milliDel", Type.INTEGER),
    ("MILLI_INS", "milliIns", Type.INTEGER),
    ("GENO_LEFT", "genoLeft", Type.INTEGER),
    ("REF_GENES", "refGene annotation (union of refGene  annotations for all CpGs in region)", Type.STRING),
    ("REP_NAME", "repName", Type.STRING),
    ("REP_CLASS", "repClass", Type.STRING),
    ("REP_FAMILY", "repFamily", Type.STRING),
    ("REP_START", "repStart", Type.INTEGER),
    ("REP_END", " repEnd", Type.INTEGER),
    ("REP_LEFT", "repLeft", Type.INTEGER),
    ("ID", "Region id", Type.STRING),
    ("ISLAND_SHELF_SHORE", "Island/Shelf/Shore (union of CpG Island annotations for all CpGs in region)",
     Type.STRING),
    ("SIZE", "Size of region in base pairs", Type.INTEGER),
    ("IGNORE", "Ignored column", Type.STRING),
    ("TRANSCRIPT_ID_ENSEMBL", "ENSEMBL transcript ID", Type.STRING),
    ("TRANSCRIPT_SYMBOL", "Analogous to GENE_SYMBOL, usually GENE_SYMBOL with numeric suffix", Type.STRING),
    ("GENE_SYMBOL", "Gene Symbol", Type.STRING),
    ("PROBE_ID", "Microarray probe id", Type.STRING),
    ("EXPRESSION_NORM_GCRMA", "GCRMA-normalized signal intensity", Type.DOUBLE),
    ("DNA_METH_U", "Number of unmethylated reads for a cytosine in a bisulfite sequencing experiment", Type.INTEGER),
    ("DNA_METH_M", "Number of methylated reads for a cytosine in a bisulfite sequencing experiment", Type.INTEGER),
    ("DNA_METH_T", "Number of total reads for a cytosine in a bisulfite sequencing experiment", Type.INTEGER),
    ("GENE_ID_ENTREZ", "Gene ID in ENTREZ", Type.INTEGER),
    ("EXPRESSION_NORM", "", Type.DOUBLE)
]

CATEGORY = [
    ("STRAND", "Region strand: +, -, .", ["+", "-", "."])
]

RANGE = []

