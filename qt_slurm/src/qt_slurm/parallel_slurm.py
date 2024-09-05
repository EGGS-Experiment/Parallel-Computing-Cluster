import os
import csv
from qutip import *
import numpy as np
import time
import matplotlib.pyplot as plt
import nbformat
from nbconvert import PythonExporter
import subprocess
import socket
import platform
import shutil


'''
Qt_Slurm v1.2.0

See README for version history

Parts of code were taken from GeekforGeeks and ChatGPT
'''

def split_func(num_of_divs):
    '''
    The split function specifies how many tasks each node will accomplish. It divides the total number of divisions 
    by the total number of computers. This floor is added to an array with the number of entries set to the
    number of computers. The remainder is calculated with a modulus and is added as evenly as possible to each
    node. 
    
    Returns split_arr, the number of computations each node will compute. 
    
    num_of_divs: Number of divisions or points in your param parameter for your main function. 
    '''
    rank, total_ranks, job_id = get_rank()
    
    split = num_of_divs // total_ranks
    split_arr = []
    for i in range(total_ranks):
        split_arr.append(split)
    for i in range(int(num_of_divs % total_ranks)):
        split_arr[i]+=1
    return split_arr

    
def get_rank():
    '''
    The get_rank() function gets the unique number assigned to each computer by Slurm (rank, necessary for division) and the 
    total number of computers available for the job (total_ranks). 

    returns rank, total_ranks

    Code from ChatGPT
    '''
    rank = int(os.getenv('SLURM_PROCID', 0))
    total_ranks = int(os.getenv('SLURM_NTASKS', 1))
    job_id = os.getenv('SLURM_JOB_ID')    

    return rank, total_ranks, job_id

def get_var_name(var):
    '''
    From GeeksforGeeks (https://www.geeksforgeeks.org/get-variable-name-as-string-in-python/)
    '''
    
        
def parallelize(func, param, num_of_divs):
    '''
    The Parallelize function uses Qutip's parallel_map feature and splits the number of tasks created by parallel_map and 
    gives a specified amount to each node. Data is sent to a temporary file system and collected by the last node to 
    complete its computation(s).
    If used in Jupyter Notebook, it must be in the last cell with anything related to your computation (therefore 
    must be in a different cell before the execute() function. 

    func: Function you wish to parallelize using Qutip's parallel_map (see Qutip docs for more details).
    param: Parameter for given func function.
    num_of_divs: Number of divisions or points in your param parameter. 

    Returns results_arr, or output of all parallel_map processes across all nodes currently completed (will only
    be complete once the final node has completed computations). 
    '''
    
    start = time.time()
    home_dir = os.getenv('HOME')

    split_arr = split_func(num_of_divs)
    
    rank, total_ranks, job_id = get_rank()
    results_arr = [[] for _ in range(total_ranks + 1)]
    param_arr=[]
    
    print("Job ID: " + str(job_id), end="\n")
    print(socket.gethostname() + ": #" + str(rank + 1), end="\n")
    
    for i in range(total_ranks):
        if i == 0:
            param_arr.append(param[i:split_arr[i]])
        else:
            param_arr.append(param[sum(split_arr[:i]):sum(split_arr[:i])+split_arr[i]])

    for i in range(total_ranks):
        if i == rank:
            results = parallel_map(func,param_arr[i])
            results_array = np.array(results).tolist()
            
    try: #Makes a temporary folder
        if os.path.isdir(home_dir + "/temporary_files/tmp" + str(job_id)) == False:
            os.mkdir(home_dir + "/temporary_files/tmp"+ str(job_id))
    
    except Exception as e:
        print(f"Skip: {e}")

        
    if os.path.isfile(home_dir + "/temporary_files/tmp" + str(job_id) + "/results_array.csv")==True:
        with open(home_dir + "/temporary_files/tmp" + str(job_id) + "/results_array.csv", newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='"',quoting=csv.QUOTE_MINIMAL)
            tmp = 0
            for row in reader:
                results_arr[tmp] = row
                tmp+=1

        results_arr[rank] = results_array
        results_arr[-1][0]=int(results_arr[-1][0])
        results_arr[-1][0]+=1
        val = results_arr[-1][0]
        with open(home_dir + "/temporary_files/tmp" + str(job_id) + "/results_array.csv", 'w') as f:
            write = csv.writer(f)
            write.writerows(results_arr)
    else:
        results_arr[rank] = results_array
        results_arr[-1]=[1]
        with open(home_dir + "/temporary_files/tmp" + str(job_id) + "/results_array.csv", 'w') as f:

                # using csv.writer method from CSV package
                write = csv.writer(f)

                write.writerows(results_arr) 
        val = results_arr[-1][0]
    if int(val) == total_ranks:
        end = time.time()
        print("\nTotal time taken: " + str(end - start) + " seconds.")
        with open(home_dir + "/temporary_files/tmp" + str(job_id) + "/results_array.csv", newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='"',quoting=csv.QUOTE_MINIMAL)
            tmp = 0
            for row in reader:
                results_arr[tmp] = row
                tmp+=1
        for i in range(len(results_arr)):
            for j in range(len(results_arr[i])):
                results_arr[i][j] = float(results_arr[i][j])

        results_arr.pop(-1)
        results_arr = [i for j in results_arr for i in j]
        
        graph = plt.plot(param/(2*np.pi),results_arr)
        try:
            try:
                for name, value in globals().items():
                    if value is param:
                        xlab = name
                        graph = plt.xlabel(xlab)
                if os.path.isfile(home_dir + "/temporary_files/execute" + str(job_id) + ".csv") == False:
                    with open(home_dir + "/temporary_files/execute" + str(job_id) + ".csv", 'w') as f:
                        write = csv.writer(f)
                        write.writerow("0")

                
                f = open(home_dir + "/temporary_files/name" + str(job_id) + ".txt", "r")
                title = f.read()
                graph = plt.title(title)
            except Exception:
                pass

            sv = 0
            n = 0
            while(sv == 0):
                if os.path.isfile(home_dir + "/sim_data/" + str(n) + ".png") == True:
                    n += 1         
                else:
                    with open(home_dir + "/sim_data/" + str(n) + ".csv", 'w') as f:
                        write = csv.writer(f)
                        write.writerow(results_arr)
                    plt.savefig(home_dir + "/sim_data/" + str(n) + ".png") 
                    print("Figure saved as " + home_dir + "/sim_data/" + str(n) + ".png")
                    print("Data saved as " + home_dir + "/sim_data/" + str(n) + ".csv") 
                    sv = 1
                    
                    try:
                        if subprocess.run(['which', "feh"], stdout=subprocess.PIPE, stderr=subprocess.PIPE).returncode==0:
                            os.system('feh ' + home_dir + "/sim_data/" + str(n) + ".png")
                    except Exception:
                        pass
            try:
                os.remove(home_dir + "/temporary_files/tmp" + str(job_id) + "/results_array.csv")
                os.remove(home_dir + "/temporary_files/name" + str(job_id) + ".txt")
                os.rmdir(home_dir + "/temporary_files/tmp" + str(job_id))
            except Exception as e:
                print(f"{e}")
            
        except Exception as e:
            print(f"{e}")
            
        
    return results_arr

