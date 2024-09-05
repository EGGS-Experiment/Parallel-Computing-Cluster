# Parallel Computing Cluster (Farm) Guide
This is a guide on how to optimize your code for use in the Farm cluster. Please note that all of the systems utilizing Slurm only run on Linux. 

## Slurm
Slurm is a workload manager that will allocate tasks and resources in a computing cluster. It **will not** parallelize your code for you and will only 'accelerate' any code that is built for parallelization in the first place. All Slurm commands are executed via text files and/or the command line. 

## Python via Slurm
This part of the guide is for the integration of Qutip and Slurm. Please note that I have created a Python package that does everything seen below. The link can be found here: 
https://test.pypi.org/project/qt-slurm/

Also available in this repo under [qt_slurm](https://github.com/EGGS-Experiment/Parallel-Computing-Cluster/tree/main/qt_slurm).

### Parallel Map
You will need to use Qutip's [parallel map](https://qutip.org/docs/4.0.2/guide/guide-parfor.html) function for integration with Slurm. Parallel map's parameters are a function and the array/vars that you will call that function with. Parallel map will assign one calculation of the array to one available CPU core. With n cores, you can process up to n calculations simultaneously. If you have more than n possible calculations, the extra cores will speed up any remaining calculations. 

**Example:**
If the function you wish to parallelize is: 
```
def detuning_func(detuning):


    args_use = { 'w_c': delta+w0/3+detuning,'w_b': delta+w0/3+detuning,'w_c0': delta+2*np.pi*0.0*MHz,'w_b0': delta+2*np.pi*0.0*MHz,'w_r': delta+detuning, 'phi_r': 0*1*np.pi/2, 'phi_c': 0,'phi_b' :0, 'tau': tperiod}

    H=[H0,[H_b,cos_b],[H_c,cos_c],[H_b/10,cos_b0],[H_c/10,cos_c0]] # full green eggs hamitonian
    H=[H0,[H_b,cos_b],[H_c,cos_c],[H_b,cos_b0]] # full green eggs hamitonian

    outputc = sesolve(H,psi0,times,e_ops = [n], args = args_use,progress_bar=True,options = Options(nsteps = 1e6,max_step = tperiod/1000000,store_final_state = True))

    return outputc.expect[0][-1]
```
and the detuning parameter is: 

```
detuning=np.linspace(2*np.pi*12*kHz,2*np.pi*18*kHz,num_of_divisions)  
```

You would call the parallel map function with:

```
parallel_map(detuning_func,detunings_arr[i])
```

This output will not tell you anything useful. However, converting the result to an array will give you the results of your initial function. 

See [qt_slurm](https://github.com/EGGS-Experiment/Parallel-Computing-Cluster/tree/main/qt_slurm) for more details about integrating Python (including Jupyter Notebook) with Qutip and Slurm. 


### File Sharing
In order for Slurm to work, you must distribute the Python file you wish to parallelize to all nodes in the cluster. This can be done by uploading the files to the mounted folder at location "$HOME/shared_scripts/" (this folder is available on all nodes). This will automatically distribute the file. See [qt_slurm](https://github.com/EGGS-Experiment/Parallel-Computing-Cluster/tree/main/qt_slurm) for doing this with Jupyter Notebooks.  

## Sending Files to Slurm
There are two ways to start a Slurm job.

### srun
The easiest way to start a Slurm job is to use [srun](https://slurm.schedmd.com/srun.html). Generally, this can be done in the command line:

```
srun --ntasks num_of_tasks --cpus-per-task num_of_cores --nodes num_of_nodes (terminal comamand to execute code)
```
which is equivalent to:
```
srun -n num_of_tasks -c num_of_cores -N num_of_nodes (terminal comamand to execute code)
```
It is recommended you set the number of tasks equivalent to the number of nodes you are planning on using. For example, if you are planning on using six nodes and eight cores per computer to execute a python script called script.py, your srun command would look like:
```
srun -n 6 -c 8 -N 6 python script.py
```
or
```
srun --ntasks 6 --cpus-per-task 8 --nodes 6 python script.py
```

### sbatch
You can additionally use [sbatch](https://slurm.schedmd.com/sbatch.html) to execute jobs. Sbatch is a text files that will tell the cluster how many nodes, cores, memory, etc., etc. to allocate. [Here](https://www.google.com/url?q=https://www.arch.jhu.edu/short-tutorial-how-to-create-a-slurm-script/&sa=D&source=docs&ust=1725523688658699&usg=AOvVaw29U_ikFikwKmmbhnq2kSp3) is a good guide on how to write a script. Ignore usage of modules, they are only used to load Python which is already active on all computers. 

An example heading to your script:
```
#!/bin/bash
#SBATCH --nodes=2
#SBATCH --time=00:05:00
#SBATCH --output=$HOME/sim_data/outputs/%j_out.txt
#SBATCH --error=$HOME/sim_data/outputs//error_msgs/%j_err.txt
```
Here, the number of nodes, the total time allotted, the location for the output of the code, and the location for any potential error messages are specified. There are many other options that you can add for further customization. Each Slurm command must start with an #SBATCH indicator. The $HOME/sim_data/ folder is mounted across all nodes in the computer so any additions in one folder will be reflected in a folder at the same path on all nodes. 

Following this, you can add any terminal commands you need to run your code. This can include activating a virtual environment, making a directory, and more. Following the example seen in the srun section, an example sbatch script may look like:
```
#!/bin/bash
#SBATCH --nodes=6
#SBATCH --cpus-per-task=8
#SBATCH --ntasks=6
#SBATCH --output=$HOME/sim_data/outputs/%j_out.txt
#SBATCH --error=$HOME/sim_data/outputs//error_msgs/%j_err.txt

python script.py
```

### Note on different usernames/Home directories
For this demonstration, I will be referring to the 'python script.py' example. When writing python script.py (in terminal or with Slurm), you are essentially writing $HOME/path/to/python $HOME/script.py (assuming you are executing the script out of your $HOME directory). This $HOME directory is the directory of whichever computer you are running the script from. For example, if you are running srun from a computer with directory /home/farmer and one of the nodes has home directory /home/farmer_different, the farmer_different computer will receive the command as /home/farmer/path/to/python /home/farmer/script.py. However, this computer will have each of these stored at /home/farmer_different/path/to/python and /home/farmer_different/script.py, meaning that the execution of any Slurm commands will only work if the Home directories are the same.


This, however, is not a reasonable thing to assume. Therefore, if there are multiple nodes with different usernames/Home directories, you must create a Symbolic Link using [symlink](https://www.freecodecamp.org/news/symlink-tutorial-in-linux-how-to-create-and-remove-a-symbolic-link/). You can create a link between /home/farmer/ and whatever the different Home directory is (for example /home/farmer_different):
```
sudo ln -s /home/farmer_different /home/farmer
```

This will make it so there is a mirrored folder /home/farmer in the farmer_different computer that allows for the farmer_different computer to open files and commands specified to the /home/farmer directory. 


