#!/usr/bin/env python
# coding: utf-8

#Allesandro Yudo Agustus 2023

# In[ ]:


import os
import pandas as pd
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox, Label
from tkinter import ttk
import numpy as np

class ScrollableFrame(ttk.Frame):
    def __init__(self, master, *args, **kwargs):
        ttk.Frame.__init__(self, master, *args, **kwargs)

        self.canvas = tk.Canvas(self)
        self.scrollbar = ttk.Scrollbar(self, orient='vertical', command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor='nw')

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

class ColumnSelectionDialog(tk.simpledialog.Dialog):
    def __init__(self, parent, selected_df, title, use_radiobuttons=False, *args, **kwargs):
        self.df = selected_df
        # self.title = title
        self.title2 = title
        self.use_radiobuttons = use_radiobuttons
        super().__init__(parent, *args, **kwargs)

    def body(self, master):
        ttk.Label(master, text= self.title2).pack()

        # Create a scrollable frame for checkboxes
        self.scrollable_frame = ScrollableFrame(master)
        self.scrollable_frame.pack(side="left", fill="both", expand=True)

        # Select a CSV file
        # file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        # if not file_path:
        #     self.result = None
        #     return None

        # Read column headers from the CSV file
        # self.df = selected_df
        columns = self.df.columns.tolist()

        self.column_vars = []
        
        self.selected_var = tk.StringVar()
        self.selected_var.set(None)   
        
        for column in columns:
            if self.use_radiobuttons:
                button = ttk.Radiobutton(self.scrollable_frame.scrollable_frame, text=column, variable=self.selected_var, value=column)
            else:
                var = tk.IntVar()
                button = ttk.Checkbutton(self.scrollable_frame.scrollable_frame, text=column, variable=var)
                # checkbox.pack(anchor='w', padx=10)
                self.column_vars.append(var)
            button.pack(anchor='w', padx=10)        
        
        # for column in columns:

                
        return self.scrollable_frame  # initial focus

    def apply(self):
        if self.df is not None:
            if self.use_radiobuttons:
                selected_columns = self.selected_var.get()
                self.result = selected_columns
                
                self.use_radiobuttons=False
            else:
                # Get selected columns
                selected_columns = [column for var, column in zip(self.column_vars, self.df.columns) if var.get()]
                self.result = selected_columns
            self.destroy()

class FilterDialog(tk.simpledialog.Dialog):

    def __init__(self, master, filter_column):
        self.master = master
        self.filter_column = filter_column
        self.write = False
        self.upload = False
        super().__init__(master)

    def body(self, master):
        # Create a frame for the label
        label_frame = ttk.Frame(master)
        label_frame.grid(row=0, column=0, columnspan=6, pady=10, padx=10)
        
        ttk.Label(label_frame, text="Filter values for column " + self.filter_column + ":").grid(row=0, column=0, pady=(0, 5))

        self.action_var = tk.StringVar()
        write_button = ttk.Radiobutton(label_frame, text="Write Manually", variable=self.action_var, value="write")
        write_button.grid(row=1, column=0)

        upload_button = ttk.Radiobutton(label_frame, text="Upload File", variable=self.action_var, value="upload")
        upload_button.grid(row=2, column=0)

        return write_button

    def apply(self):
        selected_action = self.action_var.get()
        if selected_action == "write":
            self.write = True
            self.upload = False
        elif selected_action == "upload":
            self.write = False
            self.upload = True
        else:
            self.write = False
            self.upload = False
            
        return True
    
