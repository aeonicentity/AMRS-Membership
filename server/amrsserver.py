#!/usr/bin/env python
from SimpleXMLRPCServer import SimpleXMLRPCServer 
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler # Restrict to a particular path. 
from SQLiteAdapter import SQL
import sqlite3 as lite
import pickle
import time

class RequestHandler(SimpleXMLRPCRequestHandler): 
    rpc_paths = ('/RPC2',) # Create server 
    
    """def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    # Add these headers to all responses
    def end_headers(self):
        self.send_header("Access-Control-Allow-Headers", 
                         "Origin, X-Requested-With, Content-Type, Accept")
        self.send_header("Access-Control-Allow-Origin", "*")
        SimpleXMLRPCRequestHandler.end_headers(self)"""

#this is the live server
#server = SimpleXMLRPCServer(("192.168.1.23", 4321), requestHandler=RequestHandler) 

#local test server
server = SimpleXMLRPCServer(("localhost", 4321), requestHandler = RequestHandler ) 

		
class AMRSSQL(SQL):
	def initializeDB(self):
		memberTableValues = (
							'id',
							'RealName',
							'PersName',
							'Titles',
							'UserLevel',
							'Password',
							'Email',
							'Age',
							'PersonaEra',
							'PracticeHours',
							)
		query = """
				CREATE TABLE IF NOT EXISTS members(
											%s integer PRIMARY KEY AUTOINCREMENT,
											%s varchar(80),
											%s varchar(80),
											%s blob,
											%s tinyint,
											%s varchar(80),
											%s varchar(80),
											%s tinyint,
											%s integer,
											%s float
											);""" % memberTableValues
		self.c.execute(query)
		
		unitTableValues = (
							'id',
							'UnitName',
							'UnitType',
							'Landed',
							'Zips',
							'LeaderId',
							'LordsRepId',
							'CommonRepId',
							'HeraldId',
							'MarshalId',
							'YearEndFunds',
							'YearlyDues',
							)
		query = """
				CREATE TABLE IF NOT EXISTS groups(
											%s integer PRIMARY KEY AUTOINCREMENT,
											%s varchar(160),
											%s varchar(80),
											%s tinyint,
											%s blob,
											%s tinyint,
											%s tinyint,
											%s tinyint,
											%s tinyint,
											%s tinyint,
											%s real,
											%s real
											);""" % unitTableValues
		self.c.execute(query)
		
		certTableValues = (
							'id',
							'name',
							'parent_id',
						)
		
		query = """
				CREATE TABLE IF NOT EXISTS cert(
											%s integer PRIMARY KEY AUTOINCREMENT,
											%s varchar(160),
											%s integer
											);""" % certTableValues
		
		self.c.execute(query)
		
		rel_user__certValues = (
								'id',
								'member_id',
								'cert_id',
		)
		
		query = """
				CREATE TABLE IF NOT EXISTS rel_user__cert(
											%s integer PRIMARY KEY AUTOINCREMENT,
											%s integer,
											%s integer
											);""" % rel_user__certValues
		
		self.c.execute(query)
		
		rel_group__userValues = (
								'id',
								'UnitId',
								'MemberId',
								'isPrimary',
								)
		query = """
				CREATE TABLE IF NOT EXISTS rel_group__user(
											%s integer PRIMARY KEY AUTOINCREMENT,
											%s tinyint,
											%s tinyint,
											%s tinyint
											);""" % rel_group__userValues
		self.c.execute(query)
		
		#p = pickle.dumps(('Knight Marshal'))
		
		#self.update('members',{'RealName':'Admin'},[('id','=','0')] )
		
		#self.delete('groups',[('id','=','3')])
		
		
		"""print "all members"
		for row in self.selectAll('members'):
			print row
			
		print "all groups"
		for row in self.selectAll('groups'):
			print row"""
		
		return
