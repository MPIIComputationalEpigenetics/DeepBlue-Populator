import settings
import formats

from annotation import Annotation

cpgIslands = Annotation({
	"name":"Cpg Islands",
	"genome":"hg19",
	"description":"CpG islands are associated with genes, particularly housekeeping genes, in vertebrates. CpG islands are typically common near transcription start sites and may be associated with promoter regions. Normally a C (cytosine) base followed immediately by a G (guanine) base (a CpG) is rare in vertebrate DNA because the Cs in such an arrangement tend to be methylated. This methylation helps distinguish the newly synthesized DNA strand from the parent strand, which aids in the final stages of DNA proofreading after duplication. However, over evolutionary time, methylated Cs tend to turn into Ts because of spontaneous deamination. The result is that CpGs are relatively rare unless there is selective pressure to keep them or a region is not methylated for some other reason, perhaps having to do with the regulation of gene expression. CpG islands are regions where CpGs are present at significantly higher levels than is typical for the genome as a whole.",
	"data_file":settings.DATA_DIR + "annotations/cpgIslandExt.txt.gz",
	"file_format":formats.format_builder("cpgIsland"),
	"extra_metadata":{"URL":"genome.ucsc.edu/cgi-bin/hgTables?db=hg19&hgta_group=regulation&hgta_track=cpgIslandExt&hgta_table=cpgIslandExt&hgta_doSchema=describe+table+schema"}
})

genes = Annotation({
	"name":"Genes",
	"genome":"hg19",
	"description":"Gene set from Ensemble",
	"data_file":settings.DATA_DIR + "annotations/hg19.genes.bed.gz",
	"file_format":formats.format_builder("genes"),
})

promoters = Annotation({
	"name":"Promoters",
	"genome":"hg19",
	"description":"Promoters set from Ensemble",
	"data_file":settings.DATA_DIR + "annotations/hg19.promoters.bed.gz",
	"file_format":formats.format_builder("genes"),
})

probes450k = Annotation({
	"name":"Probes450k",
	"genome":"hg19",
	"description":"Probes for Illumina 450k",
	"data_file":settings.DATA_DIR + "annotations/hg19.probes450.bed.gz",
	"file_format":formats.format_builder("probes_450k"),
})

laminB1 = Annotation({
	"name": "lamin_b1",
	"genome": "hg19",
	"description":"The three-dimensional organization of chromosomes within the nucleus and its dynamics during differentiation are largely unknown. To visualize this process in molecular detail, high-resolution maps of genome-nuclear lamina interactions during subsequent differentiation of mouse embryonic stem cells were generated via lineage-committed neural precursor (or, neural progenitor) cells into terminally differentiated astrocytes. In addition, genome-nuclear lamina interactions for mouse embryonic fibroblasts were profiled.",
	"data_file" : settings.DATA_DIR + "annotations/laminB1.txt.gz",
	"file_format" : formats.format_builder("lamin_b1")
})

conservation_primates = Annotation({
	"name": "conservation_primates",
	"genome": "hg19",
	"description":"This track shows multiple alignments of 46 vertebrate species and measurements of evolutionary conservation using two methods (phastCons and phyloP) from the PHAST package, for all species (vertebrate) and two subsets (primate and placental mammal). The multiple alignments were generated using multiz and other tools in the UCSC/Penn State Bioinformatics comparative genomics alignment pipeline. Conserved elements identified by phastCons are also displayed in this track.",
	"data_file" : settings.DATA_DIR + "annotations/phastConsElements46wayPrimates.txt.gz",
	"file_format" : formats.format_builder("conservation_elements"),
	"extra_metadata":{"URL" :"http://genome.ucsc.edu/cgi-bin/hgTrackUi?hgsid=346691263&g=cons46way"}
})

conservation_placental = Annotation({
	"name": "conservation_placental",
	"genome": "hg19",
	"description":"This track shows multiple alignments of 46 vertebrate species and measurements of evolutionary conservation using two methods (phastCons and phyloP) from the PHAST package, for all species (vertebrate) and two subsets (primate and placental mammal). The multiple alignments were generated using multiz and other tools in the UCSC/Penn State Bioinformatics comparative genomics alignment pipeline. Conserved elements identified by phastCons are also displayed in this track.",
	"data_file" : settings.DATA_DIR + "annotations/phastConsElements46wayPlacental.txt.gz",
	"file_format" : formats.format_builder("conservation_elements"),
	"extra_metadata":{"URL" :"http://genome.ucsc.edu/cgi-bin/hgTrackUi?hgsid=346691263&g=cons46way"}
})

