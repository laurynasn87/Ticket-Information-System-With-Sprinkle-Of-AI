from copy import deepcopy
import datetime
import os
import re
from multiprocessing import freeze_support
from os.path import exists
import config
import numpy as np
from Services import ConfigService
import gensim
import gensim.corpora as corpora
import pandas as pd
male_Names = np.loadtxt("data/nltk/male.txt", dtype=str, usecols=0)
female_Names = np.loadtxt("data/nltk/female.txt", dtype=str, usecols=0)
stopwords = np.loadtxt("data/nltk/english.txt", dtype=str, usecols=0)
from gensim.utils import simple_preprocess
from nltk.stem import WordNetLemmatizer
from scipy.spatial.distance import jensenshannon
import Models.TrainedModel as TrainedModel
from gensim.models import CoherenceModel, HdpModel
class TicketComparisonAi:
    Config_service:ConfigService
    Organizations=[]
    TicketData= []
    Ticket_Models= []
    Users = []
    SavedResults = []
    Stop_Words = []
    firebase = {}
    init_in_progress = True

    def __init__(self, TicketList,Config_Service:ConfigService,Organizations = [],Users = [], firebase={}):
        self.init_in_progress = True
        self.Ticket_Models = []
        self.Organizations=Organizations
        self.Config_service = Config_Service
        self.Users = Users
        self.Config_service.Get_All_Settings()
        self.firebase = firebase
        self.innit_StopWords()
        self.Initate_model_creation(TicketList, UseOlder=True)
        self.All_Organization_Models_Creation(TicketList)
        if config.GoogleCloud:
            self.SaveData()
        self.init_in_progress = False

    #Filling bespoke stop words 
    def innit_StopWords(self):
        self.Stop_Words = list(stopwords)
        self.Stop_Words = self.Stop_Words + list(male_Names) + list(female_Names)
        self.Stop_Words = self.Stop_Words + ['from', 'subject', 're', 'edu', 'use'] + [usr.name for usr in self.Users]
        self.Stop_Words = self.Stop_Words + [usr.name.split()[0] for usr in self.Users if len(usr.name.split())>1] + [usr.name.split()[1] for usr in self.Users if len(usr.name.split())>1]
        self.Stop_Words = np.array(self.Stop_Words, dtype=str)

    def Initate_model_creation(self, Tickets, Organization_id =0, UseOlder = False):
        if Organization_id == 0:
            self.TicketData = Tickets

        Tickets_MainData = []
        Tickets_FullData = []

        if len(Tickets) == 0:
            return
        for ticket in Tickets:
            Tickets_MainData.append({"id":ticket.id, "data": ticket.subject + " " + ticket.description.replace("\r",'').replace("\n",'')})
            FullData =  ticket.subject + " " + ticket.description.replace("\r",'').replace("\n",'') + " " + "\n".join(comm.plain_body for comm in ticket.comments if comm.public == True).replace("\r",'').replace("\n",'')
            Tickets_FullData.append({"id": ticket.id, "data": FullData})

        Main_data_dataframe = self.Create_Dataframe(Tickets_MainData)
        Main_Data_Model,Main_Data_Model_Corpus,Coh = self.Generate_Model(Main_data_dataframe, Organization_id,"Main_Data_Model",UseOlder)
        Existing = TrainedModel.TrainedModels.Get_Model_By_Type(self.Ticket_Models,TrainedModel.TrainedModels.Model_Types.Main_Data_Model,self.Config_service.Get_Setting_By_Name("mode",True),Organization_id)
        if Existing:
            self.Ticket_Models.remove(Existing)
            resultExisting = [saved for saved in self.SavedResults if saved["model"]==Existing]
            if len(resultExisting)>0:
                for result in resultExisting:
                    self.SavedResults.remove(result)
        if Main_Data_Model != None:
         self.Ticket_Models.append(TrainedModel.TrainedModels(Main_Data_Model,Main_data_dataframe,TrainedModel.TrainedModels.Model_Types.Main_Data_Model,Main_Data_Model_Corpus,Coh,Organization_id))
        
        if Organization_id == 0:
            Full_data_dataframe = self.Create_Dataframe(Tickets_FullData)
            Full_Data_Model,Full_Data_Model_Corpus,Coh = self.Generate_Model(Full_data_dataframe,Organization_id,"Full_Data_Model",UseOlder)
            Existing = TrainedModel.TrainedModels.Get_Model_By_Type(self.Ticket_Models,TrainedModel.TrainedModels.Model_Types.Full_Data_Model,self.Config_service.Get_Setting_By_Name("mode",True),Organization_id)
            if Existing:
                self.Ticket_Models.remove(Existing)
                resultExisting = [saved for saved in self.SavedResults if saved["model"]==Existing]
                if len(resultExisting)>0:
                    for result in resultExisting:
                        self.SavedResults.remove(result)
            if Full_Data_Model != None:
                self.Ticket_Models.append(TrainedModel.TrainedModels(Full_Data_Model,Full_data_dataframe,TrainedModel.TrainedModels.Model_Types.Full_Data_Model,Full_Data_Model_Corpus,Coh,Organization_id))
    
    def All_Organization_Models_Creation(self,Tickets):
        Organizations = [ticket.organization_id for ticket in Tickets]
        Organizations = list(set(Organizations))
        for org_id in Organizations:
            All_org_tickets = [ticket for ticket in Tickets if ticket.organization_id == org_id]
            if len(All_org_tickets)>0:
                self.Initate_model_creation(All_org_tickets,org_id,UseOlder=True)
    

    def Initiate_model_creation_Organization(self,Ticket_Id, All_Tickets):
        Ticket = [Ticket for Ticket in self.TicketData if Ticket.id == Ticket_Id]
        if len(Ticket) > 0:
            Ticket = Ticket[0]
            self.Initate_model_creation([ticket for ticket in All_Tickets if ticket.organization_id == Ticket.organization_id],Ticket.organization_id)

    def Create_Dataframe(self,Tickets):

        for ticket in Tickets:
            ticket['data'] = re.sub('[,\.!?]', '', ticket['data'])
            ticket['data'] = ticket['data'].lower()

        # create dataframe
        dataframe = pd.DataFrame(Tickets, columns=["id","data"])

        return dataframe
        
    #divide string array to word arrays
    def sent_to_words(self,sentences):
        for sentence in sentences:
            # deacc=True removes punctuations
            yield (gensim.utils.simple_preprocess(str(sentence), deacc=True))

    def remove_stopwords(self,texts, stop_words):
        return [[word for word in simple_preprocess(str(doc))
                 if word not in stop_words and len(word) > 2] for doc in texts]

    def lemmatization(self,word_List):
        lemmatizer = WordNetLemmatizer()
        results = []
        for doc in word_List:
            row = []
            for word in simple_preprocess(str(doc)):
                try:
                    row.append(lemmatizer.lemmatize(word))
                except:
                    row.append(word)
            results.append(row)

        return results


    def Generate_Model(self, dataframe, organization_id = 0,Saved_Name="", Use_Saved= False):
        model = {}
        corpus = []
        coherence= 0
        topic_count = self.Config_service.Get_Setting_By_Name("Topics_Count",True)
        mode = self.Config_service.Get_Setting_By_Name("mode", True)

        if Use_Saved:
            model,coherence,corpus = self.Load_Models(mode,Saved_Name,organization_id,topic_count)
            if len(corpus) != len(dataframe):
                return self.Generate_Model(dataframe,organization_id,Saved_Name)
            
        else:

            data_words = list(self.sent_to_words(deepcopy(dataframe.data.to_numpy())))

            data_words = self.remove_stopwords(data_words,  self.Stop_Words)

            data_words = self.lemmatization(data_words)
            
            id2word = corpora.Dictionary(data_words)

            corpus = np.array([id2word.doc2bow(text) for text in data_words], dtype=object)

            if mode == 'lda':
                model = gensim.models.LdaModel(corpus=corpus.tolist(),
                                                   id2word=id2word,
                                                   passes=3,
                                                   num_topics=topic_count,
                                                   distributed=False,
                                                   random_state=1997)

                
            
            if mode == 'hdp':
                model = HdpModel(corpus=corpus.tolist(), id2word=id2word, random_state=1997)
                model.print_topics()
            
            coherence = 0
            existing =TrainedModel.TrainedModels.Get_Model_By_Type(self.Ticket_Models,Saved_Name,mode,organization_id)
            if (existing == None or topic_count != existing.Get_Topic_Count()):
                coherence_model = CoherenceModel(model=model, texts=data_words, dictionary=id2word, coherence='c_v')
                coherence = coherence_model.get_coherence()
            else:
                coherence = existing.Coherence

            if config.Save_Models:
                self.Save_Model(mode,model,corpus,Saved_Name,coherence,organization_id,topic_count)

        if (Use_Saved):
            print("Loaded Model with a name " + Saved_Name + " for organization id " + str(organization_id))
        else:
            print("Created Model with a name " + Saved_Name + " for organization id " + str(organization_id))

        return model, corpus, coherence


    def Load_Models(self,mode,Saved_Name,org_id = 0,topic_count=0):
        if not os.path.exists("/tmp"):
            os.makedirs("/tmp")
            print("Creating tmp")
        model = {}
        coherence = 0
        Corpus = {}
        name = mode
        if org_id != 0:
            name= name + "_" + str(org_id)
        if Saved_Name != "":
            name= name + "_" + Saved_Name
        
        name = "/tmp/" +name
        if (mode=="lda"):
            try:
                if topic_count != 0:
                    name = name + str(topic_count)
                if self.firebase != {}:
                    self.firebase.DownloadFile(name+".txt")
                    self.firebase.DownloadFile(name)
                    self.firebase.DownloadFile(name + ".id2word")
                    self.firebase.DownloadFile(name + ".state")
                    self.firebase.DownloadFile(name+".expElogbeta.npy")
                model = gensim.models.LdaModel.load(name)
            except:
                model = {}
        if (mode=="hdp"):
            try:
                model = HdpModel.load(name)
                Corpus = model.corpus
            except:
                model = {}

        if self.firebase != {}:
            self.firebase.DownloadFile(name + ".txt")
        if exists(name + ".txt"):                                                                                                                            
            f = open(name + ".txt", "r")
            coherence = f.read()
            f.close()
            coherence = float(coherence)
        if self.firebase != {}: 
            self.firebase.DownloadFile(name+"_Corpus.npy")
        if exists(name + "_Corpus.npy"):
          Corpus = np.load(name + "_Corpus.npy",allow_pickle=True)
          os.remove(name+"_Corpus.npy")

        if exists(name+".txt"):
            os.remove(name+".txt")
        if exists(name+".expElogbeta.npy"):
            os.remove(name+".expElogbeta.npy")
        if exists(name):
            os.remove(name)
        if exists(name+".id2word"):
            os.remove(name+".id2word")
        if exists(name+".state"):
            os.remove(name+".state")
            
        return model,coherence,Corpus
        
    def Save_Model(self,mode,model,Corpus,Saved_Name,Coherence,org_id = 0,topic_count=0):
        if not os.path.exists("/tmp"):
            os.makedirs("/tmp")
        name = "/tmp/" + mode
        if org_id != 0:
            name= name + "_" + str(org_id)
        if Saved_Name != "":
            name= name + "_" + Saved_Name

        if (mode=="lda"):
            if topic_count != 0:
                name = name + str(topic_count)
            gensim.models.LdaModel.save(model,name)
            np.save(name + "_Corpus.npy", Corpus)

        if (mode=="hdp"):
            HdpModel.save(model,name)

        file = open(name+".txt", "w") 
        file.write(str(Coherence)) 
        file.close() 

        self.firebase.UploadFile(name+".txt")
        if (mode!="hdp"):
            self.firebase.UploadFile(name+"_Corpus.npy")
            self.firebase.UploadFile(name+".expElogbeta.npy")
            self.firebase.UploadFile(name+".id2word")
            self.firebase.UploadFile(name+".state")
        self.firebase.UploadFile(name)
        os.remove(name+".txt")
        if (mode!="hdp"):
            os.remove(name+"_Corpus.npy")
            os.remove(name+".expElogbeta.npy")
            os.remove(name+".id2word")
            os.remove(name+".state")
        os.remove(name)

    def recommendation(self,doc_topic_dist, df, idx, k=1):
        '''
        Returns the title of the k papers that are closest (topic-wise) to the paper given by paper_id.
        '''
        index = df.index[df['id'] == idx].tolist()
        if len(index)<1:
            print("Ticket " + str(idx) + "was not found in corpus")
            return
        else:
            index=index[0]
        recommended, dist = self.get_k_nearest_docs(doc_topic_dist, doc_topic_dist.iloc[index], k, get_dist=True)

        recommended = df.iloc[recommended].copy()
        recommended["similarity"] = 1 - dist

        output = []

        for i, s in recommended[['id', 'similarity']].values:
            output.append({"id": i,
                           "similarity": round(s * 100)})

        return output

    def Is_Model_Outdated(self,Model_Type:TrainedModel.TrainedModels.Model_Types = TrainedModel.TrainedModels.Model_Types.Main_Data_Model, org_id = 0):
        if config.GoogleCloud:
            self.LoadData()
        if  self.init_in_progress == True:
            return False
        date1 = datetime.datetime.now()
        date2 = 0
        mode = self.Config_service.Get_Setting_By_Name("mode",True)
        if len(self.Ticket_Models) < 1:
            return True
        else:
            if org_id == 0:
                model = TrainedModel.TrainedModels.Get_Model_By_Type(self.Ticket_Models,Model_Type,mode)
            else:
                model = TrainedModel.TrainedModels.Get_Model_By_Type(self.Ticket_Models,Model_Type ,mode,org_id)
            
            if model is None:
                return True
            else:
                date2 = model.Created_On
        

        diff = date1 - date2

        seconds = diff.seconds
        hours = seconds / 3600

        time_limit = self.Config_service.Get_Setting_By_Name("Model_Update_Every_n_Hours",True)
        if time_limit != None and hours == time_limit or hours > time_limit:
            return True
        else:
            return False

    def Is_Ticket_Organization_Model_Outdated(self,ticket_id, Tickets):
        ticket = next((ticket for ticket in Tickets if ticket.id == ticket_id),{})
        return self.Is_Model_Outdated(org_id = getattr(ticket,"organization_id",0))
        
    def Find_Most_Similar_Ticket(self, id: int, Model_Type:TrainedModel.TrainedModels.Model_Types, By_Org = False):
        if  self.init_in_progress == True:
            return []
        MainTicket =  next((ticket for ticket in self.TicketData if ticket.id == id),{})
        if MainTicket == {}:
            return []

        if By_Org:
            selected_Model = TrainedModel.TrainedModels.Get_Model_By_Type(self.Ticket_Models,Model_Type,self.Config_service.Get_Setting_By_Name("mode",True),MainTicket.organization_id)
        else:
            selected_Model = TrainedModel.TrainedModels.Get_Model_By_Type(self.Ticket_Models, Model_Type,self.Config_service.Get_Setting_By_Name("mode",True))
        results = []

        savedResults = next((result for result in self.SavedResults if selected_Model == result["model"] and result["Ticket"] == MainTicket.id),{})
        if savedResults != {} and False:
            return savedResults["results"]
        else:

            if MainTicket != {} and  selected_Model:
                if not isinstance(selected_Model.Doc_Topic_Dist, pd.DataFrame):
                    selected_Model.Calculate_Dist()

                results = self.recommendation(selected_Model.Doc_Topic_Dist,selected_Model.DataFrame,id,self.Config_service.Get_Setting_By_Name("AI_TICKET_COUNT",True))

            if (results and len(results) > 0):
                if results[0]["id"] == id:
                    results.pop(0)

                org_info = {}
                if By_Org:
                    org_info = next((org for org in self.Organizations if org.id == MainTicket.organization_id),{})

                for item in results:
                    ticket = next((ticket for ticket in self.TicketData if ticket.id == item["id"]),{})
                    if ticket != {}:
                        if By_Org:
                            item["organization"] = org_info
                        item["subject"] = ticket.subject

                self.SavedResults.append({"model": selected_Model,"results":results,"Ticket":MainTicket.id})

        return results

    def Add_New_Ticket(self,Ticket_Map):
        if (Ticket_Map!= {}):
            topic_count = self.Config_service.Get_Setting_By_Name("Topics_Count",True)
            mode = self.Config_service.Get_Setting_By_Name("mode", True)
            ModelsToUpdate = []
            ModelsToUpdate.append(TrainedModel.TrainedModels.Get_Model_By_Type(self.Ticket_Models,TrainedModel.TrainedModels.Model_Types.Full_Data_Model,self.Config_service.Get_Setting_By_Name("mode",True)))
            ModelsToUpdate.append(TrainedModel.TrainedModels.Get_Model_By_Type(self.Ticket_Models,TrainedModel.TrainedModels.Model_Types.Main_Data_Model,self.Config_service.Get_Setting_By_Name("mode",True)))
            ModelsToUpdate.append(TrainedModel.TrainedModels.Get_Model_By_Type(self.Ticket_Models,TrainedModel.TrainedModels.Model_Types.Main_Data_Model,self.Config_service.Get_Setting_By_Name("mode",True),Ticket_Map["Ticket"].organization_id))
            print("Starting new ticket addition to AI models process")
            for model in ModelsToUpdate:
                modelName = ""
                if model == None:
                    continue
                corpus = model.Corpus
                dataframe = model.DataFrame
                data = ""
                if model.Type == TrainedModel.TrainedModels.Model_Types.Main_Data_Model:
                    data = Ticket_Map["Ticket"].subject + " " + Ticket_Map["Ticket"].description.replace("\r",'').replace("\n",'')
                    modelName = "Main_Data_Model"
                    print("Retraining Main_Data_Model for org " + str(model.Organization_id))
                if model.Type == TrainedModel.TrainedModels.Model_Types.Full_Data_Model:
                    data =  Ticket_Map["Ticket"].subject + " " + Ticket_Map["Ticket"].description.replace("\r",'').replace("\n",'') + " " + "\n".join(comm.plain_body for comm in Ticket_Map["Ticket"].comments if comm.public == True).replace("\r",'').replace("\n",'')
                    print("Retraining Full_Data_Model for org " + str(model.Organization_id))
                    modelName = "Full_Data_Model"
                data = re.sub('[,\.!?]', '', data)
                data = data.lower()
                data = {"id":Ticket_Map["Ticket"].id, "data": data}
                dataframe = dataframe.append(data,ignore_index=True)
                new_data = []
                new_data.append(dataframe.loc[len(dataframe) - 1].data)
                data_words = list(self.sent_to_words(new_data))

                data_words = self.remove_stopwords(data_words,  self.Stop_Words)

                data_words = self.lemmatization(data_words)
                if not isinstance(corpus,list):
                    corpus = corpus.tolist()
                    corpus.append([model.Model.id2word.doc2bow(text) for text in data_words][0])
                    corpus = np.array(corpus, dtype=object)
                else:
                    corpus.append([model.Model.id2word.doc2bow(text) for text in data_words][0])

                print("Generating model ")   
                if mode == 'lda':
                    newmodel = gensim.models.LdaModel(corpus=corpus.tolist(),
                                                   id2word=model.Model.id2word,
                                                   passes=3,
                                                   num_topics=topic_count,
                                                   distributed=False,
                                                   random_state=1997)

                if mode == 'hdp':
                    newmodel = HdpModel(corpus=corpus.tolist(), id2word=model.Model.id2word, random_state=1997)

                print("Generated ")  
                model.Model = newmodel
                model.Corpus = corpus
                model.DataFrame = dataframe
                model.Doc_Topic_Dist = []
                try:
                    self.Save_Model(mode,newmodel,corpus,modelName, model.Coherence,model.Organization_id,topic_count)
                except:
                    print("Error while saving")
                print("New ticket added to model for org " + str(model.Organization_id))

            if config.GoogleCloud == True:
                self.SaveData()
                
        

    def get_k_nearest_docs(self,doc_topic_dist, doc_dist, k=5, get_dist=False):
        '''
        doc_dist: topic distribution (sums to 1) of one article

        Returns the index of the k nearest articles (as by Jensen–Shannon divergence in topic space).
        '''
        distances = doc_topic_dist.apply(lambda x: jensenshannon(x, doc_dist), axis=1)
        k_nearest = distances[distances != 0].nsmallest(n=k).index

        if get_dist:
            k_distances = distances[distances != 0].nsmallest(n=k)
            return k_nearest, k_distances
        else:
            return k_nearest

    def Find_Best_Asignee(self,Full_List,User_List):
        UserList = []
        if None != Full_List: 
            for Result_ticket in Full_List:
                Full_Ticket_Info = next((ticket for ticket in self.TicketData if ticket.id == Result_ticket["id"]), [])
                if Full_Ticket_Info != []:
                    User = next((user for user in User_List if user.id == Full_Ticket_Info.assignee_id),[])
                    if User != []:
                        Existing_User = next((user for user in UserList if user["id"] == User.id),[])
                        if Existing_User != []:
                            index = UserList.index(Existing_User)
                            UserList[index]["similarity"] = UserList[index]["similarity"] + Result_ticket["similarity"]
                        else:
                            UserList.append({'id':User.id,'similarity':Result_ticket["similarity"],'user':User.name})

        return sorted(UserList,reverse=True, key=lambda user: user["similarity"])

    def SaveData(self):
        np.save("/tmp/Ai.npy",self.Ticket_Models)
        print("Saved ai data")

    def LoadData(self):
        if os.path.exists("/tmp/Ai.npy"):
            self.Ticket_Models = np.load("/tmp/Ai.npy", allow_pickle=True).tolist()
            print("Loaded ai data")
        
    

