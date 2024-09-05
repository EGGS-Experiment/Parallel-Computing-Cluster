# Parallel Computing Cluster (Farm) Guide
This is a guide on how to optimize your code for use in the Farm cluster. Please note that all of the systems run on Linux. 

## Slurm
Slurm is a workload manager that will allocate tasks and resources in a computing cluster. It **will not** parallelize your code for you and will only 'accelerate' any code that is built for parallelization in the first place. All Slurm commands are executed via text files and/or the command line. 

## Python via Slurm
This part of the guide is for the integration of Qutip and Slurm. Please note that I have created a Python package that does everything seen below. Link can be found here: 
https://test.pypi.org/project/qt-slurm/0.1.10/

Also available in this repo under [qt_slurm](https://github.com/dylankawashiri/hudsonlab/tree/main/Parallel%20Computing%20Cluster/qt_slurm).

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

### Splitting the code
You must split up your code to take advantage of the available nodes. This can be done by taking advantage of the system variables that Slurm assigns to each node upon execution of the code. Slurm will assign each node a node or rank (1 through n where n is the number of nodes requested/in use). 

This can be determined through the following (code from ChatGPT):
```
rank = int(os.getenv('SLURM_PROCID', 0))
    total_ranks = int(os.getenv('SLURM_NTASKS', 1))
    print(f"Rank: {rank+1}/{total_ranks}")
```
None of the variables that you execute will be shared between computers, so you will not need to initialize the rank value into an array. 

I found the best way to split the code was by assigning each computer a certain number of calculations based on the rank Slurm had assigned. 
First step:

```
split = num_of_divs // total_ranks #1
split_arr = [] 
for i in range(total_ranks):
    split_arr.append(split)
for i in range(num_of_divs % total_ranks): #2
    split_arr[i]+=1
```
1) Division (floor) of the total number of divisions in the function by the total number of computers being used
2) Takes the modulus of the number of divisions by the total number of computers and adds the remainder to one of the computers

Second step:

```
for i in range(total_ranks):
    if i == 0:
        detunings_arr.append(detunings[i:split_arr[i]])
    else:
        detunings_arr.append(detunings[sum(split_arr[:i]):sum(split_arr[:i])+split_arr[i]])
```

As mentioned before, there is no way to store the results in a common variable. We therefore must use a temporary shared file system between the nodes. This has already been set up. If you are looking to set up your own file system, see here. 


### File Sharing
In order for Slurm to work, you must distribute the Python file you wish to parallelize to all nodes in the cluster. This can be done by uploading the files to the mounted folder at location "$HOME/shared_scripts" (this folder is available on all nodes). This will automatically distribute the file. 


