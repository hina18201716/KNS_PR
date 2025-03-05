#!/bin/bash
# --------------------
### Directives Section
# --------------------
#SBATCH --job-name=NkSImaging_HLS
#SBATCH --account=chanc
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --time=01:00:00
# --------------------
### Code Section
# --------------------
module load hdf5
export RAPTOR=/home/u16/hinas/raptor/RAPTOR-NkS
./RAPTOR model.in data0200.dat 1000
