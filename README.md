# Commands

## Find Race

Tries to find the race information searching in the leagues webpages.

```sh
python findrace.py <datasource> <race_id> <options>
    # --day=<int>: Tells the parser the day of the race we want (for multi-race pages).
    # --female=<bool>: Specifies if we need to search in the female pages.
    # --lineups=<bool>: Tryies to fill the lineups.
    # --save=<bool>: Saves the output to a csv file.

python findrace.py act 1678276379 --female
```

## Download Images

Downloads lineup images for a given rower in a given club (Only supports traineras.es).

```sh
python downloadimages.py <rower_id> <club_name> <options>
    # --year=<str>: Year searched.
    # --output=<str>: Folder where images will be uploaded.

python downloadimages.py 2914 'PUEBLA' --year=2019 --output=out
```

## Find Lineup

Tries to parse a line-up for a given race to retrieved all the participants.

```sh
python findlineup.py <datasource> <race_id> <options>
    # --female=<bool>: Specifies if we need to search in the female pages.
    # --save=<bool>: Saves the output to a csv file.

python findlineup.py traineras 5756
```

## Parse Image

Tries to parse an Inforemo image to retrieve the race data and participants.

```sh
python parseimage.py <datasource> <path> <options>
    # --header=<int>: Indicates the ammount of the image used for the header (default = 3) representing 1/3.
    # --save=<bool>: Saves the output to a csv file.
    # --debug: Plot the image processing steps and dataframes transformations done.
```

# Utils

## Lemmatize

Create a list of lemmas for the given phrase.

```sh
python lemmatize.py <phrase>
```
