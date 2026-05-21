#!/bin/bash 
#SBATCH --account=bduu-dtai-gh
#SBATCH --job-name=AI6km
#SBATCH --partition=ghx4
#SBATCH --mem=96G
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --gpus-per-node=1
#SBATCH --gpus-per-task=1
#SBATCH --cpus-per-task=8
#SBATCH --array=0-7
#SBATCH --time=4:30:00
#SBATCH --output=../logs/ENS_%A_%a.log
#SBATCH --error=../logs/ENS_%A_%a.err
##SBATCH --output=../logs/ENS_%j.log
##SBATCH --error=../logs/ENS_%j.err

## Info here: https://docs.ncsa.illinois.edu/systems/deltaai/en/latest/user-guide/running-jobs.html

## Working directory
workdir=/path/to/your/ens_data/inference/
cd ${workdir}

## Load conda environment
source /u/yanie/anaconda3/etc/profile.d/conda.sh
conda activate /projects/bduu/yanie/envs/regional-ai

## Parameters
version=v3
lead_time=174 
date=YYYYMMDD  
date1=$(date -d "$date" +"%Y-%m-%d")
date1=$date1"T06:00:00"
echo $date1

epochs=(0 1 2 3 4 5 6 7)  # Define list of epochs to process
epoch=${epochs[$SLURM_ARRAY_TASK_ID]}
echo "Processing EPOCH $epoch"

# mkdir -p ../outputs/ENS/$version/epoch$epoch/$date  
mkdir -p ../outputs/ENS/$version/$date/epoch$epoch  
mkdir -p configs/ENS/$version/epoch$epoch  

echo "Running STRETCHED model (6km) at EPOCH $epoch to generate a $lead_time-hour forecast with initial condition: $date1." 

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
  dataset:
    cutout:
      - dataset: /path/to/your/data/zarrs/$date/ENS-6km-$date-${member}.zarr
      - dataset: /path/to/your/data/zarrs/$date/ENS-31km-$date-${member}.zarr
    adjust: all
    min_distance_km: 3 

output: 
  netcdf: /path/to/your/outputs/ENS/$version/$date/epoch$epoch/ENS-$version-epoch$epoch-$date-${member}.nc  

patch_metadata:
  dataset:
    constant_fields: [z_sfc, lsm]
EOF

    if [ ! -f ../outputs/ENS/$version/$date/epoch$epoch/ENS-$version-epoch$epoch-$date-subset-${member}.nc ]; then
        
        anemoi-inference run configs/ENS/"$version"/epoch$epoch/config_${member}.yaml

        # Extract variables from the output file
        python extract_variables.py $version $epoch $date $member

        rm /path/to/your/outputs/ENS/$version/$date/epoch$epoch/ENS-$version-epoch$epoch-$date-${member}.nc
    
    else
        echo "File already exists, skipping inference for member $member"
    fi


done

echo "Completed processing EPOCH $epoch"

echo "All epochs processed successfully!"

