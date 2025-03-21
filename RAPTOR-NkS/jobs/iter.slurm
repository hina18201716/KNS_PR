#!/bin/bash
# --------------------
### Directives Section
# --------------------
#SBATCH --job-name=NkSvaryI
#SBATCH --account=chanc
#SBATCH --partition=standard
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --time=00:30:00
#SBATCH --array=1-3
# --------------------
### Code Section
# --------------------

#download module
module load hdf5

#define path to the code
export RAPTOR=/home/u16/hinas/raptor/RAPTOR-NkS
cd ..

# run RAPTOR with 1000 resolution
./RAPTOR modelscr/model${SLURM_ARRAY_TASK_ID}.in data0200.dat ${SLURM_ARRAY_TASK_ID}








