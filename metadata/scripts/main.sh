#!/bin/bash

sIODir=/home/jladau/Desktop/Research/Java/Distribution/CoDL/metadata
sJavaDir=$sIODir/bin
sBIOMPath=/home/jladau/Desktop/Data/Microbial_Community_Samples/Subsurface.Global.BacteriaArchaea.CoDL.biom
sUtilitiesDir=/home/jladau/Desktop/Utilities

mkdir -p $sIODir/formatted_metadata

<<COMMENT0

#formatting metadata
bash $sIODir/scripts/format-metadata.sh $sIODir $sJavaDir

#counting metadata
bash $sIODir/scripts/metadata-counts.sh $sIODir $sJavaDir

#outputting wishlist table
bash $sIODir/scripts/metadata-wishlist-table.sh $sIODir $sJavaDir

#outputting minimal table
bash $sIODir/scripts/metadata-minimal-table.sh $sIODir $sJavaDir

#outputting blank and control list
bash $sIODir/scripts/metadata-blanks-controls-list.sh $sIODir $sJavaDir

#organizing formatted metadata
bash $sIODir/scripts/organize-formatted-metadata.sh $sIODir $sJavaDir

COMMENT0

#making metadata for mapping
bash $sIODir/scripts/mapping-metadata.sh $sIODir $sJavaDir $sBIOMPath $sUtilitiesDir


