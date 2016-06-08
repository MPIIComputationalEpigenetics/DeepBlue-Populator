subproject = {}
subproject["41"] = "SP 4.1"
subproject["42"] = "SP 4.2"
subproject["43"] = "SP 4.3"
subproject["44"] = "SP 4.4"
subproject["51"] = "SP 5.1"
subproject["52"] = "SP 5.2"
subproject["53"] = "SP 5.3"
subproject["00"] = "IHEC"
subproject["01"] = "SP 2.1 (UdS)"
subproject["02"] = "SP 2.2 (MPI-IE)"

def get_subproject(subproject_id):
  return subproject.get(subproject_id, subproject_id)

species = {}
species["H"] = "Human"
species["M"] = "Mouse"

def get_specie(specie_id):
  return species.get(specie_id, specie_id)

sex = {}
sex["f"] = "female"
sex["m"] = "male"

def get_sex(sex_id):
  return sex.get(sex_id, sex_id)


"""
cellline = {}
cellline["Ad"] = "3T3 L1 mouse cell line"
cellline["Mc"] = "MCF10A mouse cell line"
cellline["HR"] = "HepG2 cell line"
cellline["HG"] = "HepaRG cell line"
"""

organ_tissue = {}
organ_tissue["Bl"] = "Blood"
organ_tissue["Co"] = "Colon"
organ_tissue["Il"] = "Ileum"
organ_tissue["In"] = "Intestine"
organ_tissue["LP"] = "Lamina Propria"
organ_tissue["Li"] = "Liver"
organ_tissue["SF"] = "Synovial Fluid"
organ_tissue["WE"] = "White Adipose Tissue (Epididymal)"
organ_tissue["WS"] = "White Adipose Tissue (Subcutaneous)"
organ_tissue["WM"] = "White Adipose Tissue (Mesenteric)"
organ_tissue["Br"] = "Brown Adipose Tissue"
organ_tissue["Bm"] = "Bone marrow"

def get_organ_tissue(organ_tissue_id):
  return organ_tissue.get(organ_tissue_id, organ_tissue_id)


celltypes = {}
celltypes["Ad"] = "Adipocytes"
celltypes["CM"] = "Central memory CD4+"
celltypes["Ec"] = "Epithelial cells"
celltypes["EM"] = "Effector memory CD4+"
celltypes["Fi"] = "Fibroblasts"
celltypes["He"] = "Hepatocytes"
celltypes["Ku"] = "Kupffer cells"
celltypes["Ma"] = "Macrophages"
celltypes["Mo"] = "Monocytes"
celltypes["Mu"] = "Mucosa"
celltypes["NP"] = "Non-parenchymal cells"
celltypes["PM"] = "Protective memory CD4+"
celltypes["TA"] = "TA" # ???
celltypes["Th"] = "CD4+ T helper cells"
celltypes["Ti"] = "Whole Tissue"
celltypes["TN"] = "naive T cells"

def get_celltype(celltype_id):
  return celltypes.get(celltype_id, celltype_id)

disease_status = {}
disease_status["CD"] = "Crohn's Disease"
disease_status["Ci"] = "in vitro System, Control"
disease_status["Ct"] = "normal Control"
disease_status["Oa"] = "Osteoarthritis"
disease_status["OC"] = "ob+/-, Control"
disease_status["OS"] = "ob-/-, Steatosis"
disease_status["PH"] = "p62 transgenic, Steatohepatitis"
disease_status["PS"] = "p62 transgenic, Steatosis"
disease_status["RA"] = "Rheumatoid Arthritis"
disease_status["SC"] = "Stochastic Obesity, Control"
disease_status["Si"] = "In vitro System, Steatosis"
disease_status["SL"] = "Stochastic Obesity,Lean"
disease_status["SO"] = "Stochastic Obesity, Obese"
disease_status["St"] = "Steatosis"
disease_status["TE"] = "Treatment with E-LDL"
disease_status["TO"] = "Treatment with Ox-LDL"
disease_status["UC"] = "Ulcerative Colitis"

def get_disease_status(_id):
  if disease_status.has_key(_id):
    return disease_status[_id]

  else:
    if _id[:2] == "Db":
      return "Circadian Rythm (x= " + _id[2] + "), Db-mice"
    if _id[0] == "C":
      return "Circadian Rythm (x= " + _id[1] + ")"
    if _id[0] == "D":
      return "DMSO-treated (timepoint x= " + _id[1] + ")"
    if _id[0] == "T":
      return "Timepoint (x= " + _id[1] + ")"

library= {}
library["DNase"] = ("DNaseI", "DNase-Seq")
library["NOMe"] = ("__", "NOMe-seq")
library["WGBS"] = ("DNA Methylation", "WGBS")
library["Input"] = ("Input", "ChIP-seq")
library["H3K4me3"] = ("H3K4me3", "ChIP-seq")
library["H3K4me1"] = ("H3K4me1", "ChIP-seq")
library["H3K9me3"] = ("H3K9me3", "ChIP-seq")
library["H3K36me3"] = ("H3K36me3", "ChIP-seq")
library["H3K27ac"] = ("H3K27ac", "ChIP-seq")
library["H3K27me3"] = ("H3K27me3", "ChIP-seq")
library["mRNA"] = ("mRNA", "RNA-Seq")
library["tRNA"] = ("tRNA", "RNA-Seq")
library["snRNA"] = ("snRNA", "RNA-Seq")
library["CTCF"] = ("CTCF", "ChIP-seq")

def get_epigenetic_mark_technology(library_id):
  return library[library_id]

sequencing_center = {}
sequencing_center["B"] = "Berlin"
sequencing_center["E"] = "Essen"
sequencing_center["F"] = "Freiburg"
sequencing_center["K"] = "Kiel"
sequencing_center["M"] = "MDC Berlin"
sequencing_center["S"] = "Saarbruecken"
sequencing_center["I"] = "IHEC (Download)"
sequencing_center["R"] = "Broad Institute (Download)"

def get_sequencing_center(sequencing_center_id):
  return sequencing_center.get(sequencing_center_id, sequencing_center_id)