class JoinDialog(tk.simpledialog.Dialog):
    def __init__(self, master, title):
        self.master = master
        self.left = False
        self.right = False
        self.inner = False
        self.outer = False
        self.selected_action = None
        super().__init__(master)

    def body(self,master):
        
        label_frame = ttk.Frame(master)
        label_frame.grid(row=0, column=0, columnspan=6, pady=10, padx=10)

        ttk.Label(label_frame, text="Join Option:").grid(row=0, column=0, pady=(0, 5))
        self.action_var = tk.StringVar()
        left_button = ttk.Radiobutton(label_frame, text="Left Join", variable=self.action_var, value="left")
        left_button.grid(row=1, column=0)

        right_button = ttk.Radiobutton(label_frame, text="Right Join", variable=self.action_var, value="right")
        right_button.grid(row=2, column=0)

        inner_button = ttk.Radiobutton(label_frame, text="Inner Join", variable=self.action_var, value="inner")
        inner_button.grid(row=3, column=0)    

        outer_button = ttk.Radiobutton(label_frame, text="Outer Join", variable=self.action_var, value="outer")
        outer_button.grid(row=4, column=0)                    


    def apply(self):
        self.selected_action = self.action_var.get()
        if self.selected_action == "left":
            self.left = True
        elif self.selected_action == "right":
            self.right = True
        elif self.selected_action == "inner":
            self.inner = True
        elif self.selected_action == "outer":
            self.outer = True

