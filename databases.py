import os
from pymongo import MongoClient
import json
import config as conf
import aiohttp
import asyncio
import datetime
from uuid import uuid4
import random

# -----------------------------------economy--------------------------------------------

class Database:
    def __init__(self):
        config = conf.Config()
        self.cluster = MongoClient(config.DATABASE_URL)
        self.tenor_key = config.TENOR_KEY
        self.tagCache = []
        self.reactionRoles = []
        
        
        self.info = self.cluster['Info']
        self.economy = self.cluster['Economy']
        
        
        self.inventoryDB = self.economy['Inventory']
        self.currency = self.economy['Currency']
        self.leveling = self.info['leveling']
        self.logs = self.info['logs']
        self.tags = self.info['tags']
        self.roles = self.info['roles']

    def inventory(self, user_id):
        user = self.inventoryDB.find_one({'_id': user_id})
        if user is None:
            user = {'_id': user_id, 'items': {}}
            self.inventoryDB.insert_one(user)
        else:
            pass
        return user

    def check_account(self, user_id):
        user = self.currency.find_one({'_id': user_id})
        if user is None:
            user = {'_id': user_id, 'wallet': 0, 'bank': 0}
            self.currency.insert_one(user)
        else:
            pass
        return user


    def add_in_wallet(self, user_id, amount):
        user = self.check_account(user_id)
        money = int(user['wallet'])
        self.currency.update_one(
            {'_id': user_id}, {'$set': {'wallet': money+int(amount)}})


    def add_in_bank(self, user_id, amount):
        user = self.check_account(user_id)
        money = int(user['bank'])
        self.currency.update_one(
            {'_id': user_id}, {'$set': {'bank': money+int(amount)}})


    def get_item_from_inventory (self, user_id):
        user = self.inventoryDB.find_one({'_id': user_id})
        if user is None:
            user = {'_id': user_id, 'items': {}}
            self.inventoryDB.insert_one(user)
        else:
            pass
        return user


    def add_item(self, user_id, item, amount):
        inventory = self.get_item_from_inventory(user_id)
        items = inventory['items']
        try:
            amounts = items[item]
        except:
            amounts = 0
        amounts += int(amount)
        items[item] = int(amounts)
        self.inventoryDB.update_one(
            {'_id': user_id}, {'$set': {'items': items}})


    def remove_from_wallet(self, user_id, amount):
        user = self.check_account(user_id)
        money = int(user['wallet'])
        self.currency.update_one(
            {'_id': user_id}, {'$set': {'wallet': money-int(amount)}})


    def remove_from_bank(self, user_id, amount):
        user = self.check_account(user_id)
        money = int(user['bank'])
        self.currency.update_one(
            {'_id': user_id}, {'$set': {'bank': money-int(amount)}})


    def remove_item(self, user_id, item, amount):
        inventory = self.get_item_from_inventory (user_id)
        items = inventory['items']
        try:
            amount = items[item]
        except:
            amount = 0
        amount -= int(amount)
        items[item] = int(amount)
        self.inventoryDB.update_one(
            {'_id': user_id}, {'$set': {'items': items}})

    # ---------------------------------------------------------------------Leveling-------------------------------------------------------------------------------


    def get_leveling_info(self, user_id):
        user = self.leveling.find_one({'_id': user_id})
        if user is None:
            user = {'_id': user_id, 'experience': 0, 'level': 1}
            self.leveling.insert_one(user)
        else:
            pass
        return user


    def add_experience(self, user_id, amount):
        user = self.get_leveling_info(user_id)
        experience = user['experience']
        experience += int(amount)
        self.leveling.update_one({'_id': user_id}, {'$set': {'experience': experience}})


    def level_up(self, user_id):
        info = self.get_leveling_info(user_id)
        exp = info['experience']
        lvl=0
        while True:
            if exp < ((50*(lvl**2))+(50*lvl)):
                break
            lvl += 1
        if info['level'] < lvl:
            self.leveling.update_one(
                {'_id': user_id}, {'$set': {'level': lvl}})
            return True
        return False
    
    def get_Top_Ten_Leveling(self):
        users = self.leveling.find().sort('experience', -1).limit(10)
        ranks = []
        for user in users:
            ranks.append(user)
        return ranks
    
    def get_Top_Ten_Richest(self):
        users = self.currency.find().sort('bank', -1).limit(10)
        ranks = []
        for user in users:
            ranks.append(user)
        return ranks
    
    def get_rank(self, user_id, exp):
        users = self.leveling.find().sort('experience', -1)
        rank = 0
        for x in users:
            rank+=1
            if x['_id'] == user_id:
                break
        return rank
    
#-----------------------------------------------------Misc-----------------------------------------------------------------------------------
    
    async def get_Randon_GIF(self, query):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://g.tenor.com/v1/search?q={query}&key={self.tenor_key}&limit=20") as answer:
                # print(answer.text)
                res = await answer.json()
                # print(res)
                res = res['results']
                gif = random.choice(res)['media']
                for i in gif:
                    try:
                        gif = i['gif']['url']
                        return gif
                    except:
                        pass

#-----------------------------------------------------Tagging-----------------------------------------------------------------------------------

    def get_Cache_tags(self):
        return self.tagCache
    
    def add_Tag_in_Cache(self, data):
        self.tagCache.append(data)
        
    
    def get_Tag_by_Author_ID(self, id):
        tags = self.tags.find({'author': id})
        res = []
        for i in tags:
            res.append(i)
        return res
    
    def get_Tag_by_name(self, name):
        tags = self.tags.find({})
        res = []
        for i in tags:
            if name.lower() in i['name'].lower():
                res.append(i)
        return res
    
    def tag_Exist(self, name):
        tags = self.get_Cache_tags()
        for i in tags:
            if i['name'] == name:
                return True
        tags = self.tags.find_one({'name': name})
        if tags is not None:
            self.add_Tag_in_Cache(tags)
            return True
        return False
        
    def add_Tag(self, data):
        self.tags.insert_one(data)
        self.add_Tag_in_Cache(data)
            
    def get_Tag_by_ID(self, id):
        tags = self.get_Cache_tags()
        for i in tags:
            if i['_id'] == id:
                return i
        tags = self.tags.find_one({'_id': id})
        if tags is not None:
            self.add_Tag_in_Cache(tags)
            return tags
        return None

#-----------------------------------------------------Logging-----------------------------------------------------------------------------------
    def log(self, action):
        log = {
            "ID": str(uuid4()),
            "action": action,
            "time": datetime.datetime.now().strftime("%d %B %Y, %I:%M:%S %p")
        }
        self.logs.insert_one(log)
        
    def get_Logs(self):
        logs = []
        log = self.logs.find({})
        for i in log:
            logs.append(i)
        return logs
    
    
    def update_reaction_roles(self):
        all_roles = self.roles.find({})
        roles = []
        for i in all_roles:
            roles.append(i)
        self.reactionRoles = roles
    
    def get_reaction_roles(self):
        print(self.reactionRoles)
        return self.reactionRoles
    
    def add_reaction_role(self, data):
        self.roles.insert_one(data)
        self.update_reaction_roles()
        roles = self.get_reaction_roles()
        self.reactionRoles = roles