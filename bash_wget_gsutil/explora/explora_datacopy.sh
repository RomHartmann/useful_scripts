#!/bin/bash   

#TODO edit for server and make not sudo if can

export PATH=${PATH}:"/home/roman/program_files/gsutil"

localpath="/home/roman/dotModus/Data/Multichoice/big_data_group/Explora/data/"
FTPpath="ftp://dmanalytics:jhoFgeXHWZCSZII@10.10.23.32/dmanalytics/download/"
googlepath="gs://mc-big_data-raw/explora"

nowDateTime="$(date +"%Y-%m-%d %H:%M:%S")"
nowDate="$(date +"%Y-%m-%d")"
sLogPath="/home/roman/dotModus/Data/Multichoice/big_data_group/Explora/logs/explora.log"


#replaces old files:
#copy from ftp
currentdir=$(pwd)
cd ${localpath}
sudo wget ${FTPpath}* -nc 
cd ${currentdir}

#copy to google
gsutil cp ${localpath}* ${googlepath} 




## #keep all old files
# #copy from ftp
# currentdir=$(pwd)
# cd ${localpath}
# mkdir ${nowDate}
# cd ${nowDate}
# sudo wget ${FTPpath}* -nc 
# cd ${currentdir}
# 
# gsutil cp -r ${localpath}* ${googlepath} 



#remove local
for file in $(ls ${localpath})
do
    sudo rm data/${file}
    echo "data/${file} removed"
done


#log
echo ${nowDateTime}":  "${nowDate}" Explora dmanalytics data uploaded" >> ${sLogPath}
