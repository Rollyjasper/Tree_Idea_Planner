
import tkinter as tk
import tkinter.filedialog as tk_file
import tkinter.messagebox as tk_diag
import numpy as np
import os.path as path


class Node():
    def __init__(self,name:tuple,title:str,desc:str,parent:tuple,links:list) -> None:
        self.name = name
        self.title = title
        self.desc = desc
        self.links = links
        self.parent = parent
    
    def add_link(self,new_link:tuple):
        self.links.append(new_link)
    
    def del_link(self,link:tuple):
        index = self.links.index(link)
        del self.links[index]
    
class NodeHandler():
    def __init__(self) -> None:
        self.nodes = {}
        self.levels = {}
    
    def add_node(self,parent:tuple,title:str,desc:str,name:str=None):
        if parent == None:
            name = (0,0)
            self.levels[0] = 1

            self.nodes[name] = Node(name,title,desc,(0,0),[])
        elif name != None:
            self.nodes[name] = Node(name,title,desc,parent,[])
            self.add_link(parent,name)

        else:
            level = parent[0]+1
            try:
                node_no = self.levels[level]
            except KeyError:
                node_no = 0
                self.levels[level] = 1
            else:
                self.levels[level] += 1
            
            name = (level,node_no)

            self.nodes[name] = Node(name,title,desc,parent,[])
            self.add_link(parent,name)
    
    def del_node(self,name,shift=True):
        for link in self.nodes[name].links:
            self.nodes[link].del_link(name)
        level = name[0]
        self.levels[level] -= 1
        del self.nodes[name]

        if (level,self.levels[level]) in self.nodes.keys() and shift == True:
            self.node_shift(level,name[1])
    
    def node_shift(self,level,start):
        for new_num in range(start,self.levels[level]):
            old_num = new_num+1
            old_name = (level,old_num)
            new_name = (level,new_num)
            title = self.nodes[old_name].title
            desc = self.nodes[old_name].desc
            links = self.nodes[old_name].links
            links.remove(self.nodes[old_name].parent)

    
    def add_link(self,node_1,node_2):
        self.nodes[node_1].add_link(node_2)
        self.nodes[node_2].add_link(node_1)
    
    def del_link(self,node_1,node_2):
        self.nodes[node_1].del_link(node_2)
        self.nodes[node_2].del_link(node_1)
    
    def get_node(self,name):
        return self.nodes[name]
    
    def get_links(self,name):
        return self.nodes[name].links