class AMRSRPC:
	###TODO: add the functionality to require password verification to make database queries###
	
	# General functions
	def version(self):
		return "version: 0.1"
	
	# Member Functions
	def searchMemberRealName(self,name):
		return self.sql.search('members',[('RealName','LIKE',name)])
		
	def searchMemberPersName(self,persona):
		return self.sql.search('members',[('PersName','LIKE',persona)])

	def fetchRawMember(self,mid):
		return self.sql.select('members',mid)
		
	def fetchFighterName(self,mid):
		return self.sql.select('members',mid)['PersName']

	def fetchHours (self,mid):
		return self.sql.select('members',mid)['PracticeHours']
		
	def fetchCerts (self,mid):
		ret = []
		res = self.sql.search('rel_user__cert',[('member_id','=',mid)])
		for relId in res:
			ret.append( self.sql.select('cert',relId)['name'] )
		return ret
		
	def fetchTitles (self,mid):
		return pickle.loads( self.sql.select('members',mid)['Titles'] )
		
	def putTitles(self,titles,mid):
		self.sql.update('members',{'Titles':pickle.dumps(titles)},[('id','=',mid)])
		return True
		
	def fetchMemberCard(self,mid):
		res = self.sql.select( 'members', mid )
		
		if res['Titles'] != '':
			res['Titles'] = pickle.loads( str( res['Titles'] ) )
		return res
		
	def deleteMember(self,mid):
		return self.sql.delete('members',[('id','=',mid)])
	
	def updateMemberData(self,mid,data):
		print data
		try:
			if isinstance(data['Titles'],list):
				data['Titles'] = pickle.dumps(data['Titles'])
		except KeyError:
			data['Titles'] = pickle.dumps([])
			
		return self.sql.update('members',data,[('id','=',mid)])
	
	def createMember(self,data,unitIds = None):
		#first I need to pickle the titles if there are any.
		try:
			if data['Titles']:
				data['Titles'] = pickle.dumps(data['Titles'])
		except KeyError:
			data['Titles'] = pickle.dumps([])
		res = self.sql.insert('members',data)
		if unitIds:
			for id in unitIds:
				self.sql.insert('rel_group__user',{'UnitId':id,'MemberId':res,'isPrimary':1})
		if res:
			print "Member Created"
			return res
		else:
			print "Failure"
			return False
			
	def updateHours(self,mid,hours):
		return self.sql.update('members',{'PracticeHours':float(hours)},[('id','=',mid)])		
	
	def fetchAllMemberNames(self):
		res = self.sql.search('members',[('id','!=','-1')])
		ret = []
		for mid in res:
			ret.append(self.fetchFighterName(mid))
		return ret		
	
	# Unit and Group Functions
	def searchUnitName(self,unitName):
		return self.sql.search('groups',[('UnitName','=',unitName)])
	
	def fetchUnit(self,uid):
		res = self.sql.select('groups',uid)
		if(res['Zips'] != ''):
			res['Zips'] = pickle.loads(res['Zips'])	
		return res
	
	def fetchUnitName(self,uid):
		return self.sql.select('groups',uid)['UnitName']
	
	def updateUnit(self,uid,data):
		print data
		if data['Zips']:
			data['Zips'] = pickle.dumps(data['Zips'])
		res = self.sql.update('groups',data,[('id','=',uid)])
		return res
		
	def createUnit(self,data):
		if data['Zips']:
			data['Zips'] = pickle.dumps(data['Zips'])
			

		res = self.sql.insert('groups',data)
		print res
		self.sql.insert('rel_group__user',{'UnitId':res,'MemberId':data['LeaderId'],'isPrimary':0})
		return res
	
	def fetchAllUnitNames(self):
		res = self.sql.search('groups',[('id','!=','-1')])
		ret = []
		for uid in res:
			ret.append(self.fetchUnitName(uid))
		return ret
	
	
	def getPrimaryUnit(self,mid):
		groupid = self.sql.search('rel_group__user',[('MemberId','=',mid),('isPrimary','=','1')])[0]
		unitid = self.sql.select('rel_group__user',groupid)['UnitId']
		return self.sql.select('groups',unitid)['UnitName']
		
	
	def changePrimaryUnit(self,uid,mid):
		self.sql.update('rel_group__user',{'isPrimary':0},[('MemberId','=',mid),('isPrimary','=','1')])
		print "Search Result: "+str(self.sql.search('rel_group__user',[('MemberId','=',mid),('UnitId','=',uid)]))
		if self.sql.search('rel_group__user',[('MemberId','=',mid),('UnitId','=',uid)]):
			print "Member already part of group"
			self.sql.update('rel_group__user',{'isPrimary':1},[('MemberId','=',mid),('UnitId','=',uid)])
		else:
			print "Joining Group"
			self.sql.insert('rel_group__user',{'UnitId':uid,'MemberId':mid,'isPrimary':1})
		return True
	
	def deleteUnit(self,uid):
		self.sql.delete('groups',[('id','=',uid)])
		self.sql.delete('rel_group__user',[('UnitId','=',uid)])
		return True
	
	def fetchAllUserUnits(self,mid):
		groupId = self.sql.search('rel_group__user',[('MemberId','=',mid)])
		allIds = []
		for gid in groupId:
			tempId = self.sql.select('rel_group__user',gid)['UnitId']
			allIds.append(self.sql.select('groups',tempId)['UnitName'])
		if allIds != None:
			return allIds
		return False
		
	# Group/member association functions
	
	def removeUserFromUnit(self,mid,uid):
		# TODO: Eliminate references from groups
		# TODO: if there's only one unit left, make it primary
		return self.sql.delete('rel_group__user',[('UnitId','=',uid),('MemberId','=',mid)]) # Eliminate user from rel_group__user
		
	def insertUserInUnit(self,mid,uid):
		return self.sql.insert('rel_group__user',{'UnitId':uid,'MemberId':mid,'isPrimary':0})
		
	def getMemberNamesInUnit(self,uid):
		try:
			recordIds = self.sql.search('rel_group__user',[('UnitId','=',uid)])
			memberIds = []
			if recordIds != None:
				for rid in recordIds:
					memberIds.append( self.sql.select('rel_group__user',rid)['MemberId'] )
			MemberNames = []
			if memberIds != None:
				for mid in memberIds:
					MemberNames.append(self.sql.select('members',mid)['PersName'])
		except TypeError:
			return []
		return MemberNames
	
	# Certification functions
	
	def getAllCerts(self):
		tmp = self.sql.selectAll('cert')
		ret = []
		for t in tmp:
			ret.append( t )
		print ret
		return ret
		
	def __init__(self):
		self.sql = AMRSSQL()
		return

server.register_instance(AMRSRPC()) # Run the server's main loop 
server.serve_forever()
