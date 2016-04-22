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