class Window():
    def __init__(self,root) -> None:
        self.root = root

        self.nodes = NodeHandler()

        self.tree_list = {}

        self.save_name = 'Untitled Tree'
        self.edited = False

        self.static()
        self.tree()
    
    def static(self):
        self.frame = tk.Frame(self.root)
        self.frame.grid(row = 0)

        #Tree Buttons
        self.new_button = tk.Button(self.frame,text = 'New Tree', width = 25, command = self.new_on_click)
        self.new_button.grid(row = 0, column=0)

        self.load_button = tk.Button(self.frame,text = 'Load Tree', width = 25, command = self.load_on_click)
        self.load_button.grid(row = 1, column=0)

        self.save_button = tk.Button(self.frame,text = 'Save Tree', width = 25, command = self.save_on_click)
        self.save_button.grid(row = 2, column=0)

        #Node Buttons
        self.addN_button = tk.Button(self.frame,text = 'Add Node', width = 25, command = self.addN_on_click)
        self.addN_button.grid(row = 0, column=1)

        self.delN_button = tk.Button(self.frame,text = 'Delete Node', width = 25, command = self.delN_on_click)
        self.delN_button.grid(row = 1, column=1)

        self.editN_button = tk.Button(self.frame,text = 'Edit Node', width = 25, command = self.editN_on_click)
        self.editN_button.grid(row = 2, column=1)

        #Link Buttons
        self.addL_button = tk.Button(self.frame,text = 'Add Link', width = 25, command = self.addL_on_click)
        #self.addL_button.grid(row = 0, column=2)

        self.delL_button = tk.Button(self.frame,text = 'Delete Link', width = 25, command = self.delL_on_click)
        #self.delL_button.grid(row = 1, column=2)

    def tree(self):
        if self.edited == True:
            self.tree_frame = tk.LabelFrame(self.root,text=self.save_name+'*')
        else:
            self.tree_frame = tk.LabelFrame(self.root,text=self.save_name)
        self.tree_frame.grid(row = 1)

        if self.nodes.nodes:
            groups,sizes = self.level_sizes(self.nodes.levels.keys())

            self.tree_list[(0,0)] = (NodeUI(self.nodes.nodes[(0,0)],self.tree_frame,0,0))
            
            if groups != {}:##This means we have just the root and no children:
                rows = np.zeros(len(self.nodes.levels.keys()),int)
                for parent,nodes in groups.items():
                    for node in nodes:
                        name = node.name
                        column = name[0]
                        self.tree_list[node.name] = NodeUI(node,self.tree_frame,rows[name[0]],column)
                            
                        if name in sizes:
                            if sizes[name] >0:
                                rows[name[0]] += sizes[name]
                            else:
                                rows[name[0]:] += 1
                        else:
                            rows[name[0]] += 1
                    if nodes == []:
                        name = self.nodes.nodes[parent].name
                        rows[name[0]+1:] += 1
            
            for name,UI_obj in self.tree_list.items():
                if name == (0,0):
                    continue
                node_row = UI_obj.row
                node = UI_obj.node
                parent_name = node.parent
                parent = self.tree_list[parent_name]
                parent_row = parent.row
                parent_size = sizes[parent_name]

                if node_row < parent_row:
                    UI_obj.row = parent_row
                    UI_obj.button.destroy()
                    UI_obj.show()
                elif node_row >= parent_row+parent_size:
                    UI_obj.row = parent_row+parent_size-1
                    UI_obj.button.destroy()
                    UI_obj.show()




    def update(self):
        self.tree_frame.destroy()
        self.tree_list = {}
        self.tree()
    
    def group_level(self,level:int,nodes:list):
        grouping = {}
        sizes = {}
        for node in nodes:
            if node.name[0] == level:
                parent = node.parent
                if parent in grouping:
                    grouping[parent].append(node)
                    sizes[parent] += 1
                else:
                    grouping[parent] = [node]
                    sizes[parent] = 1
            elif node.name[0] == level-1:
                if not node.name in grouping:
                    grouping[node.name] = []
                    sizes[node.name] = 0
        
        return grouping,sizes
    
    def level_sizes(self,levels):
        lowest_level = max(levels)
        nodes = self.nodes.nodes.values()
        groups = {}
        sizes = {}

        for level in range(lowest_level,0,-1):
            group,size = self.group_level(level,nodes)
            for key,value in group.items():
                if key in groups:
                    print(key)
                groups[key] = value
            
            for key,value in size.items():
                if key in sizes:
                    print(key)
                if level == lowest_level:
                    sizes[key] = value
                else:
                    total = 0
                    for child in groups[key]:
                        name = child.name
                        child_size = sizes[name]
                        if child_size > 0:
                            total += child_size
                        elif child_size == 0:
                            total += 1
                    sizes[key] = total
            
            for i in range(self.nodes.levels[lowest_level]):
                groups[(lowest_level,i)] = []
                sizes[(lowest_level,i)] = 1
        
        return groups,sizes

    def get_save_string(self):
        string = ''
        for level,size in self.nodes.levels.items():
            for i in range(size):
                name = (level,i)
                node = self.nodes.nodes[name]
                string += '{0},{1},{2},{3},{4}\n'.format(level,i,node.parent[1],node.title,node.desc)
        return string
    
    def new_on_click(self):
        if self.edited == True:
            warn = tk_diag.askokcancel('Unsaved Tree','There are unsaved changes to {}, if you start a new tree, these changes will be lost.'.format(self.save_name))

            if warn == False:
                return

        
        self.save_name = 'Untitled Tree'
        self.nodes = NodeHandler()
        self.edited = False
        self.update()
    
    def load_on_click(self):
        if self.edited == True:
            warn = tk_diag.askokcancel('Unsaved Tree','There are unsaved changes to {}, if you load a saved tree, these changes will be lost.'.format(self.save_name))

            if warn == False:
                return
        
        file = tk_file.askopenfile('r',defaultextension='.sav')
        if file == None:
            return#canceled
        self.nodes = NodeHandler()
        text = file.readlines()

        for line in text:
            l = line.strip('\n').split(',')
            name = (int(l[0]),int(l[1]))
            parent = (int(l[0])-1,int(l[2]))
            title = l[3]
            desc = l[4]

            if parent[0] < 0:
                parent = None
            
            self.nodes.add_node(parent,title,desc)

        self.save_name = path.basename(file.name).split('.')[0]
        file.close()

        self.edited = False
        self.update()
        
    def save_on_click(self):
        file = tk_file.asksaveasfile('w',defaultextension='.sav',initialfile=self.save_name)
        if file == None:
            return#canceled
        text = self.get_save_string()
        file.write(text)
        self.save_name = path.basename(file.name).split('.')[0]
        file.close()

        self.edited = False
        self.update()
    
    def addN_on_click(self):
        dialog_win = tk.Toplevel(self.root)
        win = DiagWin(dialog_win,self,'AN')
    
    def delN_on_click(self):
        dialog_win = tk.Toplevel(self.root)
        win = DiagWin(dialog_win,self,'DN')
    
    def editN_on_click(self):
        dialog_win = tk.Toplevel(self.root)
        win = DiagWin(dialog_win,self,'EN')
    
    def addL_on_click(self):
        pass
    
    def delL_on_click(self):
        pass

