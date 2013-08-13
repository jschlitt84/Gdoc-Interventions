GDoc Interventions, a collaborative approach to Epifast experiment scripting
User Guide by James Schlitt
Written 8/6/2013 for the Network Dynamics and Simulation Science Laboratory
https://github.com/jschlitt84/Gdoc-Interventions

Introduction:
	Gdoc-Interventions (GDI) is a suite of python scripts designed to foster rapid development and analysis of large, multivariate experiment sets within Epifast via a collaborative, Google Drive based approach. While lacking the simplicity of Didactic, GDI serves to mirror the logistical realities of mass pharmaceutical intervention, automating the scripting of graduated treatment rollouts to target populations via the PolyRun.py and RollVac.py scripts. Further, GDI eases analysis via the generation of mass statistics for ready parsing by standard statistical packages in GetSlice.py. GDI is intended to serve as a time saving middle ground between the fast, low level capabilities of Didactic and the powerful but labor intensive text scripting of pure Epifast

Primary Components
GetSlice.py: Statistical analysis script for mass experiment sets following the Epifast naming standards. Generates both mass multivariate tables, individual cell epicurve replicate tables, and individual cell summary statistics. Designed for easy parsing of output via statistical packages. Under ongoing development.
gDocsImport.py: Google Drive spreadsheet loading & parsing class. Allows ready access to text or line number denoted spreadsheets for scripting input with single row and ‘ignore below’ commenting for markup or experimental manipulations. Currently supports owned private spreadsheets or public document URLs.
PolyRun.py: Script for iterating the mass generation of RollVac experiments based upon nested, looped operators for multidimensional data analysis. Generated experiments are output into a directory tree based upon the PolyRun loop/ variable combinations of a given experiment. Also creates a bash script to submit all generated experiments which is further used in GetSlice’s analysis functions. 
RollVac.py: Epifast experiment generating script. Reads spreadsheet scripting & parameters passed by gDocsImport.py and generates an experiment in the Epifast 2009 intervention, config, antiviral, and diagnosis file formats. Contains numerous allowances for forward & backward compatibility via find & replace scripting, mass file copy, and base intervention files. Contains local text file and input prompt based scripting modes, though such have been deprecated in favor of PolyRun automation.

Experimental Parameters & Functions
Current Work
~This guide is written specifically for paired PolyRun.py and GetSlice.py usage as single experiment RollVac.py use is depracated. All rows containing ‘#’ comments or below an ‘#IGNORE” tag are ignored during runtime. All rows containing PolyRun operators are passed based on the specific combination/ loop of PolyRun operators. All rows without PolyRun operators are passed to every experiment. Any row in the following categories may be iterated over through use of PolyRun operators.

