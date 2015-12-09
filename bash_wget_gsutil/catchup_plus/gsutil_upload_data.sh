#!/bin/bash   

export PATH=${PATH}:"/home/roman/program_files/gsutil"

sFilePath="/home/roman/dotModus/Data/Multichoice/big_data_group/CatchupPlus/data/"
sFileBase="$1"
sFiles=$"${sFileBase}*.csv.gz"

sDataPath=$"${sFilePath}${sFiles}"
sGooglePath="gs://mc-big_data-raw/catchup_plus"

now="$(date +"%Y-%m-%d %H:%M:%S")"
sLogPath="/home/roman/dotModus/Data/Multichoice/big_data_group/CatchupPlus/logs/upload_to_google.log"

    


function clean_paths {
    #remove path from filenames
    sOnlineFiles=$(gsutil ls ${sGooglePath} | grep ${sFileBase})
    sLocalFiles=$(ls ${sFilePath} | grep ${sFileBase})
    
    a=()
    for sItem in ${sOnlineFiles[@]}
    do
        sOnline=$(awk -F "/" '{print $NF}' <<< ${sItem})
        sItem=$sOnline
        a+=${sItem}" "
    done
    sOnlineFiles=${a}
}


function get_pushed {
    #get list of files that have been pushed already
    
    clean_paths
    
    for sLocal in ${sLocalFiles[@]}
    do
        x="0"
        for sOnline in $sOnlineFiles
        do
            if [ "$sOnline" == "$sLocal" ]; then
                x+="1"
            fi
        done
        
        if [ ${x} != "0" ]
        then
            echo $sLocal
        fi
    done
}


function get_unpushed {
    #get list of files that have been pushed already
    
    clean_paths
    
    for sLocal in ${sLocalFiles[@]}
    do
        x="0"
        for sOnline in $sOnlineFiles
        do
            if [ "$sOnline" == "$sLocal" ]; then
                x+="1"
            fi
        done
        
        if [ ${x} == "0" ]
        then
            echo $sLocal
        fi
    done
}



echo ${now} >> ${sLogPath}
echo "    Files needing to be pushed:" >> ${sLogPath}
get_unpushed >> ${sLogPath}
echo "    Files already on server, not pushing:" >> ${sLogPath}
get_pushed >> ${sLogPath}

gsutil cp -n ${sDataPath} ${sGooglePath}


sUnpushed=$(get_unpushed)
if [ "${sUnpushed}" == "" ]
then
    echo "+++++++Server is up to date with all files from local." >> ${sLogPath}
else
    echo "-------Something happened.  Files not pushed:   ${sUnpushed}" >> ${sLogPath}
fi

echo " " >> ${sLogPath}









