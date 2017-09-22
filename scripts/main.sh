#!/bin/bash

sIODir=/home/jladau/Desktop/Research/Java/Distribution/CoDL
sJavaDir=$sIODir/bin

mkdir -p $sIODir/formatted_metadata

#formatting metadata
bash $sIODir/scripts/format-metadata.sh $sIODir $sJavaDir

#counting metadata
bash $sIODir/scripts/metadata-counts.sh $sIODir $sJavaDir

#outputting wishlist table
bash $sIODir/scripts/metadata-wishlist-table.sh $sIODir $sJavaDir

#outputting minimal table
bash $sIODir/scripts/metadata-minimal-table.sh $sIODir $sJavaDir