Global Parameters: Controls the high level functionalities and base properties of the experiment. Only one line of such should be passed at any one time.
Study Name Prefix: Optional for RollVac standalone usage, used as a prefix to the generated experimental Intervention, Antiviral, and Diagnosis Epifast files. Required for PolyRun usage, used as an experimental directory name in the local directory or the PolyRun Explicit Directory Prefix. Should be a short, easy to remember alphanumeric string with no spaces,  or special characters ($ # ,).
Diagnosis Based Antivirals: Yes or no value, if ‘yes’, will parse the Gdoc v2009 Diagnosis and Antiviral intervention parameters and generate Epifast Antiviral and Diagnosis files. If no, said rows will be ignored.
Polyrun Explicit Directory Prefix (optional): For on server usage, specifies the explicit, UNIX formatted head directory for Epifast file output. Intended method for Pecos/ Shadowfax use.
PolyRun Files To Copy (optional): Checks GDI directory for listed files, runs through PolyRun Find & Replace if a replace script is selected, and copies said files into each PolyRun cell subdirectory. Useful for any additional setup files used in every experiment. Usage: “File1; File2”
PolyRun Base Intervention File (optional): Checks GDI directory for listed file and appends said file’s contents to the beginning of each cells’ Intervention file. Intended to extend backwards/ forwards compatibility by allowing the incorporation of Epifast scripting beyond the capabilities of RollVac parsing. Usage: “Basefile.txt” 
PolyRun Find & Replace File (optional): Checks GDI directory for listed file containing find and replace script. If used, checks the PolyRun Files To Copy for selected strings and if found, replaces the entire line with scripted text. Also allows for ’#’ commenting and experiment specific text replacement via the $DIR, $EXP, and $ITER commands. Sample script:
File = qsub
Find = #PBS -W
Replace = #PBS -W group_list=server
File = config
Find = ContactGraphFile =
Replace = ContactGraphFile = /directory/EFIG
	Special strings:
$DIR: replaced with current cell explicit directory
$EXP: replaced with experiment top directory
$ITER: replaced with the number of a given cell by order of execution
#: at the beginning of a line, signals a comment/ ignore
Find & Replace was designed specifically to point qsub & config files properly to specific experimental cell subdirectories while allowing a further means of user control for unforeseen, extended functionalities via on the fly manipulation of generic basefiles.
Subpop Home Folder: points to the explicit directory of the experimental subpopulations. If empty, GDI local directory is used.
Append chmod 775: seldom used, will add a chmod 775 command to the end of the PolyRun generated bash script. Useful for clearing up permission arguments during collaboration.
PolyRun.py Operator: as with ‘#’ comments, the column location of an operator is non specific and the existence of an operator in a given row will affect the parsing and execution of an entire row. See PolyRun Operation for further detail.

Intervention Scripting Parameters: Based off the Epifast 2009 Intervention, Antiviral, and Diagnosis file formats with the important addition of spread-date enumeration. It’s important to note that each type of intervention must only be applied once to a given population or it will be administered to the same individuals on successive uses. If an intervention is to be administered unevenly or on non-successive days, it currently must be done via the enum function.
Subpopulation: Denotes which subpopulation file in Subpop Home Folder the intervention will be applied to.
Day/ ‘enum’:  If an integer is entered, denotes the first day on which a given intervention will be administered (day mode), allowing for either single day interventions or interventions evenly spread across multiple days as denoted by the Length of Spread entry. If the text ‘enum’ is entered, triggers Rollvac to load Length of Spread as an explicit enumeration (enumeration mode) from the next row via the following format:

Subpopulation
Day/'enum'
Length of Spread
Intervention Type
Duration
Compliance
SUBPOP.txt
enum
enum
(any intervention)
10
0.5
0,100
2,4%
5,0.2






~SUBPOP.txt is given 100 interventions on day 0, 4% of the population is given interventions on day 2, and 20% on day 5
	
Interventions may be given for any day in the experiment via the same style and interpretation as pure Epifast with the addition of length of spread and enumerated application functionality.

Length of Spread: Integer value if in day mode, denotes how many days it will take to administer the interventions once started and evenly spreads the intervention across said day. If uneven intervention is desired, use enumeration mode formatting as seen above.
Intervention Type: Denotes the standard, Epifast names for Vaccination, Antiviral Prophylaxis (written as “Antiviral” in the Intervention Block, antiviral treatment must be scripted via the separate Diagnosis and Antiviral Blocks), SocialDistancing, WorkClosure, and CloseSchools. If the wrong number of arguments are given in the following blocks for a given intervention it will result in an error termination.
Duration: Integer value, denotes how long a given intervention will remain effective/ in effect.
Compliance: Decimal value, denotes the odds an individual within the given subpopulation will comply with an intervention.
V/AV Efficiency In: Decimal value, denotes the percentage by which risk of transmission is reduced between a treated, uninfected individual and infected individual upon exposure.
V/AV Efficiency Out: Decimal value, denotes the percentage by which risk of transmission is reduced between a treated, infected individual and an uninfected individual upon exposure.
PolyRun.py Operator: See PolyRun Operation for further detail.

Diagnosis Scripting & Antiviral Treatment Parameters: Expected to be deprecated in favor of a new format within the next version of Epifast, covers broad, global diagnosis parameters for when an infected individual may seek medical attention and be prescribed antiviral treatment as well as the properties of a specific treatment implementation for a given subpopulation. Follows Epifast standard text formatting with the single added capability of iteration by PolyRun operators.

Analysis Parameters & Functions:
~Parameters marked with a ‘*’ are used only for single chart, 2D bivariate comparison. Most development has been geared towards mass generation of statistics.
	Current Work
GetSlice is intended mostly as a quick, utilitarian means of generating mass stats for analysis and visualization to provide a bridge between PolyRun generated experiments and pre-existing statistical packages. As such, it does not have the degree of polish and interactivity of the other GDI tools. While initial usage was geared towards two dimensional heatmap generation via string parsing, newer functions are geared specifically for mass stat generation to evaluate the effects of specific human interventions against the range of antiviral and vaccine efficacies beyond immediate human control. The parameters Output File Name, Qsublist, Script To Run, and Script Target are not yet implemented. Further analyses may be scripted into a single Gdoc as additional columns.

Experiment Directory: Explicit top directory for experiment where qsublist will be found. Should be /ExplicitDirectory/ExperimentName.
Output Directory: Explicit output directory, ideally a subdirectory of the Experiment Directory.
Subdirectory/File Target: File to be analyzed, should almost always be ‘EFO6’ unless standard output names not in use.
Folder Level X/Y Axis*: as each directory level is intended to represent a range of variables in a multivariate analysis, the X axis level denotes from 0-n the subdirectory to be compared for the X/Y axis of the heatmap.
Include with these strings*: if entered, only experiments containing all of the given space separated strings in their given Folder Level will be used. If empty, all experiments at the given level will be passed.
Ignore with these strings*: if entered, only experiments without any of the space separated strings in their given Folder Level will be used. Overrides Include with.
Const directory PolyRun operators*: Single string that must be found in all Folder levels excepting the X & Y axis levels. Intended to narrow a single subset of constant conditions against a range of X & Y axis values. If more than one unique Folder Level string is found to contain the Const directory operator, the script will assume improper narrowing of results and cancel the analysis.
Generate Stats for Everything: Primary mode of use, generates single detail stat file in given Output Folder, summary stats and attack rate v. day plots in cell subdirectories, and directories of ve vs ave charts for each unique human intervention combination. Under ongoing development.

PolyRun Operation:
	PolyRun is intended specifically for the mass generation of multivariate data sets and as such functions via a tree of nested loops over each variable combination. It allows for simply rerunning an experiment with different efficacies, timing, etc, similar to but perhaps more slowly than in Didactic, but also allows novel functionality by looping over divergent sets of experiment global variables, basefiles, find & replace scripts, and copy files. As designed, every single row in a GDI sheet may be iterated over via a PolyRun operator. Further, every combination of operators for a given index loop will be run against every other index loops’ operators, with the non-flagged rows being passed as well to every experiment.

Operator format is simple and may be placed in any vacant cell in a row such that it doesn’t disrupt the scripting content, though specific columns are marked per convenience. Care should be taken to avoid nonstandard characters in a PolyRun operator cell.

Format is as follows:
$[operator flag] 1[numeric loop index] somestring[operator] 
Example:
$ 1 ave95sd33AllMil

Operator Flag: Tells PolyRun that that row is part of a PolyRun loop, designated by the numeric loop index. If an intervention row contains no operator flag, it will be passed to every experiment as a constant event. In most use, the diagnosis and global parameters may have no operator flag.
Numeric loop index: Identifies a given row as part of a loop, and creates a new loop if it is the first loaded row marked with a given index. Directories are generated in numeric order of the run indices such the the lowest index will be the first folder level inside an experimental directory.
Operator: Each unique operator specifies a variable which will be output into its own directory tree. Lines given the same operator and loop index will always be passed together to the same experiments, as must be done for all 2-line enumerated interventions. Operators should be given in a meaningful manner along the standard Epifast format to allow human review and GetSlice parsing & analysis. Any text content in an operator not matching Epifast format will be categorized as “other” in the GetSlice run all mode statistical output.

For simulation methods beyond the scope of GDI’s experiment generation, PolyRun loops provide a valuable avenue for experiment customization as any value within the config, qsub, and related setup files may be changed with a PolyRun iterated set of find and replace scripts in the global variables. Likewise, novel intervention code may be readily integrated by an iterated set of base intervention files containing the desired code. Finally, any novel setup script may simply be bulk copied without customization via the files to copy feature.

Setting up and executing an experiment:
GDI is heavily designed towards a collaborative, online approach to experimental design, and as such requires a properly formatted google drive spreadsheet to access most features. Each spreadsheet is parsed by text strings to find user generated blocks of scripted values, and alterations to the column labels may cause a loading error (E1). In each spreadsheet, only the first page is accessed, allowing for discussion and calculations on subsequent pages. Further, any row containing a ‘#’ or below an ‘#IGNORE’ entry will be ignored by the loader, allowing for temporary blanking of cells and user markup. Due to the potential time and energy expenditures of a misformatted experiment, GDI will always terminate with a message at the first detected sign of erroneous input while providing verbose feedback during normal activity.

1: Experimental Design: For a single celled experiment, one need simply input the experimental data fields as detailed above in Experimental Functions and Parameters in a blank GDI spreadsheet. This will consist of 1 Global Parameters and Diagnosis Scripting row per experiment with one or more rows of Interventions and Antiviral Treatment. If multiple cells are needed, one will have to script a loop across each cell via PolyRun operators.

2: Execution: For a public spreadsheet, navigate to the GDI folder and enter:

$ python PolyRun.py spreadsheetURL

For a private spreadsheet, usage is:

$ python PolyRun.py ownerGoogleID ownerGooglePassword gDocFileName

If an experiment has previously been run with the same name and directory, you will be asked whether to delete, ignore, or append a numeric suffix to the new experiment on output. Improper URLs or access permissions will lead to an error termination (E2).

3: Job submission: PolyRun will generate a bash file to execute each cell of the generated experiment and output it to theExperimentDirectory/qsublist. To execute, navigate to the experimental directory and enter “source qsublist”. The qsublist contains no pauses or restrictions on the rate of submission, and care should be taken to avoid swamping the queue. Further, the qsublist is a valuable directory list of each experiment that is both parsed by GetSlice and useful for rapid navigation by users via terminal. While it may be valuable to alter the qsublist to spread out job submission, the original file is used in analysis and must be retained.

4: Analysis: Same format as PolyRun, in terminal enter:

$ python GetSlice.py spreadsheetURL

For a private spreadsheet, usage is:

$ python GetSlice.py ownerGoogleID ownerGooglePassword gDocFileName



Common Errors (E)
Column Labels changed: gDocsImport will not be able to find & load proper rows and will quit shortly after termination. As gDocsImport’s text output generally notifies user of loading purpose, errors may be caught in this fashion.
Insufficient access rights or malformed URL: Characterised by the loading dialogue showing html code segments rather than the expected spreadsheet scripting parameters. May be fixed by reloading the URL, ensuring user is logged into google, and verifying public file access when allowable.
Prior value used in script pending user edits: In spite of the save dialogue, google drive does not update the values sent to a gDocsImport exported spreadsheet until the cursor is moved from an edited cell. Be sure to always click a separate section of the sheet after making an important edit.
Stale NFS Handle Terminations of file.close(): problem appears to occur in seemingly random functions/ GDI scripts when larger populations are in use, likely due to exceeding the write speed of the system. Currently a 50ms delay is in place at line 404 of PolyRun, “sleep(0.05)”. If this error becomes common, consider editing the code to manually increase the delay in short increments until the issue resolved.




