class Systemsettings:
    Id: int
    Name: str
    Value: str

    @staticmethod
    def from_dict(my_dict):
        new_stg:Systemsettings = Systemsettings()
        for key in my_dict:
            if key == 'Id':
                new_stg.Id=my_dict[key]
            if key == 'Name':
                new_stg.Name=my_dict[key]
            if key == 'Value':
                new_stg.Value = my_dict[key]
        return new_stg