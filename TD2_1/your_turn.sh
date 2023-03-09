## Extract the tab title :

cat cyberattacks.txt | grep -o '<title>.*</title>' | sed 's/<title>//;s/<\/title>//'

## To make a list of cyber attacks based on section titles :

cat cyberattacks.txt | grep -o '<h[1-6][^>]*>.*</h[1-6]>' | sed 's/<[^>]*>//g' | grep -i 'cyber attack'
