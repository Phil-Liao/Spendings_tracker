import json
from datetime import datetime

class MasterLogger:
    def __init__(self, log_file_path="logs/log.json"):
        self.log_file_path = log_file_path

    def fetch_logs(self) -> dict:
        with open(self.log_file_path, "r") as file:
            return json.load(file)

    def log_info(self, text: str) -> None:
        logs_data = self.fetch_logs()
        logs = logs_data["logs"]
        dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        log_entry = (text, dt_string)
        logs.append(log_entry)
        logs_data["logs"] = logs
        with open(self.log_file_path, "w") as file:
            json.dump(logs_data, file, indent=4)
    def clear_log(self) -> bool:
        logs = []
        with open(self.log_file_path, "w") as file:
            json.dump({"logs":logs}, file, indent=4)
        return True

