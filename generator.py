import argparse
import os
import subprocess
from shutil import copyfile,rmtree
import re
import itertools
import tarfile

from Tkinter import *
import Tkinter, Tkconstants, tkFileDialog
import ttk

_SEP = "_"

class ImageGUI:

    def __init__(self,master):
        self.master = master
        self.create_containers()
        self.create_layout()

    def create_containers(self):
        self.file_path = StringVar()
        self.var_options_list = []

    def create_layout(self):
        select_file_frame = Frame(self.master)
        Label(select_file_frame, text="Image TeX File:").pack(side=LEFT)
        self.file_entry = Entry(select_file_frame,textvariable=self.file_path,width=20)
        self.file_entry.pack(side=LEFT)
        Button(select_file_frame,text="+",command=lambda:self.select_file("Select File",self.file_path,self.file_entry)).pack(side=LEFT)
        select_file_frame.pack(side=TOP)

        ttk.Separator(self.master).pack(fill="x")

        self.var_frame = Frame(self.master)
        self.var_frame.pack()
        # self.add_var()

        # Button(self.master,text="Add Another",command=self.add_var).pack()

        ttk.Separator(self.master).pack(fill="x")

        Button(self.master,text="Generate",command=self.generate_images).pack()

    def select_file(self,type,input_file,input_entry):
		Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
		filename = tkFileDialog.askopenfilename() # show an "Open" dialog box and return the path to the selected file
		input_file = filename
		input_entry.delete(0,END)
		input_entry.insert(0,filename)

		self.identify_vars()

    def add_var(self,var_name):
        f = Frame(self.var_frame)

        var_options = StringVar()
        self.var_options_list.append(var_options)

        Label(f,text="List of options for " + var_name + ":").pack(side=LEFT)
        Entry(f,textvariable=var_options,width=12).pack(side=LEFT)

        f.pack(side=TOP)

    def identify_vars(self):
        _LOCATION = '/'.join(self.file_path.get().split('/')[0:-1])
        input_filename = self.file_path.get().split('/')[-1:][0]

        _REG = '\\\\newcommand\\\\\w+\{[\w.-]+\}'

        with open(os.path.join(_LOCATION,input_filename),'r') as f:
            filename_base = input_filename.split('.')[0]
            content = f.read()

        reg = re.compile(_REG)
        newcommand_strings = reg.findall(content)

        for s in [s.split('\\')[2].split('{')[0] for s in newcommand_strings]:
            print s
            self.add_var(s)

    def generate_images(self):
        # _LOCATION = '/'.join(os.path.realpath(__file__).split('/')[0:-1])
        _LOCATION = '/'.join(self.file_path.get().split('/')[0:-1])
        input_filename = self.file_path.get().split('/')[-1:][0]

        _REG = '\\\\newcommand\\\\\w+\{[\w.-]+\}'

        input_base = input_filename.split('.')[0]

        os.mkdir(os.path.join(_LOCATION,'temp'))
        os.mkdir(os.path.join(_LOCATION,input_base))

        with open(os.path.join(_LOCATION,input_filename),'r') as f:
            filename_base = input_filename.split('.')[0]
            content = f.read()

        reg = re.compile(_REG)
        newcommand_strings = reg.findall(content)

        num_vals = len(self.var_options_list)
        vals = [val.get().split(',') for val in self.var_options_list]
        val_combinations = list(itertools.product(*vals))

        for val_set in val_combinations:
            val_set = list(val_set)
            print val_set
            output_folder = os.path.join(_LOCATION,'temp')
            output_filename = filename_base + _SEP + _SEP.join(val_set) + '.tex'

            output_content = content
            for i in range(len(val_set)):
                output_content = output_content.replace(newcommand_strings[i],newcommand_strings[i].split('{')[0]+'{'+val_set[i]+'}')

            with open(os.path.join(output_folder,output_filename),'w+') as f:
                f.write(output_content)

            os.chdir(output_folder)

            os.system('pdflatex ' + output_filename)
            os.system('convert -density 300x300 ' + '.'.join(output_filename.split('.')[0:-1]) + '.pdf' + ' ' + '.'.join(output_filename.split('.')[0:-1]) + '.png')
            # cmd = ['pdflatex', '-shell-escape', output_filename]
            # proc = subprocess.Popen(cmd)
            # proc.communicate()

            os.chdir("..")

            output_imagename = ".".join(output_filename.split('.')[0:-1]) + '.png'
            copyfile(os.path.join(output_folder,output_imagename),os.path.join(_LOCATION,input_base,output_imagename))

        with tarfile.open(os.path.join(_LOCATION,input_base+'.tgz'), "w:gz") as tar:
            tar.add(os.path.join(_LOCATION,input_base), arcname=os.path.sep)

        rmtree(output_folder)
        rmtree(os.path.join(_LOCATION,input_base))

root = Tk()
my_gui = ImageGUI(root)
root.mainloop()
