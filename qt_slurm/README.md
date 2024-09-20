# Qt_Slurm v1.4.0
This package is meant for Qutip integration with Slurm on Linux based systems.

## Installation
### Required Installations:
- qutip<=4.7.6
### Optional Installations:

- feh (apt-package) - Displays graphs/images via command line

### How to Install:

```cmd
pip install qt-slurm
```



## How to Use

### Required Steps:

First, import the library as shown below:

```python
from qt_slurm import parallel_slurm as pqt
```
### Jupyter Notebook

If using Jupyter Notebook, at the end of your code (in the same cell as the last thing you wish to run), implement the parallelize function.

```python
result = pqt.parallelize(func, num_range, num_of_divs)
```
The first parameter of pqt.parallelize is 'func'. This is the function you wish to parallelize (usually a function incorporating the mesolve/sesolve functions of Qutip). The 'num_range' parameter is the parameter of the other 'func' function. This is usually the range as to which your are calculating mesolve/sesolve over. Finally, the final parameter, num_of_divs, is the number of points within your range. If using np.linspace() function, it is the final parameter entered. 

In a new cell (which will be the first cell you execute - besides the importing of libraries and modules) add the following function:

```python
pqt.execute("Name_of_notebook", num_of_nodes, num_of_cores, num_of_tasks)
```

pqt.execute() is responsible for converting the contents of your Jupyter Notebook to a Python file, moving that file to a shared folder, and then finally executing a Slurm command. To do this, you must enter the name of your notebook. If you are running the Jupyter Notebook out of your home directory, you do not need to include a path name. Otherwise, include a full path name if possible. The following three parameters are all variables required by Slurm. Set num_of_cores to the number of cores each computer has (in this case, 8) and num_of_nodes and num_of_tasks to the number of nodes you wish to use. 

Once you execute the last cell, the conversion will occur and the script will compute in parallel with Slurm. Outputs will be saved in the $HOME/sim_data folder in the form of a CSV file and PNG graph. If you have installed feh, the graph will be displayed on your screen. See the Python code for a more detailed breakdown. 

### Python

If using Python, you will only need to use the pqt.parallelize() function. This should be added to the end of your code with the necessary arguments. 

### Graphing

While the pqt.parallelize() function does do graphing, it currently does not have any customization options. However, the pqt.parallelize() function does return the output of the parallel_map functionality so you can choose to graph the data in its entirety once the parallelize() function has executed. However, you can also use the graph_viewer() function. 

Simply type and run a cell with the graph_viewer() function (as shown below) to view a live preview of your data. A slider at the bottom allows for the selection of different data in the $HOME/sim_data/ folder, this will automatically update the graph. There are additionally optional customization options for the title, axes labels, color, and legend. Checking the Save_Image box saves an image to the $HOME/sim_data folder. 

Note that running this function does not backlog any other usage of other functions in the Jupyter notebook. However, you cannot execute this code if there is a Slurm job running (or in an empty Jupyter notebook). 

![Screenshot 2024-09-06 at 12.16.10 AM](/Users/dylankawashiri/Desktop/Screenshot 2024-09-06 at 12.16.10 AM.png)

![Enter Title_21csv](/Users/dylankawashiri/Downloads/Enter Title_21csv.png)

Example of the live preview and saved image. 

## Functions

```python
from qt_slurm import parallel_slurm as pqt
```

### Parallelize()

```python
pqt.parallelize(func, num_range, num_of_divs)
```

**Arguments**: 

- func
  - Parallelizable function (should already be defined)
- num_range
  - Argument of 'func'
- num_of_divs
  - Number of divisions 

**Output**:

Parallelizes script only using Qutip's parallel_map function, **must be used with Slurm**. When used with a Slurm command, this function will split up the range of values and assign them to each node. 

Returns the results of the computation, additionally outputs the data and graph of the data locally.  

### Execute()  -- Specific to Jupyter Notebook

```python
pqt.execute("Name_of_notebook", num_of_nodes, num_of_cores, num_of_tasks)
```

**Arguments**:

- "Name_of_notebook"
  - The name (path optional, may prevent bugs or FileNotFound errors)
- num_of_nodes
  - Slurm command - requests the number of nodes to be used for the job
- num_of_cores
  - Slurm command - requests the number of cores to be used by each node (all Farm computers have 8 cores)
- num_of_tasks
  - Slurm command - The number of times the notebook will be sent out, *set equal to num_of_nodes*

**Output**:

Function will convert the Jupyter Notebook to an executable Python file. The Python file and job allocation request (in the form of srun) will be sent to Slurm.

### Clear()

```python
pqt.clear()
```

**Arguments**:

None

**Output**:

The clear() function will empty the temporary file folder if there is no job running. This function is not vital to be used and should only be used if you are running out of space/do not know how to find the temporary_files folder ($HOME/temporary_files).



### Graph_Viewer -- Specific to Jupyter Notebook

```python
pqt.graph_viewer()
```

**Arguments**:

None

**Output**:

Function will display a small GUI within Jupyter Notebook allowing for graphing customizations (as shown above). Will only run if there is no job currently running on the computer in use. 



### Get_CSV -- Specific to Jupyter Notebook

```python
pqt.get_csv()
```

**Arguments:** 

None

**Output:**

Displays a dropdown box that outputs a list to the variable, csv_data. 



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
- v1.3.3 - Fixed various fatal bugs
- v1.3.4 - Fixed bug that would cause Graph_viewer() function to not work
- v1.4.0 - Added support for functions that do not automatically take the expectation value, added ability to get variables from CSVs
