DROP TABLE IF EXISTS CIFgene;
CREATE TABLE CIFgene
(
  ID	 VARCHAR(10) NOT NULL PRIMARY KEY,
  gene	 VARCHAR(4) NOT NULL,
  product	VARCHAR NOT NULL,
  cif_type VARCHAR NOT NULL,
  organism VARCHAR NOT NULL,
  strain  	 VARCHAR NOT NULL,
  host VARCHAR NOT NULL,
  description VARCHAR NOT NULL,
  NCBI_nucleotide VARCHAR,
  locus_tag VARCHAR,
  NCBI_protein VARCHAR,
  aa_sequence VARCHAR NOT NULL
);