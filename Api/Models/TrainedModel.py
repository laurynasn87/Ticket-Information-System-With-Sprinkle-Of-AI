
import datetime
import pandas as pd
import gensim
from gensim.models import hdpmodel
class TrainedModels:
    Type: str
    Model = []
    Organization_id: int
    DataFrame ={}
    Corpus= {}
    Coherence: int = 0
    Doc_Topic_Dist = []
    Ai_Model_Type= ""
    Created_On: datetime

    class Model_Types():
        Main_Data_Model = "MainData"
        Full_Data_Model = "FullData"


    def __init__(self, Trained_Model,DataFrame, Type:Model_Types, Corpus, Coherence = 0, Organization_id = 0):
        self.Type= Type
        self.Model = Trained_Model
        self.DataFrame = DataFrame
        self.Coherence = Coherence
        self.Corpus = Corpus
        self.Created_On = datetime.datetime.now()
        self.Organization_id = Organization_id
        self.Ai_Model_Type = self.Get_Model_Type()
        self.Calculate_Dist()

    @staticmethod
    def Get_Model_By_Type(TrainedModels: list,Type:Model_Types,AiModelType,Organization_id = 0):
        selectModel = [model for model in TrainedModels if model.Type == Type and Organization_id == model.Organization_id]

        if (AiModelType =='lda'):
            selectModel = [model for model in selectModel if isinstance(model.Model, gensim.models.LdaModel)]
        elif (AiModelType =='hdp'):
            selectModel = [model for model in selectModel if isinstance(model.Model, hdpmodel.HdpModel)]
        
        if len(selectModel) > 0:
            return selectModel[0]
        else:
            return None

    def Calculate_Dist(self):
        temp_dist = []
        if self.Ai_Model_Type == "lda":
            temp_dist, _ = self.Model.inference(self.Corpus)
        if self.Ai_Model_Type == "hdp":
            temp_dist = self.Model.inference(self.Corpus)
        for idx, arr in enumerate(temp_dist):
            if temp_dist[idx][0] == 0:
                for idy, a in enumerate(temp_dist[idx]):
                    if temp_dist[idx][idy] == 0:
                        temp_dist[idx][idy] = 0.01
        temp_dist /= temp_dist.sum(axis=1)[:, None]
        self.Doc_Topic_Dist = pd.DataFrame(temp_dist)

    def Get_Topic_Count(self):
        count = 0
        if isinstance(self.Model, gensim.models.LdaMulticore) or isinstance(self.Model, gensim.models.LdaModel):
            count = len(self.Model.get_topics())
        if isinstance(self.Model, hdpmodel.HdpModel):
            count = len(self.Model.get_topics())
        
        return count
    def Get_Model_Type(self):
        if isinstance(self.Model, gensim.models.LdaMulticore):
           return "lda"
        if isinstance(self.Model, gensim.models.LdaModel):
           return "lda"
        if isinstance(self.Model, hdpmodel.HdpModel):
            return "hdp"