from glob import glob

class colors:
    WHITE   = '\033[97m'
    CYAN    = '\033[96m'
    MAGENTA = '\033[95m'
    BLUE    = '\033[94m'
    YELLOW  = '\033[93m'
    GREEN   = '\033[92m'
    RED     = '\033[91m'
    ORANGE  = '\033[38;5;208m'
    ENDC    = '\033[39m'
    
def print_info(string, color = colors.GREEN, endcolor = colors.ENDC):
    print(color + string + endcolor)   
    
def print_alert(string, color = colors.YELLOW, endcolor = colors.ENDC):
    print(color + string + endcolor)
    
def print_error(string, color = colors.RED, endcolor = colors.ENDC):
    print(color + string + endcolor)

def get_file_list(base_dir, file_ext = None, recglob = False):
    '''
    S. D. Butalla
    2022/08/17 - v0
    
    Generic function that retrieves a list of files in 
    a specified directory. An option for recursive
    globbing for all subdirectories given a base 
    directory is also available.
    
    Dependencies:
    
    glob
    
    Positional arguments:
    base_dir          : (string) The base directory to
                        retrieve the files from.
    Optional arguments:
    file_ext          : (string) File extension. If not
                        None, all contents of directory
                        will be returned (including    
                        directories).
    recglob           : (bool) Enable recursive 
                        globbing.
    
    Output:
    total_file_list   : (list; string) List of strings
                        of complete file paths
    file_names        : (list; string) List of strings
                        of file names (including those 
                        in subdirectories!).
    '''
    if file_ext is not None:
        if file_ext[0] != ".":
            file_ext = "." + file_ext
    else:
        file_ext = ""

    if recglob:
        total_file_list = glob(f'{base_dir}/*/*%s' % file_ext)
    else:
        total_file_list = glob(f'{base_dir}/*%s' % file_ext)
    
    file_names = [file.split("/")[-1] for file in total_file_list]
    return total_file_list, file_names