class FileMerger:
    def __init__(self, master):
        # General App Styling
        self.master = master
        master.title("File Merger")
        master.geometry('600x520')
        master.configure(bg="#F0F0F0")  # Setting a light gray background color
        
        style = ttk.Style()
        style.configure("TButton", font=("Arial", 10), padding=10)
        style.configure("TLabel", font=("Arial", 10), background="#F0F0F0")
        
        self.label = ttk.Label(master, text="Welcome To CSV Files Combiner", font="Arial 20 bold", foreground="dark orange")
        self.label.grid(row=0, column=0, columnspan=6, pady=10, padx=10)

        info_labels = [
            "This is a CSV files combiner with easy to use, read these first:",
            "1). This app uses the first file of your folder as header.",
            "2). Make sure that the data you input has the same count of columns.",
            "3). Once you click the Process Files button, wait for it to finish."
        ]

        for index, text in enumerate(info_labels, start=1):
            ttk.Label(master, text=text).grid(row=index, column=0, columnspan=6, sticky='w', pady=5, padx=20)

        # Directory Button and Label
        self.choose_directory_button = ttk.Button(master, text="Choose Your FS Folder", command=self.set_directory)
        self.choose_directory_button.grid(row=20, column=0, pady=5, padx=5,sticky="w")
        self.directory_label = ttk.Label(master, text="")
        self.directory_label.grid(row=25, column=0, padx=20, sticky="w")

        # Output Directory Button and Label
        self.choose_output_directory_button = ttk.Button(master, text="Choose Output Directory", command=self.set_output_directory)
        self.choose_output_directory_button.grid(row=30, column=0, pady=5, padx=5, sticky="w")
        self.output_directory_label = ttk.Label(master, text="")
        self.output_directory_label.grid(row=35, column=0, padx=20, sticky="w")
        
        # Filter Label and Button
        self.apply_filter_label = ttk.Label(master, text="")
        self.apply_filter_label.grid(row=25, column=3, pady=0, padx=0)
        self.filter_button = ttk.Button(master, text="Filter", command=self.apply_filter)
        self.filter_button.grid(row=20, column=3, pady=20, padx=20)
        
        # Keep column Label and Button
        self.columns_label = ttk.Label(master, text="")
        self.columns_label.grid(row=35, column=3, pady=0, padx=0)
        self.columns_button = ttk.Button(master, text="Columns Keep", command=self.keep_columns)
        self.columns_button.grid(row=30, column=3, pady=20, padx=20)
        
        # Filename label and Button
        self.add_filename_label = ttk.Label(master, text="")
        self.add_filename_label.grid(row=25, column=4, pady=5, padx=5)
        self.add_filename_button = ttk.Button(master, text="Filename Column", command=self.add_filename_column)
        self.add_filename_button.grid(row=20, column=4, pady=20, padx=20)
        
        # Remove duplicates label and Button
        self.remove_dups_label = ttk.Label(master, text="")
        self.remove_dups_label.grid(row=35, column=4, pady=5, padx=5)
        self.remove_dups_button = ttk.Button(master, text="Remove Duplicates", command=self.remove_duplicates)
        self.remove_dups_button.grid(row=30, column=4, pady=20, padx=20)
        
        # Join Files Button
        self.join_files_label = ttk.Label(master, text="")
        self.join_files_label.grid(row=50, column=4, pady=5, padx=5)            
        self.join_files_button = ttk.Button(master, text="Join Files", command=self.join_files)
        self.join_files_button.grid(row=45, column=4, pady=20, padx=20)
        
        # "SUM Amount" button
        self.sum_amount_label = ttk.Label(master, text="")
        self.sum_amount_label.grid(row=50, column=3, pady=5, padx=5)        
        self.sum_amount_button = ttk.Button(master, text="SUM Amount", command=self.sum_amount)
        self.sum_amount_button.grid(row=45, column=3, pady=20, padx=20)
    
        
        # Merge Button
        self.merge_button = ttk.Button(master, text="Process Files", command=self.merge_files)
        self.merge_button.grid(row=45, column=0, pady=20, padx=20, sticky="w")
        
        master.grid_columnconfigure(3, weight=1)
        master.grid_rowconfigure(3, weight=1)

        self.directory = None
        self.output_directory = None
        self.filter_column = None
        self.filter_values = None
        self.columns_to_keep = None
        self.remove_dups = False
        self.add_filename = False 
        self.groupby_text = None
        self.sum_text = None
        self.key_column = None
        self.right_column = None
        self.right_df = None
        self.right_return = None
        self.join_option = None


        
    def set_directory(self):
        self.directory = filedialog.askdirectory(title="Choose Your FS Folder")
        num_files = len([f for f in os.listdir(self.directory) if f.endswith('.csv')])
        os.chdir(self.directory)
        self.csv_files = [f for f in os.listdir(self.directory) if f.endswith('.csv')]
        # self.first_df = pd.read_csv(self.csv_files[0], encoding='utf-8-sig', dtype=str, keep_default_na=False, na_values=[''])
        self.directory_label.config(text=f"Number of files: {num_files}")

        

    def set_output_directory(self):
        self.output_directory = filedialog.askdirectory(title="Choose Output Directory")
        self.output_directory_label.config(text="Output Path Chosen")
        
    def apply_filter(self):
        if not self.directory:
            messagebox.showwarning("Warning", "Please choose the FS Folder first.")
            return

        filter_option = messagebox.askyesno("Filter Option", "Do you want to apply a filter?")
        if not filter_option:
                 
            self.apply_filter_label.config(text="")
            self.filter_columns = None
            self.filter_values = None            
            return

        try:
            filter_df = pd.read_csv(self.csv_files[0])
            # Create and show the column selection dialog
            column_dialog = ColumnSelectionDialog(self.master, selected_df=filter_df, title= "Select Column to Filter")
            # Wait for the dialog to close
            column_dialog_result = column_dialog.result

            if column_dialog_result:
                # Retrieve selected columns from the dialog
                self.filter_columns = column_dialog.result
                # column_string = ', '.join(str(item) for item in filter_columns)
                # self.filter_column = column_string
                self.filter_values = []
                self.filter_column = ""

                for column in self.filter_columns:
                    self.filter_column = column
                
                    dialog = FilterDialog(self.master, self.filter_column)
                    
                    if dialog.write:
                        
                        # self.filter_column = column_string #int(simpledialog.askstring("Filter Column", "Enter the column number for filtering (starting from 0):"))
                        filter_string = simpledialog.askstring("Filter Values", "Enter filter values separated by commas:")
                        column_filter_values = filter_string.split(',')
                        self.filter_values.append(column_filter_values)
                        # self.apply_filter_label.config(text=f"Filter in column {self.filter_column}: \n{', '.join(self.filter_values)}")
                        
                    elif dialog.upload:
                        filter_file_path = filedialog.askopenfilename(title="Upload Filter Values Excel File (The First Row Reads as Header)", filetypes=[("Excel files", "*.xlsx"), ("CSV files", "*.csv")])

                        if filter_file_path:
                            # Read filter values from the uploaded file
                            filter_values_df = pd.read_excel(filter_file_path)  # Assuming it's an Excel file, adjust if it's a CSV
                            column_filter_values = filter_values_df.iloc[:, 0].tolist()
                            self.filter_values.append(column_filter_values)

                            # self.apply_filter_label.config(text=f"Filter in column {self.filter_column}: \n{', '.join(map(str, self.filter_values))}")
                filter_text = "\n".join(f"Filter {column}: {', '.join(map(str, values))}" for column, values in zip(self.filter_columns, self.filter_values))
                self.apply_filter_label.config(text=filter_text)

            else:
                return
                        
        except ValueError as ve:
            messagebox.showerror("Error", "Please enter a valid column number and filter values.")
    
    def keep_columns(self):
        if not self.directory:
            messagebox.showwarning("Warning", "Please choose the FS Folder first.")
            return

        keep_option = messagebox.askyesno("Keep Columns Option", "Do you want to keep specific columns?")
        if not keep_option:
            self.columns_to_keep = None
            self.columns_label.config(text="")
            return

        try:
            kcolumn_df = pd.read_csv(self.csv_files[0])
            # self.title = "Select column to keep"
            # Create and show the column selection dialog
            column_dialog = ColumnSelectionDialog(self.master, selected_df=kcolumn_df, title= "Select Column to Keep")
            # Wait for the dialog to close
            column_dialog_result = column_dialog.result

            if column_dialog_result:            
                # column_string = simpledialog.askstring("Keep Columns", "Enter the column numbers to keep, separated by commas:")
                keep_columns = column_dialog.result
                # column_string = ', '.join(str(item) for item in keep_columns)
                self.columns_to_keep = keep_columns #[str(i) for i in column_string.split(',')]
                self.columns_label.config(text=f"Columns to keep:\n {', '.join(map(str, self.columns_to_keep))}")

        except ValueError as ve:
            messagebox.showerror("Error", "Please enter valid column numbers separated by commas.")
    
    def add_filename_column(self):
