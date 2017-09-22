#!/bin/bash

#This script formats CoDL metadata downloaded from VAMPS2

sIODir=$1
sJavaDir=$2

cd $sIODir

#decompressing raw metadata
cd raw_metadata
rm -rf '__MACOSX'
rm -f *.gz
unzip $sIODir/raw_metadata/codl_metadata.zip
rm -rf '__MACOSX'
cd $sIODir
for f in raw_metadata/*.gz
do
	gunzip -r $f
done

#converting files to tsv
for f in raw_metadata/*.csv
do
	sName=`basename $f`
	mv $f $sName
	sed -i "s|\,|\;|g" $sName
	sed -i "s|\t|\,|g" $sName
done

#fixing errors in files
sFile='metadata-samples_in_rows1505847186991_DCO_LAV_Bv6v4.csv'
head --lines=1 $sFile | cut -d\, -f1-76 > 'metadata-samples_in_rows1505847186991_DCO_LAV_Bv6v4_edited.csv'
grep 'DCO_' $sFile >> 'metadata-samples_in_rows1505847186991_DCO_LAV_Bv6v4_edited.csv'
rm $sFile

sFile='metadata-samples_in_rows1505847207792_DCO_LAV_Av6v4.csv'
head --lines=1 $sFile | cut -d\, -f1-76 > 'metadata-samples_in_rows1505847207792_DCO_LAV_Av6v4_edited.csv'
grep 'DCO_' $sFile >> 'metadata-samples_in_rows1505847207792_DCO_LAV_Av6v4_edited.csv'
rm $sFile

#concatenating files
echo 'PROJECT_ID,SAMPLE_ID,VARIABLE,VALUE' > temp.2.txt
for f in metadata-samples*.csv
do

	sFile=${f/\.tsv/}
	echo 'Analyzing '$sFile'...' 
	head --lines=1 $f > temp.7.txt
	
	#selecting usable samples and fixing headers
	grep "DCO_" $f >> temp.7.txt
	sed -i "s|^\,|SAMPLE_ID\,|g" temp.7.txt

	#flattening file
	lstColumnsToFlatten=`head --lines=1 temp.7.txt | sed "s|SAMPLE_ID\,||g"`	
	java -cp $sJavaDir/Utilities.jar edu.ucsf.PivotTableToFlatFile.PivotTableToFlatFileLauncher \
		--lstColumnsToFlatten="$lstColumnsToFlatten" \
		--sDataPath=$sIODir/temp.7.txt \
		--sOutputPath=$sIODir/temp.6.txt
	paste -d\, <(tail -n+2 temp.6.txt | cut -d\_ -f1-2) <(tail -n+2 temp.6.txt) >> temp.2.txt
done
mv temp.2.txt temp.2.csv

#correcting empty cells
sed -i "s|\,$|\,null|g" temp.2.csv

#flattedning interpolated values file
lstColumnsToFlatten=`head --lines=1 raw_supplementary_metadata/metadata_minimal_pivot_selected_2017-09-20.csv | sed "s|PROJECT_ID\,SAMPLE_ID\,||g"`
java -cp $sJavaDir/Utilities.jar edu.ucsf.PivotTableToFlatFile.PivotTableToFlatFileLauncher \
	--sDataPath=$sIODir/raw_supplementary_metadata/metadata_minimal_pivot_selected_2017-09-20.csv \
	--lstColumnsToFlatten=$lstColumnsToFlatten \
	--sOutputPath=$sIODir/temp.3.csv
sed -i "s|FLAT_VAR_KEY\,FLAT_VAR_VALUE|VARIABLE\,VALUE|g" temp.3.csv


#appending blank_or_control field
grep 'blank_or_control' temp.3.csv | sed "s|blank_or_control|blank_or_control\,null|g" >> temp.2.csv

#standardizing null values
sed -i -e "s|unknown|null|g" -e "s|undefined|null|g" -e "s|\,\,|\,null\,|g" -e "s|None|null|g" temp.3.csv
sed -i -e "s|unknown|null|g" -e "s|undefined|null|g" -e "s|\,\,|\,null\,|g" -e "s|None|null|g" temp.2.csv

#joining interpolated values
java -cp $sJavaDir/Utilities.jar edu.ucsf.JoinTables.JoinTablesLauncher \
	--sBaseDataPath=$sIODir/temp.2.csv \
	--sAppendDataPath=$sIODir/temp.3.csv \
	--rgsBaseKeys='PROJECT_ID,SAMPLE_ID,VARIABLE' \
	--rgsAppendKeys='PROJECT_ID,SAMPLE_ID,VARIABLE' \
	--rgsAppendValues='VALUE' \
	--sOutputPath=$sIODir/temp.1.csv
sed -i -e "s|VALUE|VALUE_0|" -e "s|\,\-9999$|\,null|g" temp.1.csv

#adding interpolated values (priority is given to values input by the investigators)
rm -f temp.4.db
sqlite3 temp.4.db ".import $sIODir/temp.1.csv tbl1"
echo 'PROJECT_ID,SAMPLE_ID,VARIABLE,VALUE' > temp.5.csv
sqlite3 temp.4.db "select PROJECT_ID, SAMPLE_ID, VARIABLE, VALUE_0 from tbl1 where not(VALUE_0='null') or VALUE='null';" | tail -n+3 >> temp.5.csv
i1=`wc -l temp.5.csv | cut -d' ' -f1`
sqlite3 temp.4.db "select PROJECT_ID, SAMPLE_ID, VARIABLE, VALUE from tbl1 where VALUE_0='null' and not(VALUE='null');" | tail -n+3 >> temp.5.csv
i2=`wc -l temp.5.csv | cut -d' ' -f1`

echo $(($i2-$i1))'  interpolated records added'
mv temp.5.csv formatted_metadata/metadata_formatted.csv

#importing formatted metadata to database
rm -f formatted_metadata/metadata_formatted.db
sqlite3 formatted_metadata/metadata_formatted.db ".import $sIODir/formatted_metadata/metadata_formatted.csv tbl1"

#cleaning up
rm -f *.txt
rm -f metadata-*.csv
rm -f temp.*
