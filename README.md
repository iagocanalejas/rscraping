# Commands

## Find Race

Tries to find the race information searching in the leagues webpages.

```sh
python findrace.py <datasource> <race_id> <options>
    # --female=<bool>: Specifies if we need to search in the female pages.
    # --lineups=<bool>: Tryies to fill the lineups.
```

## Find Lineup

Tries to parse a line-up for a given race to retrieved all the participants.

```sh
python findlineup.py <datasource> <race_id> <options>
    # --female=<bool>: Specifies if we need to search in the female pages.
```

## Lemmatize

Create a list of lemmas for the given phrase.

```sh
python lemmatize.py <phrase>
```

## Build PDF

Build all required files for a rower.

```sh
python fillforms.py <options>
    # -on: SignOn date to use in the documents (DD/MM/YYYY).
    # -t, --type: Specifies the list of files to be generate (['all']). ['national', 'image', 'fegar', 'xogade', 'all']
    # -p, --parent: Specifies if the rower requires parents data. (False)
    # -i, --images: Folder containing the images for fegar generator.
    # --coach: Create the files for a coach.
    # --directive: Create the files for a delegate.
    # --no-preset: Asks to input more information.
    # --no-entity: Asks to input entity information.
    # --debug: Logs and autofilled data.
```

## Parse PDF

Tries to parse a line-up image to retrieve all the participants and the line-ups.

```sh
python parsepdf.py <path> <options>
    # --datasource=<source>: Specifies the format of the PDF.
    #     - lgt
    #     - act
    # --debug: Logs the extracted PDF values.
```

#### Notes:

    - ACT
        - Coxswain and bow are included in the rowers list.
        - Starboard and larboard will contain the same list.

## Parse Image

Tries to parse an Inforemo image to retrieve the race data and participants.

```sh
python parseimage.py <path> <options>
    # --datasource=<source>: Specifies the format of the Image.
    #     - inforemo
    # --debug: Plot the image processing steps and dataframes transformations done.
```
