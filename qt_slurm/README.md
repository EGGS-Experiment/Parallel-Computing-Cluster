# Qt_Slurm v1.3.0
This package is meant for Qutip integration with Slurm on Linux based systems. Please let me know if there are any bugs. 

## Release History

- v0.0.1-0.1.10 - Bug fixes (previous versions are fatal)
- v0.1.11 - Added return value to parallelize function, fixed deletion of job storage 
- v0.2.1 - Added Jupyter notebook integration, $HOME generalization
- v0.2.2 - Fixed fatal bug with import
- v1.0.0 - First release, removed safety feature (not necessary), removed unnecessary comments, created initialization function, working Jupyter notebook loop and deletion (if necessary)
- v1.0.1 - Forgot to add $HOME variable to initialization function
- v1.0.2 - Added exception to loop in execute() function
- v1.0.3 - Added a waiting period in the execute() function - immediate execution was previously leading to Slurm executing older scripts that had not been deleted yet (can be fatal)
- v1.1.1 - Incorporated initialization() function into execute script, added plot showing capabilities, added automatic title and x labels, included Linux only parameter, included job_id with get_rank() (fatal)
- v1.1.2 - Forgot to include third parameter in new get_rank() function (fatal)
- v1.1.3 - Fixed job_id being called before Slurm job start (fatal)
- v1.1.4 - Added condition to set initial loop value (fatal)
- v1.1.5 - Readded home_dir var to execute() funciton
- v1.1.6 - Fixed printing of each computer rank, added printing job_id (fatal) 
- v1.1.7 - Added timing function (fatal)
- v1.1.8 - Changed plot name finding location (fatal)
- v1.1.9 - Fixed calling of job_id in execute function
- v1.1.10 - Never added creation of temporary file for loop 
- v1.1.11 - Fixed issue where I wrote isdir instead of isfile in execute() function (fatal)
- v1.1.12 - Forgot to delete code (can be fatal)
- v1.1.13 - Added if job_id hasn't been defined, continue loop, else stop - removes need for temporary execute file
- v1.1.14 - Fixed title of graph bug
- v1.1.15 - Changed location of timing variable
- v1.2.0 - Added clear() function
- v1.3.0 - Added graph_viewer() function
## How to Use
### Required Installations:
- qutip<=4.7.6
### Optional Installations:

- feh (apt-package)

### Required Steps:

First, import the library as shown below:

```python
from qt_slurm import parallel_slurm as pqt
```
### Jupyter Notebook

If using Jupyter Notebook, at the end of your code (in the same cell as the last thing you wish to run), implement the parallelize function.

```python
pqt.parallelize(func, num_range, num_of_divs)
```
The first parameter of pqt.parallelize is 'func'. This is the function you wish to parallelize (usually a function incorporating the mesolve/sesolve functions of Qutip). The 'num_range' parameter is the parameter of the other 'func' function. This is usually the range as to which your are calculating mesolve/sesolve over. Finally, the final parameter, num_of_divs, is the number of points within your range. If using np.linspace() function, it is the final parameter entered. 

In a new cell (which will be the first cell you execute - besides the importing of libraries and modules) add the following function:

```python
pqt.execute("Name_of_notebook", num_of_nodes, num_of_cores, num_of_tasks)
```

pqt.execute() is responsible for converting the contents of your Jupyter Notebook to a Python file, moving that file to a shared folder, and then finally executing a Slurm command. To do this, you must enter the name of your notebook. If you are running the Jupyter Notebook out of your home directory, you do not need to include a path name. Otherwise, include a full path name if possible. The following three parameters are all variables required by Slurm. Set num_of_cores to the number of cores each computer has (in this case, 8) and num_of_nodes and num_of_tasks to the number of nodes you wish to use. 

Once you execute the last cell, the conversion will occur and the script will compute in parallel with Slurm. Outputs will be saved in the $HOME/sim_data folder in the form of a CSV file and PNG graph. If you have installed feh, the graph will be displayed on your screen. See the Python code for a more detailed breakdown. 

### Python

If using Python, you will only need to use the pqt.parallelize() function. This just needs to be added 

### Graphing

While the pqt.parallelize() function does do graphing, it currently does not have any customization options. However, the pqt.parallelize() function does return the output of the parallel_map functionality so you can choose to graph the data in its entirety once the parallelize() function has executed. However, you can also use the graph_viewer() function. 

Simply type and run a cell with the graph_viewer() function (as shown below) to view a live preview of your data. A slider at the bottom allows for the selection of different data in the $HOME/sim_data/ folder, this will automatically update the graph. There are additionally optional customization options for the title, axes labels, color, and legend. Checking the Save_Image box saves an image to the $HOME/sim_data folder. 

Note that running this function does not backlog any other usage of other functions in the Jupyter notebook. However, you cannot execute this code if there is a Slurm job running (or in an empty Jupyter notebook). 

![Screenshot 2024-09-06 at 12.16.10 AM](/Users/dylankawashiri/Desktop/Screenshot 2024-09-06 at 12.16.10 AM.png)

![Enter Title_21csv](/Users/dylankawashiri/Downloads/Enter Title_21csv.png)

Example of the live preview and saved image. 
