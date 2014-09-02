import settings
import formats

from annotation import Annotation

cpgIslands = Annotation({
	"name":"Cpg Islands",
	"genome":"hg19",
	"description":"CpG islands are associated with genes, particularly housekeeping genes, in vertebrates. CpG islands are typically common near transcription start sites and may be associated with promoter regions. Normally a C (cytosine) base followed immediately by a G (guanine) base (a CpG) is rare in vertebrate DNA because the Cs in such an arrangement tend to be methylated. This methylation helps distinguish the newly synthesized DNA strand from the parent strand, which aids in the final stages of DNA proofreading after duplication. However, over evolutionary time, methylated Cs tend to turn into Ts because of spontaneous deamination. The result is that CpGs are relatively rare unless there is selective pressure to keep them or a region is not methylated for some other reason, perhaps having to do with the regulation of gene expression. CpG islands are regions where CpGs are present at significantly higher levels than is typical for the genome as a whole.",
	"data_file":settings.DATA_DIR + "annotations/cpgIslandExt.txt.gz",
	"file_format":formats.format_builder("cpgIsland"),
	"extra_metadata":{"url":"genome.ucsc.edu/cgi-bin/hgTables?db=hg19&hgta_group=regulation&hgta_track=cpgIslandExt&hgta_table=cpgIslandExt&hgta_doSchema=describe+table+schema"}
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
	"extra_metadata":{"url" :"http://genome.ucsc.edu/cgi-bin/hgTrackUi?hgsid=346691263&g=cons46way"}
})

conservation_placental = Annotation({
	"name": "conservation_placental",
	"genome": "hg19",
	"description":"This track shows multiple alignments of 46 vertebrate species and measurements of evolutionary conservation using two methods (phastCons and phyloP) from the PHAST package, for all species (vertebrate) and two subsets (primate and placental mammal). The multiple alignments were generated using multiz and other tools in the UCSC/Penn State Bioinformatics comparative genomics alignment pipeline. Conserved elements identified by phastCons are also displayed in this track.",
	"data_file" : settings.DATA_DIR + "annotations/phastConsElements46wayPlacental.txt.gz",
	"file_format" : formats.format_builder("conservation_elements"),
	"extra_metadata":{"url" :"http://genome.ucsc.edu/cgi-bin/hgTrackUi?hgsid=346691263&g=cons46way"}
})

repeat_masker = Annotation({
	"name": "repeat_masker",
	"genome": "hg19",
	"description":"This track was created by using Arian Smit's RepeatMasker program, which screens DNA sequences for interspersed repeats and low complexity DNA sequences. The program outputs a detailed annotation of the repeats that are present in the query sequence (represented by this track), as well as a modified version of the query sequence in which all the annotated repeats have been masked (generally available on the Downloads page). RepeatMasker uses the RepBase library of repeats from the Genetic Information Research Institute (GIRI). RepBase is described in Jurka, J. (2000) in the References section below.",
	"data_url" : "http://hgdownload.cse.ucsc.edu/goldenPath/hg19/database/rmsk.txt.gz",
	"file_format" : formats.format_builder("rmsk"),
	"extra_metadata":{"url" : "http://genome.ucsc.edu/cgi-bin/hgTrackUi?hgsid=185567991&c=chrX&g=rmsk"}
})

annotations = [repeat_masker, cpgIslands, genes, promoters, probes450k, laminB1,conservation_primates, conservation_placental]