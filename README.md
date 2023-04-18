# Commands
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