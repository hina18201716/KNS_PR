#!/bin/bash
# --------------------
### Directives Section
# --------------------
#SBATCH --job-name=NkSImaging_HLS
#SBATCH --account=chanc
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --time=09:00:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=hinas@arizona.edu
#SBATCH --output=HLS_IMG.out
#SBATCH --error=HLS_IMG.err

# --------------------
### Code Section
# --------------------

#download module
module load hdf5

#define path to the code
export RAPTOR=/home/u16/hinas/raptor/RAPTOR-NkS
cd ..

# run RAPTOR with 1000 resolution
./RAPTOR modelscr/model1000.in data0200.dat 1000


