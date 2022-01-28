

from tokenize import Name
from numpy import e, number
import config
import firebase_admin
from Models.ConditionModel import ConditionModel
from firebase_admin import credentials, firestore, auth
from firebase_admin import storage
from google.cloud.storage import Blob 

class FireStoreService:
    app = ''
    database = ''
    bucket = ""
    def __init__(self):
        creds = credentials.Certificate(config.Fire_Store_Cred_Path)
        if not firebase_admin._apps:
            self.app = firebase_admin.initialize_app(creds,{
        'storageBucket': 'xxx.appspot.com'
        })
        else:
            self.app =firebase_admin.get_app()
        self.database = firestore.client(app= self.app)
        self.bucket = storage.bucket()

    def GetData(self,Collection_Name: str):
        return self.database.collection(Collection_Name).stream()
    
    def GetDataByDocumentId(self,Collection_Name: str,Document_Name: str):
        return self.database.collection(Collection_Name).document(Document_Name).get()
    
    def GetDataWithConditions(self,Collection_Name: str, Conditions: list):
        results_ref = self.database.collection(Collection_Name)
        condition: ConditionModel.ConditionModel
        for condition in Conditions:
            results_ref = results_ref.where(condition.name, condition.operator, condition.value)

        return results_ref.stream();

    def Add_Document(self,Data:list,Collection_Name:str,Document_Name:str = '', mergeInsert = False):
       data_ref = self.database.collection(Collection_Name)
       if Document_Name != '':
           data_ref.document(Document_Name).set(Data, merge= mergeInsert)
       else:
           data_ref.add(Data)
    
    def Delete_Document(self,Collection_Name,Document_Name):
        self.database.collection(Collection_Name).document(Document_Name).delete()
        
    def Batch_Add_Document(self,Data:list,Collection_Name:str, DocumentField=""):
        batch = self.database.batch()
        data_ref = self.database.collection(Collection_Name)
        for idx, dataset in enumerate(Data):
            if DocumentField != '':
                temp_data_ref = data_ref.document(str(dataset[DocumentField]))
                batch.set(temp_data_ref,dataset)
            else:
                batch.add(data_ref, dataset)
            if (idx == 399):
                batch.commit()
                batch = self.database.batch()

        batch.commit()

    def Get_Users(self):
        users = auth.list_users(max_results=1000).users
        results = [user._data for user in users]
        return results

    def Create_User(self, email,password,displayName,role ='user',organization=0,userId=0):
        try:
            new_usr = auth.create_user(
                email=email,
                email_verified=False,
                password=password,
                disabled=False)

            if isinstance(organization,str):
                organization=number(organization)
            if organization == None:
                organization=0
            if new_usr != {}:
                self.Add_Document({'role':role,'displayName':displayName, 'uid': new_usr.uid,"userId":userId,"organization":organization},'users',new_usr.uid,True)
            return True,""
        except Exception as e:
            return False, e.default_message

    def Update_User(self,uid,dispalyName,role,userId=0, org=0):
        try:
            if isinstance(org,str):
                org = number(org)
            self.Add_Document({'role':role,'displayName':dispalyName,"userId":userId,"organization":org},'users',uid,True)
            return True
        except Exception as e:
            return False

    def Delete_User(self, uid):
        try:
            auth.delete_user(uid)
            self.Delete_Document("users",uid)
            return True
        except:
            return False

    def Set_User_Disable(self, uid, Value = True):
        try:
            auth.update_user(uid, disabled = Value)
            return True
        except:
            return False
    
    def Verify_Token(self,token):
        try:
            decoded_token = auth.verify_id_token(token)
            if "uid" in decoded_token:
                return decoded_token
        except:
            return None
        finally:
            return None
    
    def UploadFile(self, Name):
        blob = self.bucket.blob(Name)
        blob.upload_from_filename(Name)

    def DownloadFile(self,Name, SavePath=""):
        SavePath = Name
        if isinstance(self.bucket.get_blob(Name), Blob):
            blob = self.bucket.get_blob(Name)
            blob.download_to_filename(SavePath)
