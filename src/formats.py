from settings import log

simple = []

bed = [
  "CHROMOSOME",
  "START",
  "END",
  "NAME",
  "SCORE",
  "STRAND",
  "THICK_START",
  "THICK_END",
  "ITEM_RGB",
  "BLOCK_COUNT",
  "BLOCK_SIZES",
  "BLOCK_STARTS"
]

narrow_peak_format = [
  "CHROMOSOME",
  "START",
  "END",
  "NAME",
  "SCORE",
  "STRAND",
  "SIGNAL_VALUE",
  "P_VALUE",
  "Q_VALUE",
  "PEAK"
]

broad_peak_format = [
  "CHROMOSOME",
  "START",
  "END",
  "NAME",
  "SCORE",
  "STRAND",
  "SIGNAL_VALUE",
  "P_VALUE",
  "Q_VALUE",
]

encode_rna = [
  "CHROMOSOME",
  "START",
  "END",
  "NAME",
  "SCORE",
  "STRAND",
  "LEVEL",
  "SIGN_IF",
  "SCORE_2"
]

cpg_island = [
  "CHROMOSOME",
  "START",
  "END",
  "NAME",
  "LENGTH",
  "CPG_NUM",
  "GC_NUM",
  "PER_CPG",
  "PER_GC",
  "OBS_EXP"
]

genes = [
  "CHROMOSOME",
  "START",
  "END",
  "ENSEMBL_ID",
  "VALUE",
  "STRAND"
]

probes_450k = [
  "CHROMOSOME",
  "START",
  "END",
  "NAME",
  "VALUE",
  "STRAND"
]

lamin_b1 = [
  "CHROMOSOME",
  "START",
  "END",
  "NAME",
  "SPAN",
  "COUNT",
  "OFFSET",
  "FILE",
  "LOWER_LIMIT",
  "DATA_RANGE",
  "VALID_COUNT",
  "SUM_DATA",
  "SUM_SQUARES",
]

conservation_elements = [
  "CHROMOSOME",
  "START",
  "END",
  "NAME",
  "SCORE"
]

rmsk = [
  "SW_SCORE",
  "MILLI_DIV",
  "MILLI_DEL",
  "MILLI_INS",
  "CHROMOSOME",
  "START",
  "END",
  "GENO_LEFT",
  "STRAND",
  "REP_NAME",
  "REP_CLASS",
  "REP_FAMILY",
  "REP_START",
  "REP_END",
  "REP_LEFT",
  "ID",
]

formats = {
  "simple": simple,
  "bed" : bed,
  "broadPeak" : broad_peak_format,
  "narrowPeak" : narrow_peak_format,
  "encode_rna" : encode_rna,
  "cpgIsland" : cpg_island,
  "genes" : genes,
  "probes_450k": probes_450k,
  "lamin_b1" : lamin_b1,
  "conservation_elements": conservation_elements,
  "rmsk":rmsk
}

def format_builder(format_name, length=None):
  if not formats.has_key(format_name):
    log.error("Format %s not found", format_name)
    return None

  frmt = formats[format_name]
  if length==None:
    return ",".join(frmt)
  else:
    return ",".join(frmt[0:length])
