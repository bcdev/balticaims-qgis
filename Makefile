.PHONY: all clean

PLUGIN_ROOT := balticaims
TOP_LEVEL_DIR = src
METADATA = "${TOP_LEVEL_DIR}/${PLUGIN_ROOT}/metadata.txt"
VERSION = $(shell grep "version" ${METADATA} | cut -d = -f 2)
ZIPFILE := ${PLUGIN_ROOT}.${VERSION}.zip
CURRENT_PATH = $(realpath .)
EXCLUDES = "**/__pycache__/*"

version:
	echo "Plugin version: ${VERSION}"

all: $(ZIPFILE)

$(ZIPFILE): $(TOP_LEVEL_DIR)/$(PLUGIN_ROOT) version
	(cd $(TOP_LEVEL_DIR) && zip -r $(CURRENT_PATH)/$(ZIPFILE) $(PLUGIN_ROOT) -x $(EXCLUDES) )

clean:
	rm -f $(ZIPFILE)

sync: $(ZIPFILE)
	rsync $< qgis:/var/www/qgis/plugins/${PLUGIN_ROOT}/version/${VERSION}/$<
