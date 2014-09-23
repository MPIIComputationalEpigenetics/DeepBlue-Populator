import cStringIO

def try_to_convert(filename):
	f = open(filename)
	output = cStringIO.StringIO()
	init = False
	type = "wig"
	for line in f:
		if line.startswith("#bedGraph"):
			type = "bedgraph"
			if init:
				output.write("fixedStep chrom=%s start=%d step=%d span=%d\n" % (chromosome, start, actual_step, actual_span))
				for v in actual_block:
					output.write("%f\n" % (v))
				init = False

			fields = line.split()
			(chromosome, localization) = fields[2].split(":")
			(start, end) = localization.split("-")

			actual_block = []
			actual_step = -1
			actual_span = -1
			previus_start = -1
			start = int(start)
			end = int(end)
			init = True
		elif line.startswith("chr"):
			type = "bedgraph"
			(l_chr, l_start, l_end, l_value) = line.strip().split("\t")
			if (l_chr != chromosome):
				return (type, "Invalid chromosome %s expecting %s" %(l_chr, chromosome))

			l_start = int(l_start)
			l_end = int(l_end)
			l_value = float(l_value)

			if actual_span == -1:
				actual_span = l_end - l_start
			elif actual_span != l_end - l_start:
				return (type, "invalid span %d" %(actual_span))

			if actual_step == -1 and previus_start != -1:
				actual_step = l_start - previus_start
			elif actual_step != -1 and actual_step != l_start - previus_start:
				return (type, "invalid step %d" %(actual_step))

			actual_block.append(l_value)
			previus_start = l_start

		elif line.startswith("track"):
			if "bedgraph" in line.lower():
				type = "bedgraph"
			continue
		elif line.startswith("#"):
			continue
		elif line.startswith("browser"):
			continue
		else:
			return (type, "invalid: %s " %(line))

	if init:
		output.write("fixedStep chrom=%s start=%d step=%d span=%d\n" % (chromosome, start, actual_step, actual_span))
		for v in actual_block:
			output.write("%f\n" % (v))

	s = output.getvalue()
	return ("wig", s)
