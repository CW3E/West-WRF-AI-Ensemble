import gc
from anemoi.datasets import open_dataset
def plot_n320(path_pred,
              path_target,
              var,
              ax,
              date,
              cmap='Reds',
              levels=None,
              title=None):
    ##### Load prediction #####
    ds_pred=xr.open_dataset(path_pred)[var]
    # Select a specific date
    ds_pred=ds_pred.sel(time=date).load()
    values_pred=ds_pred.values
    # Latitudes and longitudes
    longitudes_p=ds_pred.lon.values
    latitudes_p=ds_pred.lat.values
    ##### Load target (groundtruth) #####
    ds_target=open_dataset(path_target)
    # Select a specific date
    idx_var=ds_target.name_to_index[var]
    idx_time=np.where(ds_target.dates == date)[0][0]
    values_target=ds_target.data[idx_time, idx_var, 0, :]
    # Latitudes and longitudes
    longitudes_t=ds_pred.lon.values
    latitudes_t=ds_pred.lat.values
    ##### Plot #####
    # Levels?
    if levels is None:
        levels=np.linspace(values_target.min(), values_target.max(),21)
    # Plot (groundtruth)
    print("Plotting groundtruth..")
    triangulation = tri.Triangulation(longitudes_t, latitudes_t)
    fig_ = ax[0].tricontourf(triangulation, values_target, levels=levels, extend="both", transform=ccrs.PlateCarree(), cmap=cmap)
    ax[0].set_title("ERA5-31km: %s" % (var))
    # Plot (prediction)
    print("Plotting prediction..")
    triangulation = tri.Triangulation(longitudes_p, latitudes_p)
    fig_ = ax[1].tricontourf(triangulation, values_pred, levels=levels, extend="both", transform=ccrs.PlateCarree(), cmap=cmap)
    ax[1].set_title("AI-31km: %s" % (var))
    print("Done!")
    ##### Metadata of the plot #####
    for ax_ in ax:
        ax_.coastlines(linewidth=2)
        cbar=plt.colorbar(fig_, ax=ax_, fraction=0.035, pad=0.045, orientation="horizontal")
        cbar.set_label(var, rotation=0, labelpad=5, fontsize=10)
        cbar.ax.tick_params(labelsize=8)
    ##### Close xarray files #####
    ds_pred.close()
    del ds_pred, ds_target
    gc.collect()
    return None