def execute(name, nodes, cores, tasks):
    '''
    Jupyter Notebook-specific function. Copies the contents of the Jupyter Notebook and exports it to a Python file
    in a shared filesystem at location $HOME/shared_scripts/. The function will then use Slurm to execute the job in
    parallel using srun and the specified variables once the file has been uploaded. 

    name: Name of the Jupyter Notebook (path optional if in $HOME directory) 
    nodes: Number of nodes (computers) the user will request Slurm for
    cores: Number of cores requested (max is the number specified in slurm.conf file - also number of cores per CPU)
    tasks: Number of tasks requested (set to nodes, this will tell Slurm how many times to distribute the .py file)

    *Parts of the code were taken from ChatGPT
    '''
    home_dir = os.getenv('HOME')
    
    rank, total_ranks, job_id = get_rank()
    try:
        with open(home_dir + "/temporary_files/name" + str(job_id) + ".txt", "w") as file:
            file.write(name)
    except Exception:
        pass
    if platform.system() != "Linux": 
        raise TypeError("Slurm is only compatiable with Linux systems")
    if job_id==None:
        if os.path.isfile(home_dir + "/shared_scripts/" + name.split(".")[0]+ ".py") == False:
            file = name.split(".")[0]+ ".ipynb"
            try:
                with open(file, 'r') as notebook_file:
                    notebook_content = nbformat.read(file, as_version=4)

                # Convert the notebook to Python script
                python_exporter = PythonExporter()
                python_script, _ = python_exporter.from_notebook_node(notebook_content)

                # Write the script to a file
                with open(home_dir + "/shared_scripts/" + name.split(".")[0]+ ".py", 'w') as output_file:
                    output_file.write(python_script)
                    
                      
                
                os.system("srun -n" + str(nodes) + " -c " + str(cores) + " -N " + str(tasks) + " python " + home_dir + "/shared_scripts/" + name.split(".")[0]+ ".py")
                home_dir = os.getenv('HOME')
                
            except Exception as e:
                print(f"Error: {e}")

        else:
            try:
                ans = input("A file with the name of your Jupyter notebook file already exists, would you like to delete it and restart (will be done automatically)?\n")
                if ans.lower().replace(" ", "") == "yes" or ans.lower().replace(" ", "") =="y":
                    os.remove(home_dir + "/shared_scripts/" + name.split(".")[0]+ ".py")
                    print("\nWaiting ten seconds...\n")
                    time.sleep(10)
                    execute(name, nodes, cores, tasks)
                else:
                    print("Exiting...")
            except Exception:
                pass 
            
            
def clear():
    print("Active Jobs:\n")
    os.system("squeue")
    ans = input("Do you want to clear all temporary files? This may disrupt any computers/processes currently using the file system.\n")
    if ans.lower().replace(" ", "") == "yes" or ans.lower().replace(" ", "") =="y":
        for filename in os.listdir("/home/farmer/temporary_files/"):
            try:
                os.remove("/home/farmer/temporary_files/" + filename)
            except:
                try:
                    shutil.rmtree("/home/farmer/temporary_files/" + filename)
                except Exception:
                    pass
    print("\nDeleted all temporary files!")