class DiagWin():
    def __init__(self,root,master,key):
        self.root = root
        self.master = master
        self.key = key

        self.frame = tk.Frame(self.root)
        self.frame.grid()

        self.show()

    def show(self):
        if self.key == 'AN':
            self.header_str = 'Create a Node'
            self.action_str = 'Add Node'
            self.title_entry(1)
            self.desc_entry(2)
            self.node_selector(3)
            row = 4
        elif self.key == 'DN':
            self.header_str = 'Delete a Node'
            self.action_str = 'Delete Node'
            self.node_selector(1)
            row = 2
        elif self.key == 'EN':
            self.header_str = 'Edit a Node'
            self.action_str = 'Edit Node'
            self.node_selector(1)
            self.title_entry(2)
            self.desc_entry(3)
            row = 4
        else:
            self.header_str = 'Header'
            self.action_str = 'Yes'
            row = 1
        
        self.header = tk.Label(self.frame,text=self.header_str)
        self.header.grid(row=0,column=0,columnspan=2)
        self.actions(row)

    def title_entry(self,row):
        self.title_label = tk.Label(self.frame,text='Name:')
        self.title_label.grid(row=row,column=0)

        self.title_var = tk.StringVar()
        self.title_entry = tk.Entry(self.frame,textvariable=self.title_var)
        self.title_entry.grid(row=row,column=1)
    
    def desc_entry(self,row):
        self.desc_label = tk.Label(self.frame,text = 'Description:')
        self.desc_label.grid(row=row,column=0)

        self.desc_var = tk.StringVar()
        self.desc_entry = tk.Entry(self.frame,textvariable=self.desc_var)
        self.desc_entry.grid(row=row,column=1)
    
    def node_selector(self,row,i=''):
        self.create_node_list()

        self.select_label = tk.Label(self.frame,text='Select Node{}:'.format(i))
        self.select_label.grid(row=row,column=0)

        if self.node_list != {'name':[],'title':[]}:
            values = self.node_list['title'].copy()
            node = values.pop(0)
        else:
            node = 'None'
            values = []
        self.select_var = tk.StringVar(value=node)

        self.select_menu = tk.OptionMenu(self.frame,self.select_var,node,*values,command=self.node_on_select)
        self.select_menu.config(width=15)
        self.select_menu.grid(row=row,column=1)
    
    def actions(self,row):
        self.yes_button = tk.Button(self.frame,text=self.action_str,command=self.yes_on_click)
        self.yes_button.grid(row=row,column=0)

        self.no_button = tk.Button(self.frame,text='Cancel',command=self.no_on_click)
        self.no_button.grid(row=row,column=1)

    def create_node_list(self):
        self.node_list = {'name':[],'title':[]}
        nodes = self.master.nodes.nodes
        for node in nodes.values():
            self.node_list['name'].append(node.name)
            self.node_list['title'].append(node.title)

    def yes_on_click(self):
        if self.key == 'AN':
            title = self.title_var.get()
            desc = self.desc_var.get()
            var = self.select_var.get()

            if var == 'None':
                parent = None
            else:
                i = self.node_list['title'].index(var)
                parent = self.node_list['name'][i]

            self.master.nodes.add_node(parent,title,desc)
        elif self.key == 'DN':
            var = self.select_var.get()

            if var == 'None':
                node = None
            else:
                i = self.node_list['title'].index(var)
                node = self.node_list['name'][i]

            self.master.nodes.del_node(node)
        
        elif self.key == 'EN':
            title = self.title_var.get()
            desc = self.desc_var.get()
            var = self.select_var.get()

            i = self.node_list['title'].index(var)
            node = self.node_list['name'][i]

            self.master.nodes.nodes[node].title = title
            self.master.nodes.nodes[node].desc = desc



        self.master.edited = True
        self.master.update()
        self.root.destroy()
    
    def no_on_click(self):
        self.root.destroy()
    
    def node_on_select(self,val):
        if self.key == 'EN':
            i = self.node_list['title'].index(val)
            node = self.node_list['name'][i]

            desc = self.master.nodes.nodes[node].desc
            self.title_var.set(val)
            self.desc_var.set(desc)


class NodeUI():
    def __init__(self,node:object,frame,row,column) -> None:
        self.node = node
        self.frame = frame

        self.row = row
        self.column = column

        self.show()
    
    def show(self):
        self.button = tk.Button(self.frame,text = self.node.title,width=15,command=self.on_click)
        self.button.grid(row=self.row,column=self.column)
    
    def on_click(self):
        print(self.node.name)

