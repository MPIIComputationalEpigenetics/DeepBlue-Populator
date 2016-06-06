class Type(object):
    STRING = "string"
    INTEGER = "integer"
    DOUBLE = "double"


SIMPLE = [
    ("AVG_METHYL_LEVEL", "Average methylation level in region", Type.DOUBLE),
    ("BLOCK_COUNT", "Block count", Type.STRING),
    ("BLOCK_SIZES", "Block sizes", Type.STRING),
    ("BLOCK_STARTS", "Block starts", Type.STRING),
    ("CHROMOSOME", "Chromosome", Type.STRING),
    ("COUNT", "count", Type.INTEGER),
    ("COUNT_A", "Count of A", Type.INTEGER),
    ("COUNT_G", "Count of A", Type.INTEGER)
    ("DATA_RANGE", "Data range", Type.DOUBLE),
    ("DNA_METH_M", "Number of methylated reads for a cytosine in a bisulfite sequencing experiment", Type.INTEGER),
    ("DNA_METH_T", "Number of total reads for a cytosine in a bisulfite sequencing experiment", Type.INTEGER),
    ("DNA_METH_U", "Number of unmethylated reads for a cytosine in a bisulfite sequencing experiment", Type.INTEGER),
    ("END", "End", Type.INTEGER),
    ("EXPRESSION_NORM", "", Type.DOUBLE),
    ("EXPRESSION_NORM_GCRMA", "GCRMA-normalized signal intensity", Type.DOUBLE),
    ("FILE", "file", Type.STRING),
    ("GENE_ID_ENSEMBL", "Gene Ensemble ID", Type.STRING),
    ("GENE_ID_ENTREZ", "Gene ID in Entrez", Type.STRING),
    ("GENE_SYMBOL", "Gene Symbol", Type.STRING),
    ("GENO_LEFT", "genoLeft", Type.INTEGER),
    ("GFF_SCORE", "A floating point value. The type is a string because the value '.' is also acceptable.", Type.STRING),
    ("ID", "Region id", Type.STRING),
    ("IGNORE", "Ignored column", Type.STRING),
    ("ISLAND_SHELF_SHORE", "Island/Shelf/Shore (union of CpG Island annotations for all CpGs in region)", Type.STRING),
    ("ITEM_RGB", "Item RGB", Type.STRING),
    ("LENGTH", "Length", Type.INTEGER),
    ("LEVEL", "Level", Type.DOUBLE),
    ("LOWER_LIMIT", "Lower limit", Type.DOUBLE),
    ("MEDIAN_CONVERTED_CPG", "Median number of converted reads at CpGs in region", Type.INTEGER),
    ("MEDIAN_NON_CONVERTED_CPG", "Median number of non-converted reads at CpGs in region", Type.INTEGER),
    ("MEDIAN_TOTAL_CPG", "Median number of total reads at CpGs in region", Type.INTEGER),
    ("MILLI_DEL", "milliDel", Type.INTEGER),
    ("MILLI_DIV", "milliDiv", Type.INTEGER),
    ("MILLI_INS", "milliIns", Type.INTEGER),
    ("NAME", "Region name", Type.STRING),
    ("NUM_CPG", "Number of CpGs in region", Type.INTEGER),
    ("NUM_GC", "Number of GCs dinucleotide in region", Type.INTEGER),
    ("OBS_EXP", "Obs Exp", Type.DOUBLE),
    ("OFFSET", "offset", Type.INTEGER),
    ("P_VALUE", "P value", Type.DOUBLE),
    ("PEAK", "Region peak", Type.INTEGER),
    ("PEAK_TAG_DENSITY", "Peak tag density", Type.INTEGER),
    ("PER_CPG", "Per CPG", Type.DOUBLE),
    ("PER_GC", "Per GC", Type.DOUBLE),
    ("PROBE_ID", "Microarray probe id", Type.STRING),
    ("Q_VALUE", "Q value", Type.DOUBLE),
    ("REF_GENES", "refGene annotation (union of refGene  annotations for all CpGs in region)", Type.STRING),
    ("REP_CLASS", "repClass", Type.STRING),
    ("REP_END", " repEnd", Type.INTEGER),
    ("REP_FAMILY", "repFamily", Type.STRING),
    ("REP_LEFT", "repLeft", Type.INTEGER),
    ("REP_NAME", "repName", Type.STRING),
    ("REP_START", "repStart", Type.INTEGER),
    ("SCORE", "Region score", Type.DOUBLE),
    ("SCORE_2", "Level", Type.DOUBLE),
    ("SIGN_IF", "Sign if", Type.DOUBLE),
    ("SIGNAL_VALUE", "Signal value", Type.DOUBLE),
    ("SIZE", "Size of region in base pairs", Type.INTEGER),
    ("SPAN", "span", Type.INTEGER),
    ("START", "Start", Type.INTEGER),
    ("SUM_DATA", "Sum data", Type.DOUBLE),
    ("SUM_SQUARES", "Sum squares", Type.DOUBLE),
    ("SW_SCORE", "SW score", Type.INTEGER),
    ("THICK_END", "Thick end", Type.INTEGER),
    ("THICK_START", "Thick start", Type.INTEGER),
    ("TRANSCRIPT_ID_ENSEMBL", "ENSEMBL transcript ID", Type.STRING),
    ("TRANSCRIPT_SYMBOL", "Analogous to GENE_SYMBOL, usually GENE_SYMBOL with numeric suffix", Type.STRING),
    ("VALID_COUNT", "Valid count", Type.INTEGER),
    ("VALUE", "Value", Type.INTEGER),
    ("Z_SCORE", "Z-Score", Type.DOUBLE)
]

CATEGORY = [
    ("STRAND", "Region strand: +, -, .", ["+", "-", "."])
]

RANGE = []

