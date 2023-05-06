# Commands
## Build PDF
Build all required files for a rower.
```sh
python fillforms <sign_on (DD/MM/YYYY)> <options>
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
python parsepdf <path> <options>
    # --datasource=<source>: Specifies the format of the PDF.
    #     - lgt
    #     - act
    # --debug: Logs the extracted PDF values.
```
#### Notes:
    - ACT 
        - Coxswain and bow are included in the rowers list.
        - Starboard and larboard will contain the same list.
## Parse URL
Tries to parse a line-up url to retrieve all the participants and the line-ups.
```sh
python parseurl <url> <options>
    # --datasource=<source>: Specifies the url we are parsing.
    #     - arc
    # --debug: Logs the extracted URL values.
```
## Parse Image
Tries to parse an Inforemo image to retrieve the race data and participants.
```sh
python parseimage <path> <options>
    # --datasource=<source>: Specifies the format of the Image.
    #     - inforemo
    # --debug: Plot the image processing steps and dataframes transformations done.
```