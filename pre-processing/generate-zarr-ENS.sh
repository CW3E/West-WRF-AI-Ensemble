#!/bin/bash
#SBATCH --account=cwp179
#SBATCH --partition=shared-128
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --mem=12G
#SBATCH --array=0-4
#SBATCH --time=10:00:00
#SBATCH --export=ALL
#SBATCH --job-name=ENS2zarr
#SBATCH --output=../logs/ENS2zarr_%A_%a.log

starts=(0 10 20 30 40)
ends=(9 19 29 39 50)
start=${starts[$SLURM_ARRAY_TASK_ID]}
end=${ends[$SLURM_ARRAY_TASK_ID]}

dates=()
start_date="YYYYMMDD"  
end_date="YYYYMMDD"
current_date="$start_date"
while [[ "$current_date" != $(date -I -d "$end_date + 1 day") ]]; do
    dates+=("$(date -d "$current_date" +"%Y%m%d")")
    current_date=$(date -I -d "$current_date + 1 day")
done


for date in "${dates[@]}"; do
    echo "Processing date: $date"

    date1=$(date -d "$date" +"%Y-%m-%d")
    echo $date1

    for i in $(seq $start $end); do
        
        num=$(printf "%02d" $i)
        
        # generate yaml and zarr file names
        new_yaml="yaml/generate-zarr-ENS_${i}.yaml"
        mkdir -p /path/to/your/ens_data/zarr/$date
        zarr_31km="/path/to/your/ens_data/zarr/$date/ENS-31km-$date-${num}.zarr"
        zarr_6km="/path/to/your/ens_data/zarr/$date/ENS-6km-$date-${num}.zarr"

        cp generate-zarr-ENS.yaml $new_yaml 
        sed -i "s/_0.nc/_$i.nc/g" $new_yaml

        # Modify the date in the yaml template file
        sed -i "s/20250101/$date/g" $new_yaml 
        sed -i "s/2025-01-01/$date1/g" $new_yaml 

        # generate the 31km zarr file 
        anemoi-datasets create $new_yaml $zarr_31km --overwrite

        # Modify the zarr file name in the yaml file
        sed -i "s/_31km/_6km/g" $new_yaml 
        sed -i "s/_"$i".nc/_"$i"_rotated.nc/g" $new_yaml  

        # generate the 6km zarr file 
        anemoi-datasets create $new_yaml $zarr_6km --overwrite

    done

done

# 0.5 hour for 1 day?
# time=15:00:00 for 1 month 