#         self.add_filename = False   # Initialize a flag attribute to False

        option = messagebox.askyesno("Add Filename", "Do you want to add filename as a new column?")
        if option:
            self.add_filename = True   # Set the flag to True if user selects "yes"
            self.add_filename_label.config(text="Yes")
        else:
            self.add_filename = False
            self.add_filename_label.config(text="")
            
    def remove_duplicates(self):
        self.remove_dups = False   # Initialize a flag attribute to False

        option = messagebox.askyesno("Remove Duplicates", "Do you want to remove duplicates in the result file?")
        if option:
            self.remove_dups = True  # Set the flag to True if user selects "yes"
            self.remove_dups_label.config(text="Yes")    
        else:
            self.remove_dups = False
            # Update status check label if user selects "No"
            self.remove_dups_label.config(text="")
            
        
    def join_files(self):
        
        if not self.directory:
            messagebox.showwarning("Warning", "Please choose the CSV Folder first.")
            return
        
#         self.fs02_data = None
        # Ask for confirmation
        confirm_join_files = messagebox.askyesno(
            "Join Files Confirmation",
            "This will join / lookup values of the result file with another file you choose, continue?"
        )

        if confirm_join_files:
#             # Ask user to choose the FS02 folder
            
            df_file_path = filedialog.askopenfilename(title="Select a CSV / Excel File To Join", filetypes=[("all files", "*.*")])

            if df_file_path:
                # Get the file extension
                _, file_extension = os.path.splitext(df_file_path)

                # Read filter values from the uploaded file
                if file_extension == ".xlsx":
                    values_df = pd.read_excel(df_file_path)
                elif file_extension == ".csv":
                    values_df = pd.read_csv(df_file_path)
                else:
                    print("Unsupported file type.")
            self.right_df = values_df
            column_values = values_df.iloc[:, 0].tolist()
            
            dialog = JoinDialog(self.master, title="Select Join Option")

            if dialog.left:
                join_option = "left"
            elif dialog.right:
                join_option = "right"
            elif dialog.inner:
                join_option = "inner"
            elif dialog.outer:
                join_option = "outer"
            elif dialog.all:
                join_option = "all"
            else:
                return
    
            self.join_option = join_option
            key_df = pd.read_csv(self.csv_files[0])
            # dialog_text = self.action_var.get()
           # Determine whether to use Radiobuttons or Checkbuttons
            use_radiobuttons = True

            # Create and show the column selection dialog
            column_dialog = ColumnSelectionDialog(self.master, selected_df=key_df, title="Select Left File Primary Key Column", use_radiobuttons=use_radiobuttons)
            # Wait for the dialog to close
            column_dialog_result = column_dialog.result

            if column_dialog_result:
                
                # Retrieve selected columns from the dialog
                primarykey_columns = column_dialog.result
                # column_string = ', '.join(str(item) for item in filter_columns)

                self.key_column = primarykey_columns 
            else:
                return

            right_dialog = ColumnSelectionDialog(self.master, selected_df=values_df, title="Select Right File Primary Key Column", use_radiobuttons=use_radiobuttons)
            # Wait for the dialog to close
            right_dialog_result = right_dialog.result

            if right_dialog_result:
                
                # Retrieve selected columns from the dialog
                rightkey_columns = right_dialog.result
                # column_string = ', '.join(str(item) for item in filter_columns)

                self.right_column = rightkey_columns 
            else:    
                return            


            use_radiobuttons = False

            # Create and show the column selection dialog
            return_dialog = ColumnSelectionDialog(self.master, selected_df=values_df, title= "Select Column to Return")
            # Wait for the dialog to close
            return_dialog_result = return_dialog.result
            self.right_return = return_dialog_result

            # Update status check label
            self.join_files_label.config(text=f"{join_option} join")

        else:
            # Update status check label if user selects "No"
            self.join_files_label.config(text="")
