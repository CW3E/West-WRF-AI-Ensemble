#!/bin/bash
#SBATCH --account=cwp179
#SBATCH --partition=shared-128
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1  # 4
#SBATCH --mem=32G  # 64G
#SBATCH --array=0-12
#SBATCH --time=2:00:00
#SBATCH --export=ALL
#SBATCH --job-name=ENS2netcdf
#SBATCH --output=../logs/ENS2netcdf_%A_%a.log

# export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK

source /home/yanie/anaconda3/etc/profile.d/conda.sh
conda activate cdo_env

# Define list of dates to process
dates=()
start_date="YYYYMMDD"
end_date="YYYYMMDD"
current_date="$start_date"
while [[ "$current_date" != $(date -I -d "$end_date + 1 day") ]]; do
    dates+=("$(date -d "$current_date" +"%Y%m%d")")
    current_date=$(date -I -d "$current_date + 1 day")
done

# Loop through each date sequentially
for date in "${dates[@]}"; do
    echo "Processing date: $date"
    
    mkdir -p /path/to/your/ens_data/netcdf/"$date"
    
    echo "Starting processing for $date at $(date)"
    python ens_preprocess_multithread.py $date
    
    if [ $? -eq 0 ]; then
        echo "Successfully completed processing for $date at $(date)"
    else
        echo "Error processing $date at $(date)"
        exit 1
    fi
    
    echo "Finished processing date: $date"
    echo "----------------------------------------"
done

echo "All dates processed!"

# rotate winds
starts=(0 4 8 12 16 20 24 28 32 36 40 44 48)
ends=(3 7 11 15 19 23 27 31 35 39 43 47 50)  # there are 51 members in total, the last group has 3 members
start=${starts[$SLURM_ARRAY_TASK_ID]}
end=${ends[$SLURM_ARRAY_TASK_ID]}

for date in "${dates[@]}"; do
    for i in $(seq $start $end); do
        date1=$(date -d "$date" +"%Y%m%d")
        cd /path/to/your/ens_data/netcdf/"$date"/
        cdo merge ENS_6km_"$date1"_"$i".nc ../sincos.nc temp_$i.nc
        cdo -aexpr,'vg=v*CosAlpha-u*SinAlpha' -aexpr,'ug=u*CosAlpha+v*SinAlpha' -aexpr,'10vg=10v*CosAlpha-10u*SinAlpha' -aexpr,'10ug=10u*CosAlpha+10v*SinAlpha' -aexpr,'ivt_vg=ivt_v*CosAlpha-ivt_u*SinAlpha' -aexpr,'ivt_ug=ivt_u*CosAlpha+ivt_v*SinAlpha' temp_$i.nc temp1_$i.nc
        cdo -delvar,u,v,10u,10v,ivt_u,ivt_v,SinAlpha,CosAlpha temp1_$i.nc temp2_$i.nc
        cdo -chname,ug,u -chname,vg,v -chname,10ug,10u -chname,10vg,10v -chname,ivt_ug,ivt_u -chname,ivt_vg,ivt_v temp2_$i.nc ENS_6km_"$date1"_"$i"_rotated.nc
        rm temp_$i.nc temp1_$i.nc temp2_$i.nc ENS_6km_"$date1"_"$i".nc
    done
done
