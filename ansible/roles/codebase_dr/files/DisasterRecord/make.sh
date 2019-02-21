#!/bin/bash
#make.sh

#########################PARAMETERS###############################################

#File path with Data containing JSON structured tweets with metadata
#Can be left empty if you intend to crawl through keywords
#Example, './_Data/tweets.json'
DATA_JSON_URL="IRMA"

#Tweepy credentials:
#Can be left empty if you intend to read from file
Consumer_Key="AGdM9YV89pVK6KJlbRss1CdOB"
Consumer_Secret="GGdsC5NOCt4W6jmp6tTcXwjMmxzPACVxGopuIL1u1Krt95U9Nz"
Access_Key="2941079587-vXRnSGS9GVJldDkqhH5XLFg0agrfRKjuuFFh2Vy"
Access_Secret="CLXzOmy9PfWtWCSRQ8gf0fgoRANSkEPDCEdx1YSDsI6iT"

#PORT of API
API_PORT=""

#Image classification of Flood/Non-Flood images
Flood_Check="ON"

#Object Detection from images - people,vehicles,animals
Object_Check="ON"

#Satellite image data - Flood mapping
Satellite="OFF"

#Campaign/Dataset name: disaster/region name of the crawl
Dataset="irma"

#################################INSTALLATIONS#########################################

#Install photon


#Install LNEx



#Install Flood-Image Classification


#Install Object detection


#Install requirements file


#############################Create mappings############################################

#File and tweepy records mapping
./file-mapping.sh $Dataset

#Processed tweets mapping
./tweet-mapping.sh $Dataset

#OpenStreetMap content mapping
./osm-mapping.sh $Dataset


#API mapping


#Geographical area of targetted area as a boundingbox
#[12.74, 80.066986084, 13.2823848224, 80.3464508057] - Chennai boundingbox
#Boundingbox=("39.1912856591" "-84.6447033333" "40.0880515857" "-83.2384533333")
#Boundingbox=("12.74" "80.066986084" "13.2823848224" "80.3464508057")
Boundingbox=("24.2176" "-83.2781" "27.04" "-79.6856")

#List of keywords to search from:
#Keywords=("WSU" "fighting4Wright")
Keywords=("Flood" "HurricaneFlorence" "Florence2018")

#if [ -z "$DATA_JSON_URL" ];
#then
#    #python prepare.py $Dataset $Flood_Check $Object_Check $Satellite "${Boundingbox[*]}" &
#    #echo "tweet collection....." &
#    python tweet_collection.py "${Keywords[*]}" $Consumer_Key $Consumer_Secret $Access_Key $Access_Secret $Dataset
#else
#    python prepare.py $Dataset $Flood_Check $Object_Check $Satellite "${Boundingbox[*]}" &
#    echo "reading tweets....."
#    python read_from_file.py $Dataset

#
#fi
#echo "${Keywords[*]}" "|" $Consumer_Key "|" $Consumer_Secret "|" $Access_Key "|" $Access_Secret "|" $Dataset "|" $Flood_Check "|" $Object_Check "|" $Satellite "|" "${Boundingbox[*]}" "|" $DATA_JSON_URL
python core.py "${Keywords[*]}" $Consumer_Key $Consumer_Secret $Access_Key $Access_Secret $Dataset $Flood_Check $Object_Check $Satellite "${Boundingbox[*]}" $DATA_JSON_URL