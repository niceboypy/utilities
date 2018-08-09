#!/usr/bin/python3

#version 1.0

import os
import sys
import argparse

if len(sys.argv) < 2:
    print("Inputs not specified", file=sys.stderr)
    sys.exit()

all_flag = '_all_'
#files that should be ignored from the current directory
self_ignore = ['compile.py', 'glad.c', 'glad.h', '.last_compilation']

def get_files(path:"current directory as path"=os.getcwd(),
    ignores:"Files to ignore"=[],
    All:"get all files in curdir"=True, source_files=[], 
    usext:"denotes which extensions to use"=[]):

    """gets files in path ignoring the ones listed in self_ignore"""
    global self_ignore #modifying global variable
    self_ignore += ignores
    if os.path.exists(path):
        if All:
            All = os.listdir(path)
        else:
            All = source_files
            for File in All:
                if not os.path.exists(os.path.join(path, File)):
                    print("-- FILE MISSING Or EMPTY FLAG REQUEST, CHECK IF FLAGS HAVE VALID PARAMETERS ---")
                    print(os.path.join(path, File))
                    
                    
                    sys.exit()
        
        #checks for extension is use_ext=<something>
        if usext:
            Files = []
            for exts in usext:
                Files += [File for File in All if File.endswith(exts)]
            All = Files
        #checks if it is file and whether it is ignored, and joins them to path
        File = ' '.join(os.path.join(path, File) for File in All if (os.path.isfile(os.path.join(path, File)) and (File not in self_ignore)))
    else:
        print("Error getting Files in current directory, see if path is correct/exist.", 
                        file=sys.stderr)
        sys.exit(1)
    return File


compiler_to_use = 'g++'
cpp_compiler_standard='c++17'

#files taken from directory structure
#marked as #self_<name>

#file requirements put in the requirements directory
requirement_path = os.path.join(os.getcwd(), 'requirements')
self_requirements = ''
#requirements are not affected by flags such as useext, all the files in the folder are taken
self_requirements = get_files(requirement_path)

#all libraries to be linked via terminal
libraries_for_glfw='-lGL -lGLU -lglfw3 -lX11 -lXxf86vm -lXrandr -lpthread -lXi -ldl -lXinerama -lXcursor'
self_library_requirements='-lGL -lGLU -lglut'

#set executable path
self_executable_path = os.path.join(os.getcwd(), 'executables')
if not os.path.exists(self_executable_path):
    os.mkdir(self_executable_path)
self_src_path = os.getcwd()

executable = ''

def form_string(args):
    """ form the compilation string and return it """
    def path_check(path):
        if os.path.exists(path):
            return True
        else:
            return False
    
    if args.src[0]=='_all_':
        sources=get_files(args.srcpth, ignores=args.ignore, usext=args.usext)
    elif args.src[0]=='./':
        try:
            with open(os.path.join(os.getcwd(), '.last_compilation'), 'rb') as last_compilation:
                program_location = last_compilation.read().decode()
                os.system("{}".format(program_location))
        except:
            print('No compilation has yet been done Or, compile.py is in different directory\n',
            'Make sure the last compilation was done from this directory')
        else:
            #on successful run, exit the program, nothing more to do
            sys.exit()

    else:
        sources=get_files(args.srcpth, All=False, source_files=args.src, ignores=args.ignore, usext=args.usext)

    extrnpath = args.extrnpath
    if path_check(extrnpath):
        All = True if args.extrnreq[0]=='_all_' else False
        extrnreq = get_files(extrnpath, All=All, source_files=args.extrnreq, usext=args.usext)
    else:
        extrnreq=extrnpath=''
    
    source_files = sources
    global executable
    executable = os.path.join(args.dstpath, args.dst)
    external_files = extrnreq#(os.path.join(extrnpath, File) for File in extrnreq)
    

    return '{} -std={} {} {} {} -o {} {}'.format(args.compiler,
                                            args.std,

                                            source_files,
                                            self_requirements,

                                            external_files,
                                            executable,

                                            self_library_requirements
                        )


