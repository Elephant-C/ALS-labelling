library(lidR)
library(geojsonsf)
library(sf)

#' Fit concave boundary for core area, which will be further used as assessment area for ITS algorithm ccomparison
#' @name fit_boundary
#' @param tls_las_path character. Input path for terrestrial lidar point clouds.
#' @param hull_path character. Export path for fitted concave hull.
#' @param n_params list or numeric. n_params can be: 1,2,3, ... ,10. choose a optimal n_params for your case.
#' If you're not sure about this, you can search in the parameter space and then visualize the concave hull.
fit_boundary <- function(tls_las_path, hull_path)

  {
  # check current dir
  print(tls_las_path)
  tls_las_data <- lidR::readLAS(tls_las_path)
  n_params <- c(1) 
  for (n in n_params){
    hull <- st_concave_hull(tls_las_data, length_threshold=n)
    # visualize concave hull
    plot(hull)
  }
  st_write(hull, hull_path)
  print('Core area boundary fitting complete...')
  return(hull)
}


#' Crop core area point clouds with fitted concave hull from fit_boundary function
#' @name coreArea_crop
#' @param als_las_path character. Path for airborne LiDAR point clouds to be cropped
#' @param hul_shp shp. Concave hull used to crop corea area point clouds
#' @param outpath character. Export path for cropped airborne LiDAR point clouds
coreArea_crop <- function(als_las_path, hull_shp, outpath){
  las <- lidR::readLAS(als_las_path)
  clipped_area <- clip_roi(las, hull_shp)
  plot(clipped_area, color='PointSourceID')
  X = clipped_area@data$X
  Y = clipped_area@data$Y
  Z = clipped_area@data$Z
  ID = clipped_area@data$PointSourceID
  outdata = data.frame(X, Y, Z, ID)
  write.csv(outdata, outpath)
  print('Complete')
  return(outdata)
}


#' Normalize terrain for core area point clouds
#' @name terrain_normalization
#' @param las_tobe_normalized_path character. Path for point clouds to be normalized.
#' @param outpath character. Export path for normalized point clouds.
terrain_normalization <- function(las_tobe_normalized_path, outpath){
  las <- lidR::readLAS(las_tobe_normalized_path)
  print(las)
  # ground filtering
  csf_prede <- lidR::csf(sloop_smooth = TRUE, class_threshold = 0.8, cloth_resolution = 0.5, time_step = 1)
  las <- classify_ground(las, csf_prede)
  plot(las, color = "Classification", size = 1, bg = "white")
  gnd <- filter_ground(las)
  plot(gnd, size = 2, bg = "white")
  dtm_tin <- rasterize_terrain(las, res = 1, algorithm = tin())
  plot_dtm3d(dtm_tin, bg = "white")
  plot(dtm_tin, col = gray(1:50/50))
  # terrain normalization
  nlas <- las - dtm_tin
  print(nlas)
  # visualize normalized data
  plot(nlas, size = 1, bg = "white")
  write.csv(output, expo_path)
  print('Terrain normalization complete...')
}

#' Execute function to implement the pipeline
#' @name main
#' @param tls_las_path character.
#' @param als_las_path character.
#' @param hull_path character.
#' @param coreArea_las_path character.
main <- function(tls_las_path, als_las_path, hull_path, coreArea_las_path){
  hull <- fit_boundary(tls_las_path=tls_las_path, hull_path = hull_path)
  coreArea_df <- coreArea_crop(als_las_path = als_las_path, hull_shp = hull, outpath = coreArea_las_path)
  print('Complete....')
}