repeat_masker = Annotation({
	"name": "repeat_masker",
	"genome": "hg19",
	"description":"This track was created by using Arian Smit's RepeatMasker program, which screens DNA sequences for interspersed repeats and low complexity DNA sequences. The program outputs a detailed annotation of the repeats that are present in the query sequence (represented by this track), as well as a modified version of the query sequence in which all the annotated repeats have been masked (generally available on the Downloads page). RepeatMasker uses the RepBase library of repeats from the Genetic Information Research Institute (GIRI). RepBase is described in Jurka, J. (2000) in the References section below.",
	"data_url" : "http://hgdownload.cse.ucsc.edu/goldenPath/hg19/database/rmsk.txt.gz",
	"file_format" : formats.format_builder("rmsk"),
	"extra_metadata":{"URL" : "http://genome.ucsc.edu/cgi-bin/hgTrackUi?hgsid=185567991&c=chrX&g=rmsk"}
})

RepeatFree_1kb_autosomes = Annotation({
	"name": 'RepeatFree_1kb_autosomes',
	"genome":'mm10',
    "description" :'Non-overlapping regions of size 1kb defined by regular expression [ACGT]{1000}. The regions can be consecutive.',
    "data_file" : settings.DATA_DIR + "annotations/mm10_repfree_1000.bed.gz",
    "file_format": 'CHROMOSOME,START,END,NAME',
	"extra_metadata": {'URL': 'http://hgdownload.soe.ucsc.edu/goldenPath/mm10/chromosomes', 'Chromosomes': 'autosomes'}
})

RepeatMasked_1kb_autosomes = Annotation({
	"name": 'RepeatMasked_1kb_autosomes',
	"genome":'mm10',
	"description": 'Non-overlapping regions of size 1kb defined by regular expression [acgt]{1000}. The regions can be consecutive.',
    "data_file" : settings.DATA_DIR + "annotations/mm10_repmask_1000.bed.gz",
	"file_format": 'CHROMOSOME,START,END,NAME',
	"extra_metadata": {'URL': 'http://hgdownload.soe.ucsc.edu/goldenPath/mm10/chromosomes', 'Chromosomes': 'autosomes'}
})

gene_protcod_3kbprom_autosomes = Annotation({
	"name": 'gene_protcod_3kbprom_autosomes',
	"genome": 'mm10',
	"description": 'Promoter regions of protein coding genes defined as the min/max of all TSS in the gene and then extended by 1.5kb in each direction. Annotation based on GENCODE M4.',
	"data_file" : settings.DATA_DIR + "annotations/mm10_genes_protcod_3kbprom_GENCODE_M4.bed.gz",
	"file_format": 'CHROMOSOME,START,END,GENE_SYMBOL,GENE_ID_ENSEMBL,STRAND',
	"extra_metadata": {'URL': 'ftp://ftp.sanger.ac.uk/pub/gencode/Gencode_mouse/release_M4/gencode.vM4.annotation.gtf.gz', 'Chromosomes': 'autosomes', 'GENCODE': 'M4', 'ENSEMBL': '78', 'AltAssembly': 'GRCm38'}
})

gene_protcod_full_autosomes = Annotation({
	"name": 'gene_protcod_full_autosomes',
	"genome": 'mm10',
	"description":  'Protein coding genes as annotated with start/end in GENCODE M4 (changed to start-1 for BED output).',
	"data_file" : settings.DATA_DIR + "annotations/mm10_genes_protcod_full_GENCODE_M4.bed.gz",
	"file_format":  'CHROMOSOME,START,END,GENE_SYMBOL,GENE_ID_ENSEMBL,STRAND',
	"extra_metadata" : {'URL': 'ftp://ftp.sanger.ac.uk/pub/gencode/Gencode_mouse/release_M4/gencode.vM4.annotation.gtf.gz', 'Chromosomes': 'autosomes', 'GENCODE': 'M4', 'ENSEMBL': '78', 'AltAssembly': 'GRCm38'}
})

transcripts_protcod_3kbprom_autosomes = Annotation({
	"name" : 'transcripts_protcod_3kbprom_autosomes',
	"genome": 'mm10',
	"description" :  'Protein coding transcript promoters defined as TSS plus/minus 1.5kb (0-based coordinate for BED) based on GENCODE M4.',
    "data_file" : settings.DATA_DIR + "annotations/mm10_transcripts_protcod_3kbprom_GENCODE_M4.bed.gz",
    "file_format": 'CHROMOSOME,START,END,GENE_SYMBOL,GENE_ID_ENSEMBL,TRANSCRIPT_ID_ENSEMBL,STRAND',
	"extra_metadata": {'URL': 'ftp://ftp.sanger.ac.uk/pub/gencode/Gencode_mouse/release_M4/gencode.vM4.annotation.gtf.gz', 'Chromosomes': 'autosomes', 'GENCODE': 'M4', 'ENSEMBL': '78', 'AltAssembly': 'GRCm38'}
})