#             use_radiobuttons = False
            self.key_column = None
            self.join_option = None
    

    # def load_fs02_files(self, fs02_folder):
    #     if self.status_check_label.cget("text") == "FS02 Folder Chosen":
    #         print("Loading FS02 files...")
    #         # Create an empty list to hold dataframes
    #         fs02_dfs = []
    #         all_files = sorted([f for f in os.listdir(fs02_folder) if f.endswith('.csv')])

    #         # Load the header from the first file
    #         header_file_path = os.path.join(fs02_folder, all_files[0])
    #         first_fs02_df = pd.read_csv(header_file_path, encoding='unicode_escape', dtype={0: str}, low_memory=False)
    #         header = first_fs02_df.columns.tolist()
    #         fs02_dfs.append(first_fs02_df)
    #         keep_column = ['Policy Number for Check', first_fs02_df.columns[4], 'FS02 File Name']

    #         # Iterate through the rest of the files in the FS02 directory using the header from the first file
    #         for filename in all_files[1:]:
    #             filepath = os.path.join(fs02_folder, filename)
    #             fs02 = pd.read_csv(filepath, encoding='unicode_escape', dtype={0: str}, header=None, names=header, low_memory=False)
    #             fs02["FS02 File Name"] = filename                
    #             fs02_dfs.append(fs02)

    #         # Concatenate all dataframes in the list into a single dataframe
    #         df02 = pd.concat(fs02_dfs, ignore_index=True)

    #         df02.rename(columns={df02.columns[0]: 'Policy Number for Check'}, inplace=True)
    #         df02 = df02[keep_column]

    #         # Drop duplicates keeping the last entry and reset index
    #         df02 = df02.drop_duplicates(subset=df02.columns[0], keep='last').reset_index(drop=True)
    #         print("FS02 files loaded successfully!")

    #         return df02
        
    def sum_amount(self):
        confirm_sum_amount = messagebox.askyesno(
            "Sum Amount Confirmation",
            "This will Group The Columns & Sum Numerical Value, continue?"
        )
        
        if confirm_sum_amount:
        
            if not self.directory:
                messagebox.showwarning("Warning", "Please choose the FS Folder first.")
                return
            
            sum_df = pd.read_csv(self.csv_files[0])
            
            # Create and show the column selection dialog
            column_dialog = ColumnSelectionDialog(self.master, selected_df=sum_df, title= "             Select Column to SUM \n(selected column will be grouped by others)")
            # Wait for the dialog to close
            column_dialog_result = column_dialog.result

            if column_dialog_result:            
                selected_sum = column_dialog.result
                self.sum_text = selected_sum
            # # Ask the user for column indices to sum
            # self.sum_text = simpledialog.askstring("Sum Columns", "Enter column numbers to sum (comma-separated):")
            # if self.sum_text is None:
            #     return                        
            
