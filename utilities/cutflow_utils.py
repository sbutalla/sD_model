from .file_utils import *
import itertools
import numpy as np
import pandas as pd
import re

def process_cutflow(file_list, data_dir = None, to_pandas = True, save_csv = True, ret = True, verbose = False):
    '''
    S. D. Butalla
    2022/08/19, v. 0
    
    Function that, given a list absolute file paths (.tex or .txt) 
    for cutflow tables, parses the files and stores the cutflow 
    tables in a dictionary (key = file name without extension).
    By default, the function places the extracted cutflow
    table in a pandas dataframe and saves the table to a 
    .csv.
    
    Dependencies:
    
    pandas
    re
    itertools
    file_utils (custom class)
    colors (custom class)
    
    Positional arguments:
    file_list          : (list; string) A list of the absolute file
                         paths for the cutflow table files.
    Optional arguments:
    data_dir           : (string) Where the csvs will be saved if save_csv == True. 
    to_pandas          : (bool) If true, will convert each cutflow table
                         stored in a dictionary to a pandas dataframe. 
    save_csv           : (bool) If true, will save the pandas dataframe
                         as a .csv in the specified data directory
                         ('dataDir').
    ret                : (bool) If true, will return the various outputs
                         (see below).
    verbose            : (bool) If true, will print extra information.
    
    Output:
    cutflow_dict       : (dict) Dictionary of all cutflow tables. Keys are
                         the names of the files in the file list (without
                         the path or the file extension).
    epsilon_alpha      : (dict) Dictionary of the epsilon / alpha value
                         (keys are the same as in cutflow_dict).
    epsilon_alpha_err  : (dict) Dictionary of the epsilon / alpha
                         uncertainties (keys are the same as in cutflow_dict).
    Optional output:
    df_dict            : (dict) Dictionary of pandas dataframes of the cutflow
                         tables.
    '''
    num_gen_cuts = 5
    if save_csv and not to_pandas:
        print_error("To save cutflow table as a csv the result dictionary must be converted to a pandas dataframe first. Set to_pandas = True.")
    else:
        if data_dir[-1:] != "/": # make sure there is a forward slash at the end of data_dir
            data_dir += "/"
    
    keys_dict         = {file_list[ii].split("/")[1].split(".")[0]: file_list[ii] for ii in range(len(file_list))} # dict of key: file path
    cutflow_dict      = {} # stores all cutflow table information
    epsilon_alpha     = {} # stores all epsilon / alpha values
    epsilon_alpha_err = {} # stores all epsilon / alpha errors
    alpha_gen         = {} # tot. eff. for generator level cuts
    alpha_gen_err     = {} # tot. eff. error for generator level cuts

    if to_pandas:
        alpha_gen_dict    = {"key": [], "alpha": [], "err": []} # tot. eff. for generator level, initialize empty lists

    
    if to_pandas:
        df_dict = {}
    
    for key in keys_dict.keys():
        cut_num                = []
        selection              = []
        events                 = []
        tot_eff                = []
        rel_eff                = []
        tot_eff_err            = []
        rel_eff_err            = []
        cutflow_dict[key]      = {} # stores all cutflow table information
        #epsilon_alpha[key]     = {} # stores all epsilon / alpha values
        #epsilon_alpha_err[key] = {} # stores all epsilon / alpha errors
        #alpha_gen[key]         = {}
        #alpha_gen_err[key]     = {}
        
        if verbose:
            print_alert("Opening file %s\n" % keys_dict[key])
            
        file  = open(keys_dict[key])
        
        if verbose:
            print_alert("File opened successfully\n")
        
        lines = file.readlines()
        
        file.close()
        if verbose:
            print_alert("File closed successfully\n")
        
        if verbose:
            print_alert("Processing file...")
        
        cnt = 0
        for line in lines:
            if line == "Here is the cut-flow-table:\n":
                if verbose:
                    print_alert("Cutflow table detected, processing...\n")
                cnt_data = 0 # counter to keep track of line number
                for data in lines[(cnt + 6):]: # iterate over the table data
                    if re.split('(\d+)', re.sub('[^A-Za-z0-9]+', '', data.split("&")[0]))[0] == "epsilonrecalphagen": # find end of table and extract epsilon/alpha and error
                        epsilonalpha    = data.split("&")[1].split("$")[0].strip()                   # clean text and formatting characters, strip spaces
                        epsilonalphaerr = data.split("&")[1].split("$")[2].split("hline")[0].strip() # clean text and formatting characters, strip spaces
                        
                        # Check for results (some tables don't have epsilon/alpha error vals)
                        if len(epsilonalpha) != 0:
                            epsilon_alpha[key] = float(epsilonalpha)
                        else:
                            epsilon_alpha[key] = None
                        
                        if len(epsilonalphaerr) != 0:
                            epsilon_alpha_err[key] = float(epsilonalphaerr)
                        else:
                            epsilon_alpha_err[key] = None    
                                                    
                        if verbose:
                            print_alert("Epsilon/alpha values:")
                            print_alert(21 * "*")
                            if type(epsilon_alpha[key]) is float:
                                print_alert("eps/alp = %f" % epsilon_alpha[key])
                            elif type(epsilon_alpha[key]) is None:
                                print_alert("eps/alp not in cutflow table")
                            
                            if type(epsilon_alpha_err[key]) is float:
                                print_alert("eps/alp err = %f" % epsilon_alpha_err[key])
                            elif type(epsilon_alpha_err[key]) is None:
                                 print_alert("eps/alp error not in cutflow table")
                            
                            print_alert(21 * "*" + "\n")
                                    
                        continue
                    else:
                        temp_str = data.split("&") # split data into list based on LaTeX alignment character '&'
                        if len(temp_str) == 1:     # Skip blank rows of the table (between gen and reco cuts, and reco cuts and epsilon/alpha) 
                            pass
                        else:
                            if cnt_data == 0:
                                header_lst = []
                                cnt_hdr    = 0
                                for text in temp_str:
                                    if cnt_hdr == 5:
                                        header_lst.append(re.split('(\d+)', re.sub('[^A-Za-z0-9]+', '', text.split("hline")[0]))) # remove LaTeX formatting command "hline" and newline characters
                                    else:
                                        header_lst.append(re.split('(\d+)', re.sub('[^A-Za-z0-9]+', '', text))) # remove spaces and special characters

                                    cnt_hdr += 1

                                header_titles = list(itertools.chain.from_iterable(header_lst)) # flatten list 
                                header_titles.insert(0, "CutNum") # Only '#' is present for the cut number, this is removing during the sub./split process, so add a string title
                                cnt_data += 1
                            elif cnt_data > 0: 
                                cut_number  = re.sub('[^A-Za-z0-9]+', '', temp_str[0].split(" ")[1])
                                cut_type = temp_str[0].split(" ")[3]

                                if len(temp_str) == 1:
                                    if re.sub('[^A-Za-z0-9]+', '', temp_str[0]) == "endtabular":
                                        if verbose:
                                            print_alert("End of table reached!\n")
                                        continue
                                else:
                                    cut_num.append(int(cut_number))                            # COLUMN 0: store cut num as int
                                    selection.append(cut_type)                                 # COLUMN 1: store selection type
                                    events.append(int(temp_str[1]))                            # COLUMN 2: store num events as int
                                    tot_eff.append(float(temp_str[2]))                         # COLUMN 3: store tot. eff. as float
                                    rel_eff.append(float(temp_str[3]))                         # COLUMN 4: store rel. eff. as float
                                    tot_eff_err.append(float(temp_str[4]))                     # COLUMN 5: store tot. eff. err. as float
                                    rel_eff_err.append(float(temp_str[5].split("hline")[0]))   # COLUMN 5: clean LaTeX formatting and store rel. eff. err. as float
                                    cnt_data += 1
                    data_lists = [cut_num, selection, events, tot_eff, rel_eff, tot_eff_err, rel_eff_err] # store all lists to make filling dictionary easier

                    dict_cnt = 0
                    for datum in data_lists: # fill dictionary with lists
                        cutflow_dict[key][header_titles[dict_cnt]] = datum
                        dict_cnt += 1

                    cnt += 1
            cnt += 1
        if to_pandas: 
            alpha_gen_dict["key"].append(key)
            alpha_gen_dict["alpha"].append(tot_eff[num_gen_cuts])
            alpha_gen_dict["err"].append(tot_eff_err[num_gen_cuts])
        else:
            alpha_gen[key]         = tot_eff[num_gen_cuts]
            alpha_gen_err[key]     = tot_eff_err[num_gen_cuts]
             
        if to_pandas:
            if verbose:
                print_alert("Transferring cutflow table dictionary to pandas dataframe\n")
            
            df_dict[key] = pd.DataFrame.from_dict(cutflow_dict[key])
                        
            if verbose:
                print_alert("Transferring the generator level alpha and error into a dataframe\n")
            
            if save_csv:
                file_name = data_dir + "dataframe_%s.csv" % key
                if verbose:
                    print_alert("Saving pandas dataframe to %s\n" % file_name)
                
                df_dict[key].to_csv(file_name)
    #temp_alpha_gen_dict = {}
    #alpha_gen_df = pd.DataFrame.from_dict(cutflow_dict[key])
    if to_pandas:
        df_alpha = pd.DataFrame.from_dict(alpha_gen_dict)
        if save_csv:
            df_alpha.to_csv(data_dir + "alpha_gen.csv")
            
    
    if ret:
        if to_pandas:
            return cutflow_dict, df_dict, epsilon_alpha, epsilon_alpha_err,  alpha_gen, alpha_gen_err, df_alpha
        else:
            return cutflow_dict, epsilon_alpha, epsilon_alpha_err, alpha_gen, alpha_gen_err
            
