from framework import sheet

def compare_data(new_data:list[dict], original_data:list[dict]) -> list:
    """
    args:
        - new_data (list): updated data
        - original_data (list): original data
    """
    if len(new_data) != len(original_data):
        raise ValueError("Error, different length of data")
    elif new_data == original_data:
        return []
    abnormals = []
    for i in range(len(new_data)):
        new_dict =  new_data[i]
        original_dict = original_data[i]
        for j in range(len(new_dict)):
            if new_dict[(list(new_dict.keys()))[j]] != original_dict[(list(original_dict.keys()))[j]]:
                abnormals.append([i+2, j+1, new_dict[(list(new_dict.keys()))[j]]])
    return abnormals

def update_history(data_type:str, logger:sheet.SheetLogger, new_data:list[list], original_data:list[list]) -> bool:
    """
    args:
        - type (str): type of data -> spendings, income
        - new_data (list): updated data
        - original_data (list): original data
    """
    abnormals = compare_data(new_data, original_data)
    if abnormals == []:
        return False
    if data_type == "spendings":
        logger.update_spenings_sheet(abnormals)
        return True
    elif data_type == "income":
        logger.update_income_sheet(abnormals)
        return True
    else:
        raise KeyError("Invalid type of data, must be spendings or income.")