#             # Ask the user for column indices to group by
#             self.groupby_text = simpledialog.askstring("Group By Columns", "Enter column numbers to group by (comma-separated or 'all' for all columns):")
#             if self.groupby_text is None:
#                 return

                self.sum_amount_label.config(text=f"column to SUM: {', '.join(map(str, self.sum_text))}")
        
        else:
            self.sum_amount_label.config(text="")
#             self.groupby_text = None
            self.sum_text = None            
        
#             return groupby_text, sum_text

        
    def merge_files(self):
        if not self.directory or not self.output_directory:
            messagebox.showwarning("Warning", "Please choose both the FS Folder and Output Directory.")
            return
            
        output_file_name = simpledialog.askstring("Output File Name", "Please enter the output file name:", initialvalue="Combined.csv")
        if not output_file_name:
            return
        
        try:
            print("Processing the files...")                 

#             if self.status_check_label.cget("text") == "FS02 Folder Chosen":
            
            os.chdir(self.directory)
            csv_files = self.csv_files #[f for f in os.listdir(self.directory) if f.endswith('.csv')]
            first_df = pd.read_csv(csv_files[0], encoding='utf-8-sig', dtype=str, keep_default_na=False, na_values=[''])
            self.first_df = first_df
            column_names = first_df.columns.tolist()

            dfs = []
            
            for filename in csv_files:
                print(f"Combining file: {filename}")

                try:
                    df = pd.read_csv(filename, encoding='utf-8-sig', dtype=str, keep_default_na=False, na_values=[''])
                except UnicodeDecodeError:
                    print(f"Failed to read {filename} with utf-8-sig encoding. Trying ISO-8859-1...")
                    df = pd.read_csv(filename, encoding='ISO-8859-1', dtype=str, keep_default_na=False, na_values=[''], warn_bad_lines=True, error_bad_lines=False)

                df.columns = column_names
                
                # Apply the filter if values were set
                if self.filter_column is not None and self.filter_values:
                    for filter_column, filter_values in zip(self.filter_columns, self.filter_values):
                            # Clean up the filter values
                            filter_values = [value.strip() for value in filter_values]
                            # Apply the filter to the DataFrame
                            df = df[df[filter_column].isin(filter_values)]
                    

                # Apply column keep
                if self.add_filename_label.cget("text") == "Yes": 
                    df['File Name'] = filename
                    
#                 if self.columns_to_keep is not None:
                
#                     if self.add_filename_label.cget("text") == "Yes":
#                         selected_columns = self.columns_to_keep + [-1]
#                         df = df.iloc[:, selected_columns]
#                     else:
#                         df = df.iloc[:, self.columns_to_keep]       
                    
