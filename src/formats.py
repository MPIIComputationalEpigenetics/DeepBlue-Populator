from log import log

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

gapped_peak_format = [
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
    "BLOCK_STARTS",
    "SIGNAL_VALUE",
    "P_VALUE",
    "Q_VALUE"
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
    "NUM_CPG",
    "NUM_GC",
    "PER_CPG",
    "PER_GC",
    "OBS_EXP"
]

genes = [
    "CHROMOSOME",
    "START",
    "END",
    "GENE_ID_ENSEMBL",
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

blueprint_bs_call = [
    "CHROMOSOME",
    "START",
    "END",
    "SIZE",
    "AVG_METHYL_LEVEL",
    "NUM_CPG",
    "MEDIAN_NON_CONVERTED_CPG",
    "MEDIAN_CONVERTED_CPG",
    "MEDIAN_TOTAL_CPG",
    "ISLAND_SHELF_SHORE",
    "REF_GENES"
]

# From ROADMAP
# DNase*hotspot.all.fdr0.01.pks.bed.gz: narrow Peaks in FDR 1% hotspots (i.e., FDR 1% peaks). 5th column score is peak tag density, 6th column score is z-score.
narrow_peaks_fdr_1perc_hotspot = [
    "CHROMOSOME",
    "START",
    "END",
    "IGNORE",
    "PEAK_TAG_DENSITY",
    "Z_SCORE"
]

gff = [
    "CHROMOSOME",
    "SOURCE",
    "FEATURE",
    "START",
    "END",
    "GFF_SCORE",
    "STRAND",
    "FRAME",
    "ATTRIBUTES"
]

deep_dna_methylation_calls_bisnp = [
    "CHROMOSOME",
    "START",
    "END",
    "AVG_METHYL_LEVEL",
    "DNA_METH_T",
    "STRAND",
    "THICK_START",
    "THICK_END",
    "ITEM_RGB",
    "COUNT_A",
    "COUNT_G"
]

nome_open_chromatin = [
    "CHROMOSOME",
    "START",
    "END",
    "AVG_METHYL_LEVEL",
    "DNA_METH_T",
    "STRAND",
    "THICK_START",
    "THICK_END",
    "ITEM_RGB",
    "COUNT_A",
    "COUNT_G"
]


#chr start   stop    p.value avg(fg_cov) avg.meth    avg(fg+bg_cov)  coverage_group  q.value
nome_open_chromatin_peaks = [
    "CHROMOSOME",
    "START",
    "END",
    "P_VALUE",
    "AVG_FOREGROUND_COVERAGE",
    "AVG_METHYL_LEVEL",
    "AVG_FOREGROUND_BACKGROUND_COVERAGE",
    "COVERAGE_GROUP",
    "Q_VALUE"
]

formats = {
    "simple": simple,
    "bed": bed,
    "broadPeak": broad_peak_format,
    "narrowPeak": narrow_peak_format,
    "gappedPeak": gapped_peak_format,
    "encode_rna": encode_rna,
    "cpgIsland": cpg_island,
    "genes": genes,
    "probes_450k": probes_450k,
    "lamin_b1": lamin_b1,
    "conservation_elements": conservation_elements,
    "rmsk": rmsk,
    "blueprint_bs_call": blueprint_bs_call,
    "narrow_peaks_fdr_1perc_hotspot": narrow_peaks_fdr_1perc_hotspot,
    "gff": gff,
    "deep_dna_methylation_calls_bisnp": deep_dna_methylation_calls_bisnp,
    "nome_open_chromatin": nome_open_chromatin,
    "nome_open_chromatin_peaks": nome_open_chromatin_peaks
}


def format_builder(format_name, length=None):
    if format_name == "wig":
        return "wig"

    if format_name == "bedgraph":
        return "bedgraph"

    if not formats.has_key(format_name):
        log.error("Format %s not found.", format_name)
        return format_name

    frmt = formats[format_name]
    if length == None:
        return ",".join(frmt)
    else:
        return ",".join(frmt[0:length])
