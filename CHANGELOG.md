# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Raster layers loaded by the plugin now display the unit of the measured variable in the legend an in the layer name.
- Download progress is shown in a progress bar.

### Changed

- Consistently use "data cube" (instead of "dataset") to refer to the entries of the xcube server "datasets" api in the UI. The term serves to distinguish cubes, with have at least a time dimension in addition to the spatial dimensions, from other raster data sets.
- The "Load layer" dialog informs the user that the cube slice must fit into RAM.

### Removed

### Deprecated

### Fixed

- The plugin no longer crashes when trying to load a layer without specifying a data cube first.
  Instead, a warning message is displayed.

### Security