transcripts_lincRNA_full_autosomes = Annotation({
	"name": 'transcripts_lincRNA_full_autosomes',
	"genome": 'mm10',
	"description" : 'All transcripts with type lincRNA in GENCODE M4 as annotated with start/end (start-1 to be BED compliant).',
	"data_file" : settings.DATA_DIR + "annotations/mm10_transcripts_lincRNA_full_GENCODE_M4.bed.gz",
	"file_format" : 'CHROMOSOME,START,END,GENE_ID_ENSEMBL,GENE_SYMBOL,TRANSCRIPT_ID_ENSEMBL,TRANSCRIPT_SYMBOL,STRAND',
	"extra_metadata": {'URL': 'ftp://ftp.sanger.ac.uk/pub/gencode/Gencode_mouse/release_M4/gencode.vM4.annotation.gtf.gz', 'Chromosomes': 'autosomes', 'GENCODE': 'M4',  'ENSEMBL': '78', 'AltAssembly': 'GRCm38'}
})

transcripts_miRNA_full_autosomes = Annotation({
	"name" : 'transcripts_miRNA_full_autosomes',
	"genome" : 'mm10',
	"description" : 'All transcripts with type miRNA in GENCODE M4 as annotated with start/end (start-1 to be BED compliant).',
	"data_file" : settings.DATA_DIR + "annotations/mm10_transcripts_miRNA_full_GENCODE_M4.bed.gz",
	"file_format" :  'CHROMOSOME,START,END,GENE_ID_ENSEMBL,GENE_SYMBOL,TRANSCRIPT_ID_ENSEMBL,TRANSCRIPT_SYMBOL,STRAND',
	"extra_metadata":  {'URL': 'ftp://ftp.sanger.ac.uk/pub/gencode/Gencode_mouse/release_M4/gencode.vM4.annotation.gtf.gz', 'Chromosomes': 'autosomes', 'GENCODE': 'M4', 'ENSEMBL': '78', 'AltAssembly': 'GRCm38'}
})

transcripts_snRNA_full_autosomes = Annotation({
	"name" : 'transcripts_snRNA_full_autosomes',
	"genome" : 'mm10',
	"description" : 'All transcripts with type snRNA in GENCODE M4 as annotated with start/end (start-1 to be BED compliant).',
	"data_file" : settings.DATA_DIR + "annotations/mm10_transcripts_snRNA_full_GENCODE_M4.bed.gz",
	"file_format" : 'CHROMOSOME,START,END,GENE_ID_ENSEMBL,GENE_SYMBOL,TRANSCRIPT_ID_ENSEMBL,TRANSCRIPT_SYMBOL,STRAND',
	"extra_metadata" : {'URL': 'ftp://ftp.sanger.ac.uk/pub/gencode/Gencode_mouse/release_M4/gencode.vM4.annotation.gtf.gz', 'Chromosomes': 'autosomes', 'GENCODE': 'M4', 'ENSEMBL': '78', 'AltAssembly': 'GRCm38'}
})

transcripts_snoRNA_full_autosomes = Annotation({
	"name" : 'transcripts_snoRNA_full_autosomes',
	"genome" : 'mm10',
	"description":  "All transcripts with type snoRNA in GENCODE M4 as annotated with start/end (start-1 to be BED compliant).",
	"data_file" : settings.DATA_DIR + "annotations/mm10_transcripts_snoRNA_full_GENCODE_M4.bed.gz",
	"file_format" : 'CHROMOSOME,START,END,GENE_ID_ENSEMBL,GENE_SYMBOL,TRANSCRIPT_ID_ENSEMBL,TRANSCRIPT_SYMBOL,STRAND',
	"extra_metadata" : {'URL': 'ftp://ftp.sanger.ac.uk/pub/gencode/Gencode_mouse/release_M4/gencode.vM4.annotation.gtf.gz', 'Chromosomes': 'autosomes', 'GENCODE': 'M4', 'ENSEMBL': '78', 'AltAssembly': 'GRCm38'}
})


annotations = [repeat_masker, cpgIslands, genes, promoters, probes450k, laminB1,conservation_primates, conservation_placental, RepeatFree_1kb_autosomes, RepeatMasked_1kb_autosomes, gene_protcod_3kbprom_autosomes, gene_protcod_3kbprom_autosomes, gene_protcod_3kbprom_autosomes, gene_protcod_full_autosomes, transcripts_protcod_3kbprom_autosomes, transcripts_lincRNA_full_autosomes, transcripts_snRNA_full_autosomes, transcripts_snoRNA_full_autosomes]
