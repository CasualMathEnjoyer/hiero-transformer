#!/bin/bash

#PBS -N hiero_transformer_training
#PBS -l walltime=24:00:00
#PBS -q gpu
#PBS -j oe
#PBS -l select=1:mem=32G:ncpus=8:ngpus=1

cd $PBS_O_WORKDIR

module load cuda/12.4.1

source /mnt/lustre/helios-home/morovkat/miniconda3/etc/profile.d/conda.sh
conda activate hiero-transformer

cd /mnt/lustre/helios-home/morovkat/hiero-transformer

python train_minimal.py