#                 if self.add_filename:
#                     df['File Name'] = filename
        
                dfs.append(df)
        
            first_combined_df = pd.concat(dfs, ignore_index=True)
            
            combined_df = first_combined_df.copy()

            if self.join_option is not None:
                print("Joining the two files...")
                # Adjust data types

                combined_df[self.key_column] = combined_df[self.key_column].astype(str)

                self.right_df[self.right_column] = self.right_df[self.right_column].astype(str)

                # Merge dataframes
                combined_df = pd.merge(combined_df, self.right_df[[self.right_column] + self.right_return],
                                        left_on=combined_df[self.key_column], right_on=self.right_df[self.right_column], how=self.join_option)                   
                # Drop the unnecessary column if it exists
                if self.right_column + '_y' in combined_df.columns:
                    combined_df.drop(columns=self.right_column + '_y', inplace=True)

                # Rename the left primary key column to its original name
                combined_df.rename(columns={self.right_column + '_x': self.right_column}, inplace=True)  
            
#             combined_df.info()
            
            if self.columns_to_keep is not None:
                print("Removing Unwanted Columns...")
                if self.add_filename_label.cget("text") == "Yes" and self.join_option is not None:
                    selected_columns = self.columns_to_keep + ['File Name'] + self.right_return
                    combined_df = combined_df[selected_columns]                  
                elif self.add_filename_label.cget("text") == "Yes" and self.join_option is None:
                    selected_columns = self.columns_to_keep + ['File Name']
                    combined_df = combined_df[selected_columns]
                elif self.add_filename_label.cget("text") == "" and self.join_option is not None:
                    selected_columns = self.columns_to_keep + self.right_return
                    combined_df = combined_df[selected_columns]
                  
                else:
                    combined_df = combined_df[self.columns_to_keep]                   

            
           # Check if both groupby_col and sum_col are not empty
            if self.sum_text is not None:
                print('Aggregating...')
                
                # sum_numbers = [int(num.strip()) for num in self.sum_text.split(",")]
                # selected_sum = #[first_combined_df.columns[i] for i in sum_numbers]
                
#                 if self.groupby_text.strip().lower() == 'all':
#                 if self.columns_to_keep is not None:
#                     groupby_numbers = self.columns_to_keep
#                     groupby_numbers = [combined_df.columns[i] for i in groupby_numbers]
#                     groupby_numbers = [item for item in groupby_numbers if item not in selected_sum]
#                     print(groupby_numbers)
#                 else:

                # Group by all visible columns
                selected_sum = self.sum_text
                groupby_numbers = combined_df.columns.tolist()  # Transform to column names
                groupby_numbers = [item for item in groupby_numbers if item not in selected_sum]
#                 print(groupby_numbers)
#             else:
#                 try:
#                     groupby_numbers = [int(num.strip()) for num in self.groupby_text.split(",")]
#                     groupby_numbers = [combined_df.columns[i] for i in groupby_numbers]
#                 except ValueError:
#                     messagebox.showerror("Error", "Invalid input for group by columns.")


                for column_name in selected_sum:
                    combined_df[column_name] = combined_df[column_name].astype('float64')
            
#                 combined_df.info()
#                 print(groupby_numbers)
#                 print(selected_sum)
#                 for_sum = []
#                 for col in selected_sum:
#                     for_sum.append(col + ": 'sum'")

                combined_df = combined_df.fillna('Missing')    
#                 combined_df = combined_df.groupby([groupby_numbers])[selected_sum].agg('sum')
                combined_df = combined_df.groupby(groupby_numbers, as_index = False).agg({col: "sum" for col in selected_sum})
                combined_df = combined_df.replace('Missing', np.nan)   
                  
            
            if self.remove_dups:
                print("Removing duplicates...")
                combined_df.drop_duplicates(inplace=True)
            
            combined_df.reset_index(drop=True, inplace=True)

            output_path = os.path.join(self.output_directory, output_file_name)
            combined_df.to_csv(output_path, index=False)
            print("Done!")
            messagebox.showinfo("Info", f"Combined data saved to: {output_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = FileMerger(root)
    root.mainloop()