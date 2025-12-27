#!/bin/bash

#PBS -N hiero_transformer_training
#PBS -l walltime=24:00:00
#PBS -q gpu
#PBS -j oe
#PBS -l select=1:mem=32G:ncpus=8:ngpus=1

# Training configuration - edit these as needed
CHECKPOINT="checkpoint_total_steps=12000_loss=0.49"  # Path to checkpoint to continue from (leave empty to start fresh)
EPOCHS=20
BATCH_SIZE=16
EVAL_PERIOD=1000

cd $PBS_O_WORKDIR

module load cuda/12.4.1

source /mnt/lustre/helios-home/morovkat/miniconda3/etc/profile.d/conda.sh
conda activate hiero-transformer

cd /mnt/lustre/helios-home/morovkat/hiero-transformer

# Build command with arguments
CMD="python train_minimal.py --epochs $EPOCHS --batch_size $BATCH_SIZE --eval_period $EVAL_PERIOD"

if [ -n "$CHECKPOINT" ]; then
    CMD="$CMD --checkpoint $CHECKPOINT"
    echo "Continuing training from checkpoint: $CHECKPOINT"
else
    echo "Starting fresh training"
fi

echo "Running: $CMD"
$CMD

