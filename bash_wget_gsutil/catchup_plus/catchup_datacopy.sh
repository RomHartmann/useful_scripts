#!/bin/bash   


#TODO no sudo on db

fileBase="CatchUpPlusActivity_20"     # xxxx* - all files starting with filebase downloaded


function get_online {
    #get all files on google server
    export PATH=${PATH}:"/home/roman/program_files/gsutil"  
    googlePath="gs://mc-big_data-raw/catchup_plus"
    onlineFiles=$(gsutil ls ${googlePath} | grep ${fileBase})

    #remove online path from filenames
    a=()
    for item in ${onlineFiles[@]}
    do
        name=$(awk -F "/" '{print $NF}' <<< ${item})
        a+=${name}"$1"
    done
    echo ${a::-1}
}

onlineFiles=$(get_online ",")

. wget_data.sh ${fileBase} ${onlineFiles}
. gsutil_upload_data.sh ${fileBase}


#remove local files that are on the server
onlineFiles=$(get_online " ")

for server in ${onlineFiles[@]}
do
    sudo rm data/${server}
    echo "data/${server} removed"
done










#.