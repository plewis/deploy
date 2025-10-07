for i in {1..__NREPS__}
do
	cd rep$i/rb
	for l in {1..__NLOCI__}
	do
		mkdir gene$l
		mv locus$l.nex gene$l
		cd gene$l
		
		echo '################################################################################' > jc-post.Rev
		echo '#' >> jc-post.Rev
		echo '# RevBayes Example: Bayesian inference of phylogeny using a Jukes-Cantor' >> jc-post.Rev
		echo '#            substitution model on a single gene.' >> jc-post.Rev
		echo '#' >> jc-post.Rev
		echo '# authors: Sebastian Hoehna, Michael Landis, and Tracy A. Heath' >> jc-post.Rev
		echo '#' >> jc-post.Rev
		echo '################################################################################' >> jc-post.Rev
		echo '' >> jc-post.Rev
		echo '' >> jc-post.Rev
		echo '### Read in sequence data for both genes' >> jc-post.Rev
		echo 'data = readDiscreteCharacterData("locus$l.nex")' >> jc-post.Rev
		echo '' >> jc-post.Rev
		echo '# Get some useful variables from the data. We need these later on.' >> jc-post.Rev
		echo 'num_taxa <- data.ntaxa()' >> jc-post.Rev
		echo 'num_branches <- 2 * num_taxa - 3' >> jc-post.Rev
		echo 'taxa <- data.taxa()' >> jc-post.Rev
		echo '' >> jc-post.Rev
		echo 'moves    = VectorMoves()' >> jc-post.Rev
		echo 'monitors = VectorMonitors()' >> jc-post.Rev
		echo '' >> jc-post.Rev
		echo '######################' >> jc-post.Rev
		echo '# Substitution Model #' >> jc-post.Rev
		echo '######################' >> jc-post.Rev
		echo '' >> jc-post.Rev
		echo '# create a constant variable for the rate matrix' >> jc-post.Rev
		echo 'Q <- fnJC(4)' >> jc-post.Rev
		echo '' >> jc-post.Rev
		echo '##############' >> jc-post.Rev
		echo '# Tree model #' >> jc-post.Rev
		echo '##############' >> jc-post.Rev
		echo '' >> jc-post.Rev
		echo '# Prior distribution on the tree topology' >> jc-post.Rev
		echo 'topology ~ dnUniformTopology(taxa)' >> jc-post.Rev
		echo '' >> jc-post.Rev
		echo 'moves.append( mvNNI(topology, weight=num_taxa) )' >> jc-post.Rev
		echo 'moves.append( mvSPR(topology, weight=num_taxa/10) )' >> jc-post.Rev
		echo '\n' >> jc-post.Rev
		echo '# Branch length prior' >> jc-post.Rev
		echo 'for (i in 1:num_branches) {' >> jc-post.Rev
    	echo '	bl[i] ~ dnExponential(10.0)' >> jc-post.Rev
    	echo '	moves.append( mvScale(bl[i]) )' >> jc-post.Rev
		echo '}' >> jc-post.Rev
		echo '' >> jc-post.Rev
		echo 'TL := sum(bl)' >> jc-post.Rev
		echo '' >> jc-post.Rev
		echo 'psi := treeAssembly(topology, bl)' >> jc-post.Rev
		echo '' >> jc-post.Rev
		echo '###################' >> jc-post.Rev
		echo '# PhyloCTMC Model #' >> jc-post.Rev
		echo '###################' >> jc-post.Rev
		echo '' >> jc-post.Rev
		echo '# the sequence evolution model' >> jc-post.Rev
		echo 'seq ~ dnPhyloCTMC(tree=psi, Q=Q, type="DNA")' >> jc-post.Rev
		echo '# attach the data' >> jc-post.Rev
		echo 'seq.clamp(data)' >> jc-post.Rev
		echo '' >> jc-post.Rev
		echo '############' >> jc-post.Rev
		echo '# Analysis #' >> jc-post.Rev
		echo '############' >> jc-post.Rev
		echo '' >> jc-post.Rev
		echo 'mymodel = model(Q)' >> jc-post.Rev
		echo '' >> jc-post.Rev
		echo '# add monitors' >> jc-post.Rev
		echo 'monitors.append( mnModel(filename="output-posterior/gene$l.log", printgen=100) )' >> jc-post.Rev
		echo 'monitors.append( mnFile(filename="output-posterior/gene$l.trees", printgen=100, psi) )' >> jc-post.Rev
		echo 'monitors.append( mnScreen(printgen=100, TL) )' >> jc-post.Rev
		echo '' >> jc-post.Rev
		echo '# run the analysis' >> jc-post.Rev
		echo 'mymcmc = mcmc(mymodel, moves, monitors)' >> jc-post.Rev
		echo 'mymcmc.burnin(generations=10000,tuningInterval=100)' >> jc-post.Rev
		echo 'mymcmc.run(generations=100000)' >> jc-post.Rev
		echo '' >> jc-post.Rev
		echo '###################' >> jc-post.Rev
		echo '# Post processing #' >> jc-post.Rev
		echo '###################' >> jc-post.Rev
		echo '' >> jc-post.Rev
		echo '# you may want to quit RevBayes now' >> jc-post.Rev
		echo 'q()' >> jc-post.Rev


		echo '################################################################################' > jc-prior.Rev
		echo '#' >> jc-post.Rev
		echo '# RevBayes Example: Bayesian inference of phylogeny using a Jukes-Cantor' >> jc-prior.Rev
		echo '#            substitution model on a single gene.' >> jc-prior.Rev
		echo '#' >> jc-prior.Rev
		echo '# authors: Sebastian Hoehna, Michael Landis, and Tracy A. Heath' >> jc-prior.Rev
		echo '#' >> jc-prior.Rev
		echo '################################################################################' >> jc-prior.Rev
		echo '' >> jc-prior.Rev
		echo '' >> jc-prior.Rev
		echo '### Read in sequence data for both genes' >> jc-prior.Rev
		echo 'data = readDiscreteCharacterData("locus$l.nex")' >> jc-prior.Rev
		echo '' >> jc-prior.Rev
		echo '# Get some useful variables from the data. We need these later on.' >> jc-prior.Rev
		echo 'num_taxa <- data.ntaxa()' >> jc-prior.Rev
		echo 'num_branches <- 2 * num_taxa - 3' >> jc-prior.Rev
		echo 'taxa <- data.taxa()' >> jc-prior.Rev
		echo '' >> jc-prior.Rev
		echo 'moves    = VectorMoves()' >> jc-prior.Rev
		echo 'monitors = VectorMonitors()' >> jc-prior.Rev
		echo '' >> jc-prior.Rev
		echo '######################' >> jc-prior.Rev
		echo '# Substitution Model #' >> jc-prior.Rev
		echo '######################' >> jc-prior.Rev
		echo '' >> jc-prior.Rev
		echo '# create a constant variable for the rate matrix' >> jc-prior.Rev
		echo 'Q <- fnJC(4)' >> jc-prior.Rev
		echo '' >> jc-prior.Rev
		echo '##############' >> jc-prior.Rev
		echo '# Tree model #' >> jc-prior.Rev
		echo '##############' >> jc-prior.Rev
		echo '' >> jc-prior.Rev
		echo '# Prior distribution on the tree topology' >> jc-prior.Rev
		echo 'topology ~ dnUniformTopology(taxa)' >> jc-prior.Rev
		echo '' >> jc-prior.Rev
		echo 'moves.append( mvNNI(topology, weight=num_taxa) )' >> jc-prior.Rev
		echo 'moves.append( mvSPR(topology, weight=num_taxa/10) )' >> jc-prior.Rev
		echo '\n' >> jc-prior.Rev
		echo '# Branch length prior' >> jc-prior.Rev
		echo 'for (i in 1:num_branches) {' >> jc-prior.Rev
    	echo '	bl[i] ~ dnExponential(10.0)' >> jc-prior.Rev
    	echo '	moves.append( mvScale(bl[i]) )' >> jc-prior.Rev
		echo '}' >> jc-prior.Rev
		echo '' >> jc-prior.Rev
		echo 'TL := sum(bl)' >> jc-prior.Rev
		echo '' >> jc-prior.Rev
		echo 'psi := treeAssembly(topology, bl)' >> jc-prior.Rev
		echo '' >> jc-prior.Rev
		echo '###################' >> jc-prior.Rev
		echo '# PhyloCTMC Model #' >> jc-prior.Rev
		echo '###################' >> jc-prior.Rev
		echo '' >> jc-prior.Rev
		echo '# the sequence evolution model' >> jc-prior.Rev
		echo 'seq ~ dnPhyloCTMC(tree=psi, Q=Q, type="DNA")' >> jc-prior.Rev
		echo '# attach the data' >> jc-prior.Rev
		echo 'seq.clamp(data)' >> jc-prior.Rev
		echo '' >> jc-prior.Rev
		echo '############' >> jc-prior.Rev
		echo '# Analysis #' >> jc-prior.Rev
		echo '############' >> jc-prior.Rev
		echo '' >> jc-prior.Rev
		echo 'mymodel = model(Q)' >> jc-prior.Rev
		echo 'mymodel.ignoreAllData()' >> jc-prior.Rev
		echo '' >> jc-prior.Rev
		echo '# add monitors' >> jc-prior.Rev
		echo 'monitors.append( mnModel(filename="output-prior/gene$l.log", printgen=100) )' >> jc-prior.Rev
		echo 'monitors.append( mnFile(filename="output-prior/gene$l.trees", printgen=100, psi) )' >> jc-prior.Rev
		echo 'monitors.append( mnScreen(printgen=100, TL) )' >> jc-prior.Rev
		echo '' >> jc-prior.Rev
		echo '# run the analysis' >> jc-prior.Rev
		echo 'mymcmc = mcmc(mymodel, moves, monitors)' >> jc-prior.Rev
		echo 'mymcmc.burnin(generations=10000,tuningInterval=100)' >> jc-prior.Rev
		echo 'mymcmc.run(generations=100000)' >> jc-prior.Rev
		echo '' >> jc-prior.Rev
		echo '###################' >> jc-prior.Rev
		echo '# Post processing #' >> jc-prior.Rev
		echo '###################' >> jc-prior.Rev
		echo '' >> jc-prior.Rev
		echo '# you may want to quit RevBayes now' >> jc-prior.Rev
		echo 'q()' >> jc-prior.Rev


		cd ..
	done
	cd ../..
done
