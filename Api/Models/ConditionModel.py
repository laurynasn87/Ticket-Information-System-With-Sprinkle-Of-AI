class ConditionModel:
    name=''
    operator=''
    value=''
    def __init__(self,name:str,operator:str,value:str):
        self.name=name
        self.operator=operator
        self.value=value