# '*' zero or more
# '+' one or more
# '?' one if given if not given taken from default
parser = argparse.ArgumentParser(description="Process files for compilation")
parser.add_argument('--src', '--s', nargs='+', type=str, help='list of source files')

#src file path to take from
parser.add_argument('--srcpth', '--sp', nargs='?', default=self_src_path, help="path to take source files from")
parser.add_argument('--dst', '--d', nargs='?', default='a.out', help="executable output name")
parser.add_argument('--dstpath', '--dp', nargs='?', default=self_executable_path, help="path to output the executable")
parser.add_argument('--ignore', '--i', nargs='*', default=[])


#external_requirements: requirements from another folder rather than in directory structure
parser.add_argument('--extrnpath', '--ep', nargs='?', default='', help='Path to any other C/C++ files to include from external path')
parser.add_argument('--extrnreq', '--er', nargs='+', default=[''], help='Names of external files, "*" for all files in extrnpath')

parser.add_argument('--usext', '--ue', nargs='*', default=[], help="use these extension files only for external files")
#compiler options
parser.add_argument('--compiler', '--c', nargs='?', default=compiler_to_use, choices=['g++', 'gcc'], help="Use C or C++ compiler")
parser.add_argument('--std', nargs='?', default=cpp_compiler_standard, help='C/C++ standard to use')

#make the program run after compilation
parser.add_argument('--run', '--r', nargs='?', default='True', help='run the program after compilation')
parser.add_argument('--info', nargs='?', default='not_show', help='help text')
args = parser.parse_args()
if __name__ == '__main__':

    if args.info == 'show':
        print("""
            DIRECTORY STRUCTURE
        -------------------------
        Root directory(can be renamed):contains subfolders needed and main source files

        includes: standard includes folder

        requirements: files required for source to work, may be omitted if files kept under the root directory

        compile.py: main script to automate compilation, make executable by using chmod. Must be kept under root directory.


        FLAGS:
        -----------------------------------------------------
        NOTE: -----------------------------------------------
        -----------------------------------------------------
        --src and --extrnreq take '_all_' key to denote
        all files in the directory

        The default compiler is g++ and default standart is
        c++17
        -----------------------------------------------------
        -----------------------------------------------------


        --src: specifies source files, defaults to where compile.py is
        --srcpath: path to source file if not under root directory
        --dst: name of executable
        --dstpath: place to compile the executable to
        --ignore: files to ignore, no need to specify the path but must be named
        --extrnpath: external files elsewhere to include for compilation, NOTE:
            path must exist
        --extrnreq: external file names
        --usext: use only these extensions
        --compiler: compiler to use, must be set in environment variable or must
        include full path
        --std: standard to use for compiler
        --run: run the program on compilation. The default is true, set to 'f' to disable.

                """)
        sys.exit(0)

    compilation_string = form_string(args)
    
    
    execution_status = os.system(compilation_string)
    
    
    #store the last compilation; happens if succeeds
    #assumes that the source contains this data
    if not execution_status:
        #if the call was successful
        with open(os.path.join(os.getcwd(), '.last_compilation'), 'wb') as last_compilation:
            executable = executable.strip()
            program_location = executable.encode(encoding='utf-8')
            last_compilation.write(program_location)
    else:
        print("COMPILATION FAILED: \nPlease follow directory structure correctly.")
        sys.exit()
    
    if args.run =='True':
        try:
                with open(os.path.join(os.getcwd(), '.last_compilation'), 'rb') as last_compilation:
                    program_location = last_compilation.read().decode()
                    os.system("{}".format(program_location))
        except:
            print('No compilation has yet been done Or, compile.py is in different directory\n',
            'Make sure the last compilation was done from this directory')
        else:
            #on successful run, exit the program, nothing more to do
            sys.exit()
        