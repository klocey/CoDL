#!/bin/bash

#This script adds brz metadata to the output from format-metadata.sh (formatted-metadata.csv and formatted-metadata.db)

sIODir=$1
sJavaDir=$2

cd $sIODir

#cleaning dos formatting from file and renaming headers
cp raw_supplementary_metadata/metadata-samples_in_rows1504148199831_DCO_BRZ_Bv4v5_KIT.csv temp.0.csv
sed -i "s|\r||g" temp.0.csv
head --lines=1 temp.0.csv | cut -d\, -f2- | sed -e "s|^|PROJECT_ID\,SAMPLE_ID\,|g" -e "s|Temp\ (C)|temperature|g" > temp.4.csv
tail -n+2 temp.0.csv | sed "s|^|DCO_BRZ\,|g" >> temp.4.csv

#appending blank or control field and enriched field
sed -i -e "1 s|$|\,blank_or_control|g" -e "2,$ s|$|\,FALSE|g" temp.4.csv
sed -i -e "1 s|$|\,enrichment|g" -e "2,$ s|$|\,FALSE|g" temp.4.csv

#flattening brz metadata
lstColumnsToFlatten=`head --lines=1 temp.4.csv | sed "s|PROJECT_ID\,SAMPLE_ID\,||g"`
java -cp $sJavaDir/Utilities.jar edu.ucsf.PivotTableToFlatFile.PivotTableToFlatFileLauncher \
	--lstColumnsToFlatten="$lstColumnsToFlatten" \
	--sDataPath=$sIODir/temp.4.csv \
	--sOutputPath=$sIODir/temp.1.csv

#loading brz records to consider (brz samples with metadata in vamps may be omitted
sqlite3 formatted_metadata/metadata_formatted.db "select * from tbl1 where project_id='DCO_BRZ';" | tail -n+2 > temp.2.csv
java -cp $sJavaDir/Utilities.jar edu.ucsf.JoinTables.JoinTablesLauncher \
	--sBaseDataPath=$sIODir/temp.2.csv \
	--sAppendDataPath=$sIODir/temp.1.csv \
	--rgsBaseKeys='PROJECT_ID,SAMPLE_ID,VARIABLE' \
	--rgsAppendKeys='PROJECT_ID,SAMPLE_ID,FLAT_VAR_KEY' \
	--rgsAppendValues='FLAT_VAR_VALUE' \
	--sOutputPath=$sIODir/temp.3.csv
cut -d\, -f1-3,5 temp.3.csv | sed "s|FLAT_VAR_VALUE|VALUE|g" > temp.5.csv
sed -i "s|\,-9999$|\,null|g" temp.5.csv

#appending to formatted metadata
sqlite3 formatted_metadata/metadata_formatted.db "select * from tbl1 where not(project_id='DCO_BRZ');" | tail -n+3 >> temp.5.csv
rm -f temp.6.db
sqlite3 temp.6.db ".import $sIODir/temp.5.csv tbl1"

#replacing old metadata
mv temp.6.db formatted_metadata/metadata_formatted.db
mv temp.5.csv formatted_metadata/metadata_formatted.csv

#cleaning up
rm $sIODir/temp.*.csv
