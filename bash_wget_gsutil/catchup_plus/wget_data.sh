#!/bin/bash   

sCurrentDir=$(pwd)


sLocalPath="/home/roman/dotModus/Data/Multichoice/big_data_group/CatchupPlus/data"


sFTPPath="ftp://bigdata:U5WJmgphML1kC8H@10.10.23.32/public/download/exports/webactivity/PullVODData/"
sFileBase="$1"
sFiles=$"${sFileBase}*.csv.gz"
sDataPath=$"${sFTPPath}${sFiles}"

sExcludeFiles="$2"

now="$(date +"%Y-%m-%d %H:%M:%S")"
sLogPath="/home/roman/dotModus/Data/Multichoice/big_data_group/CatchupPlus/logs/download_from_server.log"

# sFTPFiles=$("wget --no-remove-listing "${sFTPPath} | grep ${sFileBase})
# sLocalFilesBefore=$(ls ${sLocalPath} | grep ${sFileBase})

echo ${sFTPFiles}

cd ${sLocalPath}
echo ${sExcludeFiles}
sudo wget ${sDataPath} --reject ${sExcludeFiles} -nc 
# sudo wget ${sDataPath} -nc
cd ${sCurrentDir}


sLocalFilesAfter=$(ls ${sLocalPath} | grep ${sFileBase})



function get_pulled {
    #get list of files that were there only after
    
    for sAfter in ${sLocalFilesAfter[@]}
    do
        x="0"
        for sBefore in ${sLocalFilesBefore[@]}
        do
            if [ "$sBefore" == "$sAfter" ]; then
                x+="1"
            fi
        done
        
        if [ ${x} == "0" ]
        then
            echo $sAfter
        fi
    done
}



function get_unpulled {
    #get list of files that were only there before and after
    
    for sAfter in ${sLocalFilesAfter[@]}
    do
        x="0"
        for sBefore in ${sLocalFilesBefore[@]}
        do
            if [ "$sBefore" == "$sAfter" ]; then
                x+="1"
            fi
        done
        
        if [ ${x} != "0" ]
        then
            echo $sAfter
        fi
    done
}



echo ${now} >> ${sLogPath}
echo "   +Files successfully pulled to local (or already on server):" >> ${sLogPath}
get_pulled >> ${sLogPath}
echo "   -Files already on local, not pulled:" >> ${sLogPath}
get_unpulled >> ${sLogPath}
echo " " >> ${sLogPath}








