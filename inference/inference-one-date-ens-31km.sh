#!/bin/bash 
#SBATCH --account=bduu-dtai-gh
#SBATCH --job-name=AI31km
#SBATCH --partition=ghx4
#SBATCH --mem=96G
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --gpus-per-node=1
#SBATCH --gpus-per-task=1
#SBATCH --cpus-per-task=4
#SBATCH --array=0-3
#SBATCH --time=5:00:00
#SBATCH --output=../logs/ENS_%A_%a.log
#SBATCH --error=../logs/ENS_%A_%a.err
##SBATCH --output=../logs/ENS_%j.log
##SBATCH --error=../logs/ENS_%j.err

## Info here: https://docs.ncsa.illinois.edu/systems/deltaai/en/latest/user-guide/running-jobs.html

## Working directory
workdir=/path/to/your/inference/GLOBAL-31km/scripts/
cd ${workdir}

## Load conda environment
source /path/to/your/anaconda3/etc/profile.d/conda.sh
conda activate /path/to/your/envs/regional-ai

## Parameters
version=A2
lead_time=174 
date_start=YYYYMMDD
date_end=YYYYMMDD
date_step_days=1

dates=()
current_date="$date_start"
while [[ "$current_date" -le "$date_end" ]]; do
    dates+=("$current_date")
    current_date=$(date -d "${current_date} +${date_step_days} day" +"%Y%m%d")
done

epoch=${epochs[$SLURM_ARRAY_TASK_ID]}
echo "Processing EPOCH $epoch"

for date in "${dates[@]}"; do
    date1=$(date -d "$date" +"%Y-%m-%d")
    date1=$date1"T06:00:00"
    echo "Processing date $date ($date1)"

    mkdir -p /path/to/your/outputs/ENS/$date/epoch$epoch
    mkdir -p configs/ENS/"$version"/epoch$epoch

    echo "Running GLOBAL model (31km) at EPOCH $epoch to generate a $lead_time-hour forecast with initial condition: $date1."

    for member in {0..50}; do  # 50
        member=$(printf "%02d" $member)
        echo "Member $member"

        # generate a config file for anemoi-inference
        cat > configs/ENS/"$version"/epoch$epoch/config_${member}.yaml <<EOF
checkpoint: /path/to/your/models/$version/B2-epoch$epoch.ckpt
date: $date1
lead_time: $lead_time
# time_step: 6
input:
    dataset: /path/to/your/data/zarrs/$date/ENS-31km-$date-${member}.zarr

output:
    netcdf: /path/to/your/outputs/ENS/$date/epoch$epoch/ENS-epoch$epoch-$date-${member}.nc

patch_metadata:
    dataset:
        constant_fields: [z_sfc, lsm]
EOF

        if [ ! -f ../outputs/ENS/$date/epoch$epoch/ENS-epoch$epoch-$date-subset-${member}.nc ]; then

            anemoi-inference run configs/ENS/"$version"/epoch$epoch/config_${member}.yaml

            python extract_variables_31km.py $epoch $date $member

            rm /path/to/your/outputs/ENS/$date/epoch$epoch/ENS-epoch$epoch-$date-${member}.nc

        else
            echo "File already exists, skipping inference for member $member"
        fi

    done

    echo "Completed processing EPOCH $epoch for date $date"
done


echo "All epochs and dates processed successfully!"

