# program_autotuner
##how to write configuration file?  
###example:
run ./program  
compile g++ ../mmm_block.cpp -DBLOCK_SIZE={BLOCK_SIZE} -{OPT_FLAG} -o program -std=c++11  
parameter int BLOCK_SIZE 1 10  
parameter enum OPT_FLAG O1 O2 O3  
### Descripion  
Rules:

  * support int,enum,float parameters
  * before every file add ../
  * all parameter should be in brackets {}

## Availble techniques

  * PureRandom
  * ga-OX3
  * ga-OX1
  * ga-PX
  * ga-CX
  * ga-PMX
  * ga-base
  * UniformGreedyMutation05
  * UniformGreedyMutation10
  * UniformGreedyMutation20
  * NormalGreedyMutation05
  * NormalGreedyMutation10
  * NormalGreedyMutation20
  * DifferentialEvolution
  * DifferentialEvolutionAlt
  * DifferentialEvolution_20_100
  * RandomNelderMead
  * RegularNelderMead
  * RightNelderMead
  * MultiNelderMead
  * RandomTorczon
  * RegularTorczon
  * RightTorczon
  * MultiTorczon
  * PatternSearch
  * PseudoAnnealingSearch
  * pso-OX3
  * pso-OX1
  * pso-PMX
  * pso-PX
  * pso-CX
  * GGA
  * AUCBanditMutationTechnique
  * AUCBanditMetaTechniqueA
  * AUCBanditMetaTechniqueB
  * AUCBanditMetaTechniqueC
  * PSO_GA_Bandit
  * PSO_GA_DE
  * ComposableDiffEvolution
  * ComposableDiffEvolutionCX
