#!/bin/bash
mkdir -p \
    "data"

cd data

mkdir -p \
    "202223" \
    "202324" \
    "202425" \
    "202526"

cd "$DATA_DIR"

wget -nc https://data.riksdagen.se/dataset/votering/votering-202223.json.zip
wget -nc https://data.riksdagen.se/dataset/votering/votering-202324.json.zip
wget -nc https://data.riksdagen.se/dataset/votering/votering-202425.json.zip
wget -nc https://data.riksdagen.se/dataset/votering/votering-202526.json.zip

unzip -oq votering-202223.json.zip -d 202223
unzip -oq votering-202324.json.zip -d 202324
unzip -oq votering-202425.json.zip -d 202425
unzip -oq votering-202526.json.zip -d 202526

echo "Voting datasets ready."