# BalticAIMS QGIS plugin

A plugin for [QGIS](https://qgis.org/) to load [Xcube](https://github.com/xcube-dev/xcube) datasets from an xcube server.
The plugin is being developed for ESA's [BalticAIMS](https://eo4society.esa.int/projects/balticaims/) project.

# Installation

## Windows

The Plugin relies on the [Xcube](https://github.com/xcube-dev/xcube) Python package, which is not distributed with the plugin.

In order to use the BalticAIMS QGIS plugin, the Python virtual environment, including Xcube, must be installed and configured for QGIS to use.

On Windows, you can use the install scripts provided with the release, to:

1) setup the environment (`setup.bat`), done only once on installation
2) run the QGIS version configured with the correct Python virtual environment (`run_qgis_with_xcube.bat`), every time you want to use the plugin
.

After the setup has been completed, you can install the plugin  using "Install from Zip" in the [QGIS Plugin Manager](https://docs.qgis.org/3.40/en/docs/training_manual/qgis_plugins/fetching_plugins.html). Simply select the plugin `balticaims.<version>.zip` zip file in the dialog, which is contained in the release archive together with the installation scripts.
Please make sure to not select the release archive (which you can download from this repository), but the QGIS plugin zip `balticaims.<version>.zip`, which is contained in the release archive and can be accessed after unzipping the archive.

### Steps

1) Download the relase to the directory where you would like to install the Python environment
2) Unzip the archive
3) Run (by double click) the `setup.bat` script to install the Python environment. This will take several minutes. Please be aware that the script will not produce text output for a few minutes shortly after launch. Please be patient!
4) Run (double click) the `run_qgis_with_xcube.bat` script to launch QGIS. QGIS' Python interpreter should now be configured to support the plugin
5) Install the plugin using QGIS' Plugin Manager, if you didn't already

# Notes

- If the plugin is installed, you may encounter an error when launching QGIS normally, without running `run_qgis_with_xcube.bat`. You can ignore this error, but the plugin will not work.
- You can verify that the Python environment is configured correctly, by opening the [Python Console](https://docs.qgis.org/3.40/en/docs/user_manual/plugins/python_console.html) in QGIS and running `import xcube`. If no error is thrown, the environment is working correctly.
- The scripts `setup.bat` and `run_qgis_with_xcube.bat` must remain next to the other files distributed with the release and created by running `setup.bat`. Do not move the scripts to another location, or they will stop working. You can create a Desktop shortcut, if you wish.
