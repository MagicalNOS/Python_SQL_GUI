import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import mysql.connector
import pandas as pd
from tkinter.scrolledtext import ScrolledText

class DatabaseQueryGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("数据库查询工具")
        self.root.geometry("1100x700")
        self.connection = None
        
        # 创建左右分隔的主框架
        self.paned = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 左侧面板
        left_frame = ttk.Frame(self.paned)
        self.paned.add(left_frame, weight=3)
        
        # 右侧面板 - 数据库树形视图
        right_frame = ttk.Frame(self.paned)
        self.paned.add(right_frame, weight=1)
        
        # 创建数据库连接配置区域
        connection_frame = ttk.LabelFrame(left_frame, text="数据库配置", padding="5")
        connection_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 数据库选择下拉框
        ttk.Label(connection_frame, text="数据库类型:").grid(row=0, column=0, sticky=tk.W, pady=4)
        self.db_type = ttk.Combobox(connection_frame, values=["MySQL"])
        self.db_type.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2)
        self.db_type.set("MySQL")
        
        # 服务器地址
        ttk.Label(connection_frame, text="服务器地址:").grid(row=1, column=0, sticky=tk.W, pady=4)
        self.server_entry = ttk.Entry(connection_frame)
        self.server_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2)
        self.server_entry.insert(0, "127.0.0.1")
        
        # 端口
        ttk.Label(connection_frame, text="端口:").grid(row=1, column=2, sticky=tk.W, pady=4, padx=(10,0))
        self.port_entry = ttk.Entry(connection_frame, width=10)
        self.port_entry.grid(row=1, column=3, sticky=(tk.W, tk.E), pady=2)
        self.port_entry.insert(0, "3306")
        
        # 用户名
        ttk.Label(connection_frame, text="用户名:").grid(row=2, column=0, sticky=tk.W, pady=4)
        self.username_entry = ttk.Entry(connection_frame)
        self.username_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=2)
        self.username_entry.insert(0, "kevin")
        
        # 密码
        ttk.Label(connection_frame, text="密码:").grid(row=2, column=2, sticky=tk.W, pady=2, padx=(10,0))
        self.password_entry = ttk.Entry(connection_frame, show="$")
        self.password_entry.grid(row=2, column=3, sticky=(tk.W, tk.E), pady=2)
        self.password_entry.insert(0,"password")
        
        # 数据库选择下拉框
        ttk.Label(connection_frame, text="选择数据库:").grid(row=3, column=0, sticky=tk.W, pady=4)
        self.database_combobox = ttk.Combobox(connection_frame, state='readonly')
        self.database_combobox.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=2)
        self.database_combobox.bind('<<ComboboxSelected>>', self.on_database_selected)
        
        # 连接状态标签
        self.status_label = ttk.Label(connection_frame, text="未连接", foreground="red")
        self.status_label.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # 连接和刷新按钮
        button_frame = ttk.Frame(connection_frame)
        button_frame.grid(row=4, column=2, columnspan=2, pady=5)
        
        self.connect_btn = ttk.Button(button_frame, text="连接服务器", command=self.connect_server)
        self.connect_btn.pack(side=tk.LEFT, padx=5)
        
        self.refresh_btn = ttk.Button(button_frame, text="刷新", command=self.refresh_connection)
        self.refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # 创建查询区域框架
        query_frame = ttk.LabelFrame(left_frame, text="SQL查询", padding="5")
        query_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # SQL查询输入框
        self.query_text = ScrolledText(query_frame, height=8, width=80)
        self.query_text.pack(fill=tk.X, pady=5)
        
        # 执行按钮
        ttk.Button(query_frame, text="执行查询", command=self.execute_query).pack(anchor=tk.W, pady=5)
        
        # 创建结果区域框架
        result_frame = ttk.LabelFrame(left_frame, text="查询结果", padding="5")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 结果显示区域
        self.result_text = ScrolledText(result_frame)
        self.result_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 右侧数据库树形视图
        tree_frame = ttk.LabelFrame(right_frame, text="数据库结构", padding="5")
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建树形视图
        self.tree = ttk.Treeview(tree_frame, show="tree")
        self.tree.pack(fill=tk.BOTH, expand=True)

    def connect_server(self):
        """连接到数据库服务器"""
        try:
            # 关闭已存在的连接
            if self.connection:
                self.connection.close()
            
            # 创建新连接
            self.connection = mysql.connector.connect(
                host=self.server_entry.get(),
                port=int(self.port_entry.get()),
                user=self.username_entry.get(),
                password=self.password_entry.get()
            )
            
            self.status_label.config(text="已连接服务器", foreground="green")
            
            # 获取所有数据库并更新下拉框和树形视图
            self.update_database_list()
            self.update_database_tree()
            messagebox.showinfo("成功", "服务器连接成功！")
            
        except Exception as e:
            self.status_label.config(text="连接失败", foreground="red")
            self.connection = None
            messagebox.showerror("错误", f"连接失败：{str(e)}")

    def update_database_list(self):
        """更新数据库下拉列表"""
        if self.connection:
            cursor = self.connection.cursor()
            cursor.execute("SHOW DATABASES")
            databases = [db[0] for db in cursor.fetchall()]
            self.database_combobox['values'] = databases
            cursor.close()

    def refresh_connection(self):
        """刷新连接"""
        self.connect_server()

    def on_database_selected(self, event):
        """当选择数据库时的处理函数"""
        if self.connection:
            try:
                selected_db = self.database_combobox.get()
                cursor = self.connection.cursor()
                cursor.execute(f"USE {selected_db}")
                self.status_label.config(text=f"已选择数据库: {selected_db}", foreground="green")
                cursor.close()
            except Exception as e:
                messagebox.showerror("错误", f"切换数据库失败：{str(e)}")

    def update_database_tree(self):
        """更新数据库树形视图"""
        # 清空现有树形视图
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            cursor = self.connection.cursor()
            
            # 获取所有数据库
            cursor.execute("SHOW DATABASES")
            databases = cursor.fetchall()
            
            # 添加所有数据库节点
            for database in databases:
                db_name = database[0]
                db_node = self.tree.insert("", "end", text=db_name, values=(db_name,), tags=("database",))
                
                # 获取当前数据库的所有表
                cursor.execute(f"USE {db_name}")
                cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()
                
                # 添加表到数据库节点下
                for table in tables:
                    table_name = table[0]
                    table_node = self.tree.insert(db_node, "end", text=table_name, values=(table_name,), tags=("table",))
                    
                    # 获取表结构
                    cursor.execute(f"DESCRIBE {table_name}")
                    columns = cursor.fetchall()
                    
                    # 添加列到表节点下
                    for column in columns:
                        column_name = column[0]
                        column_type = column[1]
                        self.tree.insert(table_node, "end", text=f"{column_name} ({column_type})", tags=("column",))
                        
            cursor.close()
            
        except Exception as e:
            messagebox.showerror("错误", f"更新数据库结构失败：{str(e)}")
            
    def format_results(self, cursor):
        """格式化查询结果"""
        columns = cursor.column_names
        rows = cursor.fetchall()
        
        if not rows:
            return "查询完成，但没有返回任何结果。"
            
        # 使用pandas创建表格形式的输出
        df = pd.DataFrame(rows, columns=columns)
        return df.to_string()
            
    def execute_query(self):
        if not self.connection:
            messagebox.showwarning("警告", "请先连接到数据库！")
            return
            
        query = self.query_text.get("1.0", tk.END).strip()
        if not query:
            messagebox.showwarning("警告", "请输入SQL查询语句！")
            return
            
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            
            # 清空结果框
            self.result_text.delete("1.0", tk.END)
            
            # 如果是SELECT查询，显示结果
            if query.strip().upper().startswith("SELECT"):
                results = self.format_results(cursor)
                self.result_text.insert("1.0", results)
            else:
                self.connection.commit()
                self.result_text.insert("1.0", f"查询执行成功，影响的行数：{cursor.rowcount}")
                # 如果执行的是修改类语句，更新数据库树形视图
                if query.strip().upper().startswith(("CREATE", "DROP", "ALTER", "RENAME")):
                    self.update_database_tree()
            
            cursor.close()
            
        except Exception as e:
            self.result_text.delete("1.0", tk.END)
            self.result_text.insert("1.0", f"错误：{str(e)}")
            messagebox.showerror("错误", f"查询执行失败：{str(e)}")
        
    def __del__(self):
        if self.connection:
            self.connection.close()

def main():
    root = tk.Tk()
    app = DatabaseQueryGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
