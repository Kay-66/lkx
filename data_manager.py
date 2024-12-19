import json
import os
from datetime import datetime

class DataManager:
    def __init__(self):
        self.data_dir = "data"
        self.components_file = os.path.join(self.data_dir, "components.json")
        self.ensure_data_directory()
        
    def ensure_data_directory(self):
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            
    def get_file_path(self, date):
        date_str = date.strftime("%Y%m%d")
        return os.path.join(self.data_dir, f"{date_str}.json")
        
    def save_record(self, date, record_data):
        file_path = self.get_file_path(date)
        
        existing_data = []
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
                
        record_data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        existing_data.append(record_data)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)
            
    def load_records(self, date):
        file_path = self.get_file_path(date)
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
        
    def get_all_dates(self):
        dates = []
        for filename in os.listdir(self.data_dir):
            if filename.endswith('.json'):
                date_str = filename[:-5]
                try:
                    date = datetime.strptime(date_str, "%Y%m%d")
                    dates.append(date)
                except ValueError:
                    continue
        return sorted(dates)
        
    def save_components(self, components_data):
        """保存组件信息到文件"""
        with open(self.components_file, 'w', encoding='utf-8') as f:
            json.dump(components_data, f, ensure_ascii=False, indent=2)
            
    def load_components(self):
        """从文件加载组件信息"""
        if os.path.exists(self.components_file):
            with open(self.components_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
