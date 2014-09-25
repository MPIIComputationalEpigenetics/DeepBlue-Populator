class Type(object):
  STRING = "string"
  INTEGER = "integer"
  DOUBLE = "double"


SIMPLE = [
  ("AVG_METHYL_LEVEL", "Average methylation level in region", ".", Type.DOUBLE),
  ("CHROMOSOME", "Chromosome", None, Type.STRING),
  ("START", "Start", None, Type.INTEGER),
  ("END", "End", None, Type.INTEGER),
  ("NAME", "Region name", ".", Type.STRING),
  ("SCORE", "Region score", "0", Type.DOUBLE),
  ("SIGNAL_VALUE", "Signal value", None, Type.DOUBLE),
  ("P_VALUE", "P value", "-1", Type.DOUBLE),
  ("Q_VALUE", "Q value", "-1", Type.DOUBLE),
  ("PEAK", "Region peak", "-1", Type.INTEGER),
  ("THICK_START", "Thick start", "-1", Type.INTEGER),
  ("THICK_END", "Thick end", "-1", Type.INTEGER),
  ("ITEM_RGB", "Item RGB", "*", Type.STRING),
  ("BLOCK_COUNT", "Block count", "*", Type.STRING),
  ("BLOCK_SIZES", "Block sizes", "*", Type.STRING),
  ("BLOCK_STARTS", "Block starts", "*", Type.STRING),
  ("LEVEL", "Level", "-1", Type.DOUBLE),
  ("SIGN_IF", "Sign if", "-1", Type.DOUBLE),
  ("SCORE_2", "Level", "-1", Type.DOUBLE),
  ("LENGTH", "Length", "0", Type.INTEGER),
  ("NUM_CPG", "Number of CpGs in region", "0", Type.INTEGER),
  ("NUM_GC", "Number of GCs dinucleotide in region", "0", Type.INTEGER),
  ("GC_NUM", "GC number", "0", Type.DOUBLE),
  ("MEDIAN_NON_CONVERTED_CPG", "Median number of non-converted reads at CpGs in region", ".", Type.INTEGER),
  ("MEDIAN_CONVERTED_CPG", "Median number of converted reads at CpGs in region", ".", Type.INTEGER),
  ("MEDIAN_TOTAL_CPG", "Median number of total reads at CpGs in region", ".", Type.INTEGER),
  ("PER_CPG", "Per CPG", None, Type.DOUBLE),
  ("PER_GC", "Per GC", None, Type.DOUBLE),
  ("OBS_EXP", "Obs Exp", None, Type.DOUBLE),
  ("VALUE", "Value", "0", Type.INTEGER),
  ("ENSEMBL_ID", "Ensemble ID", None, Type.STRING),
  ("SPAN", "span", None, Type.INTEGER),
  ("COUNT", "count", None, Type.INTEGER),
  ("OFFSET", "offset", None, Type.INTEGER),
  ("FILE", "file", None, Type.STRING),
  ("LOWER_LIMIT", "Lower limit", None, Type.DOUBLE),
  ("DATA_RANGE", "Data range", None, Type.DOUBLE),
  ("VALID_COUNT", "Valid count", None, Type.INTEGER),
  ("SUM_DATA", "Sum data", None, Type.DOUBLE),
  ("SUM_SQUARES", "Sum squares", None, Type.DOUBLE),
  ("SW_SCORE", "SW score", "0", Type.INTEGER),
  ("MILLI_DIV", "milliDiv", "0", Type.INTEGER),
  ("MILLI_DEL", "milliDel", "0", Type.INTEGER),
  ("MILLI_INS", "milliIns", "0", Type.INTEGER),
  ("GENO_LEFT", "genoLeft", "0", Type.INTEGER),
  ("REF_GENES", "refGene annotation (union of refGene  annotations for all CpGs in region)", ".", Type.STRING),
  ("REP_NAME", "repName", None, Type.STRING),
  ("REP_CLASS", "repClass", None, Type.STRING),
  ("REP_FAMILY", "repFamily", None, Type.STRING),
  ("REP_START", "repStart", "0", Type.INTEGER),
  ("REP_END"," repEnd", "0", Type.INTEGER),
  ("REP_LEFT", "repLeft", "0", Type.INTEGER),
  ("ID", "Region id", None, Type.STRING),
  ("ISLAND_SHELF_SHORE", "Island/Shelf/Shore (union of CpG Island annotations for all CpGs in region)", ".", Type.STRING),
  ("SIZE", "Size of region in base pairs", ".", Type.INTEGER),
  ("IGNORE", "Ignored column", "*", Type.STRING),
]

CATEGORY = [
  ("STRAND", "Region strand: + or -", ".", ["+", "-"])
]

RANGE = []

