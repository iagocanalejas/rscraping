# Commands
## Parse PDF
Tries to parse a line-up image to retrieve all the participants and the line-ups.
```sh
python parsepdf <path> <options>
    # --datasource=<source>: Specifies the format of the PDF.
    #     - lgt
    #     - act
    #     - arc
    # --debug: Plot the image processing steps and dataframes transformations done.
```
## Parse Image
Tries to parse an Inforemo image to retrieve the race data and participants.
```sh
python parseimage <path> <options>
    # --datasource=<source>: Specifies the format of the Image.
    #     - inforemo
    # --debug: Plot the image processing steps and dataframes transformations done.
```