#!/bin/bash

sIODir=/home/jladau/Desktop/Research/Java/Distribution/CoDL/metadata
sJavaDir=$sIODir/bin

mkdir -p $sIODir/formatted_metadata

#formatting metadata
bash $sIODir/scripts/format-metadata.sh $sIODir $sJavaDir

#adding brz metadata
bash $sIODir/scripts/add-brz-metadata.sh $sIODir $sJavaDir

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

