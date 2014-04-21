#!/usr/bin/env python
import Tkinter as Tk
import xmlrpclib
import string

#s = xmlrpclib.ServerProxy("http://192.168.1.23:4321/RPC2")
s = xmlrpclib.ServerProxy("http://localhost:4321/RPC2")
print s.version()

FONT = ("Helvetica",10)

tkinter_umlauts=['odiaeresis', 'adiaeresis', 'udiaeresis', 'Odiaeresis', 'Adiaeresis', 'Udiaeresis', 'ssharp']

class AutocompleteEntry(Tk.Entry):
        """
        Subclass of Tkinter.Entry that features autocompletion.
        
        To enable autocompletion use set_completion_list(list) to define 
        a list of possible strings to hit.
        To cycle through hits use down and up arrow keys.
        """
        def set_completion_list(self, completion_list):
                self._completion_list = completion_list
                self._hits = []
                self._hit_index = 0
                self.position = 0
                self.bind('<KeyRelease>', self.handle_keyrelease)               

        def autocomplete(self, delta=0):
                """autocomplete the Entry, delta may be 0/1/-1 to cycle through possible hits"""
                if delta: # need to delete selection otherwise we would fix the current position
                        self.delete(self.position, Tk.END)
                else: # set position to end so selection starts where textentry ended
                        self.position = len(self.get())
                # collect hits
                _hits = []
                for element in self._completion_list:
                        #if element.startswith(self.get().lower()): Changed this for great justice
                        if element.lower().startswith(self.get().lower()):
                                _hits.append(element)
                # if we have a new hit list, keep this in mind
                if _hits != self._hits:
                        self._hit_index = 0
                        self._hits=_hits
                # only allow cycling if we are in a known hit list
                if _hits == self._hits and self._hits:
                        self._hit_index = (self._hit_index + delta) % len(self._hits)
                # now finally perform the auto completion
                if self._hits:
                        self.delete(0,Tk.END)
                        self.insert(0,self._hits[self._hit_index])
                        self.select_range(self.position,Tk.END)
                        
        def handle_keyrelease(self, event):
                """event handler for the keyrelease event on this widget"""
                if event.keysym == "BackSpace":
                        self.delete(self.index(Tk.INSERT), Tk.END) 
                        self.position = self.index(Tk.END)
                if event.keysym == "Left":
                        if self.position < self.index(Tk.END): # delete the selection
                                self.delete(self.position, Tk.END)
                        else:
                                self.position = self.position-1 # delete one character
                                self.delete(self.position, Tk.END)
                if event.keysym == "Right":
                        self.position = self.index(Tk.END) # go to end (no selection)
                if event.keysym == "Down":
                        self.autocomplete(1) # cycle to next hit
                if event.keysym == "Up":
                        self.autocomplete(-1) # cycle to previous hit
                # perform normal autocomplete if event is a single key or an umlaut
                if len(event.keysym) == 1 or event.keysym in tkinter_umlauts:
                        self.autocomplete()

class ScrolledListbox(Tk.Listbox):
	def destroy(self):
		self.pack_forget()
		
	def __init__(self, master, **key):
		self.frame = Tk.Frame(master)
		self.yscroll = Tk.Scrollbar (self.frame, orient=Tk.VERTICAL)
		self.yscroll.pack(side=Tk.RIGHT, fill=Tk.BOTH)
		key['yscrollcommand']=self.yscroll.set
		Tk.Listbox.__init__(self, self.frame, **key)
		self.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=1)
		self.yscroll.config(command=self.yview)

		# Copy geometry methods of self.frame -- hack!
		for m in (Tk.Pack.__dict__.keys() + Tk.Grid.__dict__.keys() + Tk.Place.__dict__.keys()):
			m[0] == '_' or m == 'config' or m == 'configure' or setattr(self, m, getattr(self.frame, m))
			

class AMRSClientGUI(Tk.Frame):
	def switchMembers(self):
		self.dumpScreen()
		self.memberScreen()
	
	def switchUnits(self):
		self.dumpScreen()
		self.unitScreen()
	
	def switchAward(self):
		self.dumpScreen()
		self.awardsScreen()
		
	def switchUnitMembership(self):
		self.dumpScreen()
		self.unitMembershipScreen()
		
	def switchAwardManage(self):
		self.dumpScreen()
		pass
		
	def switchPractice(self):
		self.dumpScreen()
		self.fighterScreen()
		pass



################################## Member Screen ##################################




	def loadMember(self,e):
		if self.curMid == None:
			i = self.packItm['memberBox'].index(Tk.ACTIVE)
			self.curMid = s.searchMemberPersName(self.members[i])[0]
			memberData = s.fetchMemberCard(self.curMid)
			self.packItm['field_RealName'].insert(0,memberData['RealName'])
			self.packItm['field_PersName'].insert(0,memberData['PersName'])
			self.packItm['label_Titles'].config(text = string.join(memberData['Titles'],", "))
			self.packItm['field_Email'].insert(0,memberData['Email'])
			primeUnit = s.getPrimaryUnit(self.curMid)
			if primeUnit in self.unitOptions:
				self.field_UnitVal.set(primeUnit)
			self.packItm['label_AllUnits'].config(text= string.join(s.fetchAllUserUnits(self.curMid),", " ) )
		else:
			self.clearMember()
			self.loadMember(e)
	
	def updateMember(self):
		
		newData = {
				'RealName':self.packItm['field_RealName'].get(),
				'PersName':self.packItm['field_PersName'].get(),
				'Email':self.packItm['field_Email'].get(),
				}
		unitName = self.field_UnitVal.get()
		UnitId = s.searchUnitName(unitName)[0]
		self.packItm['field_RealName'].delete(0,Tk.END)
		self.packItm['field_PersName'].delete(0,Tk.END)
		self.packItm['label_Titles'].config(text = "")
		self.packItm['field_Email'].delete(0,Tk.END)	
		if self.curMid:
			s.updateMemberData(self.curMid,newData)
			s.changePrimaryUnit(UnitId,self.curMid)
		else:
			if newData['RealName'] != '' and newData['PersName'] != '':
				s.createMember(newData,[UnitId])
				print "create new Member"
		
		self.clearMember()
		self.updateMemberList()
		return
	
	def deleteMember(self):
		if self.curMid:
			s.deleteMember(self.curMid)
		self.clearMember()
		self.updateMemberList()
		
	
	def clearMember(self):
		self.packItm['field_RealName'].delete(0,Tk.END)
		self.packItm['field_PersName'].delete(0,Tk.END)
		self.packItm['label_Titles'].config(text = "")
		self.field_UnitVal.set("Select Unit")
		self.packItm['label_AllUnits'].config(text = "All Units")
		self.packItm['field_Email'].delete(0,Tk.END)	
		self.curMid = None
	
	def updateMemberList(self):
		self.members = s.fetchAllMemberNames()
		self.packItm['memberBox'].delete(0,Tk.END)
		self.packItm['memberBox'].insert(Tk.END, *self.members)
	
	def dumpScreen(self):
		self.curMid = None;
		self.curUid = None;
		for k,v in self.packItm.iteritems():
			v.destroy()
	
	def memberScreen(self):
		# Unit Column
	 	self.packItm['memberCol'] = Tk.Label(self)
	 	self.packItm['memberCol'].pack(side=Tk.LEFT)
	 	
		# Member Box
		self.packItm['memberBox'] = ScrolledListbox(self)
		self.updateMemberList()
		
		#if not self.packItm['memberBox']:
		self.packItm['memberBox'].pack(in_=self.packItm['memberCol'])
		self.packItm['memberBox'].bind("<Double-Button-1>",self.loadMember)
		
		self.packItm['rightCol'] = Tk.Label(self)
		self.packItm['rightCol'].pack(side=Tk.RIGHT)
		self.packItm['labelCol'] = Tk.Label(self)
		self.packItm['labelCol'].pack(in_=self.packItm['rightCol'],
		side=Tk.LEFT)
		
		
		# Real Name
		self.packItm['label_RealName'] = Tk.Label(self, text="Real Name:", font=FONT)
		self.packItm['label_RealName'].pack(in_=self.packItm['labelCol'])
		
		self.packItm['field_RealName'] = Tk.Entry(self)
		self.packItm['field_RealName'].pack(in_=self.packItm['rightCol'])
		
		# Persona Name
		self.packItm['label_PersName'] = Tk.Label(self, text="Persona Name:", font=FONT)
		self.packItm['label_PersName'].pack(in_=self.packItm['labelCol'])
		
		self.packItm['field_PersName'] = Tk.Entry(self)
		self.packItm['field_PersName'].pack(in_=self.packItm['rightCol'])
		
		# Titles
		self.packItm['label_Titles_Name'] = Tk.Label(self, text="Titles:", font = FONT)
		self.packItm['label_Titles_Name'].pack(in_=self.packItm['labelCol'])
		
		self.packItm['label_Titles'] = Tk.Label(self, text="<Show Titles Here>", font=FONT)
		self.packItm['label_Titles'].pack(in_=self.packItm['rightCol'])
		
		# Units
		self.packItm['label_Unit'] = Tk.Label(self, text="Primary Unit:", font=FONT)
		self.packItm['label_Unit'].pack(in_=self.packItm['labelCol'])
		
		# Dropdown selection===============
		self.field_UnitVal = Tk.StringVar(self)
		self.field_UnitVal.set("Select Unit")
		
		self.unitOptions = s.fetchAllUnitNames()
		
		self.packItm['field_Unit'] = Tk.OptionMenu(self,self.field_UnitVal,*self.unitOptions)
		self.packItm['field_Unit'].pack(in_=self.packItm['rightCol'])
		# End Dropdown=====================
		
		# All Units
		self.packItm['label_AllUnits_Label'] = Tk.Label(self, text="All Units:", font=FONT)
		self.packItm['label_AllUnits_Label'].pack(in_=self.packItm['labelCol'])
		self.packItm['label_AllUnits'] = Tk.Label(self, text="All Units.", font=FONT)
		self.packItm['label_AllUnits'].pack(in_=self.packItm['rightCol'])
		
		# Email
		self.packItm['label_Email'] = Tk.Label(self, text="Email:", font=FONT)
		self.packItm['label_Email'].pack(in_=self.packItm['labelCol'])
		
		self.packItm['field_Email'] = Tk.Entry(self)
		self.packItm['field_Email'].pack(in_=self.packItm['rightCol'])
		
		# Buttons
		self.packItm['btnCol'] = Tk.Label(self)
		self.packItm['btnCol'].pack(side=Tk.BOTTOM)
		
		self.packItm['btn_update'] = Tk.Button(self, text="Submit", command=self.updateMember)
		self.packItm['btn_update'].pack(in_=self.packItm['memberCol'],side=Tk.LEFT)
		
		self.packItm['btn_clear'] = Tk.Button(self, text="Clear", command=self.clearMember)
		self.packItm['btn_clear'].pack(in_=self.packItm['memberCol'],side=Tk.LEFT)
		
		self.packItm['btn_del'] = Tk.Button(self, text="Delete", command=self.deleteMember)
		self.packItm['btn_del'].pack(in_=self.packItm['memberCol'],side=Tk.LEFT)
	
	
	
########################## Unit Screen ##################################
	
	def loadUnit(self,e):
		if self.curUid == None:
			i = self.packItm['unitBox'].index(Tk.ACTIVE)
			self.curUid = s.searchUnitName(self.units[i])[0]
			print self.curUid
			unitData = s.fetchUnit(self.curUid)
			
			#fill fields	
			self.packItm['field_unitName'].insert(0,unitData['UnitName'])
			if unitData['UnitType'] in self.unitTypeOptions:
				self.field_UnitType.set(unitData['UnitType'])
			self.packItm['field_unitZip'].insert(0,string.join(unitData['Zips'],","))
			self.packItm['field_unitLeader'].insert( 0, s.fetchFighterName( unitData['LeaderId'] ) )
			if unitData['LordsRepId']:
				self.packItm['field_lordRep'].insert( 0, s.fetchFighterName( unitData['LordsRepId'] ) )
			if unitData['CommonRepId']:
				self.packItm['field_commonRep'].insert( 0, s.fetchFighterName( unitData['CommonRepId'] ) )
			if unitData['HeraldId']:
				self.packItm['field_herald'].insert( 0, s.fetchFighterName( unitData['HeraldId'] ) )
			if unitData['MarshalId']:
				self.packItm['field_marshal'].insert( 0, s.fetchFighterName( unitData['MarshalId'] ) )
			self.packItm['field_endFunds'].insert(0,str(unitData['YearEndFunds']) )
			self.packItm['field_prevDues'].insert(0,str(unitData['YearlyDues']) )
			
			#self.packItm['label_AllUnits'].config(text= string.join(s.fetchAllUserUnits(self.curMid),", " ) )
		else:
			self.clearUnit()
			self.loadUnit(e)
	
	def updateUnit(self):
		unit = self.field_UnitType.get()
		newData = {
				'UnitName':self.packItm['field_unitName'].get(),
				'UnitType':self.field_UnitType.get(),
				'Landed':True if self.packItm['field_unitZip'].get() != '' else False,
				'Zips':string.split(self.packItm['field_unitZip'].get(),"," ),
				}
		try:
			newData['LeaderId'] = s.searchMemberPersName( self.packItm['field_unitLeader'].get() )[0]
		except IndexError:
			print "Error, Unit must have leader"
			return
		try:
			newData['LordsRepId'] = s.searchMemberPersName( self.packItm['field_lordRep'].get() )[0]
		except IndexError:
			pass
		try:
			newData['CommonRepId'] = s.searchMemberPersName( self.packItm['field_commonRep'].get() )[0]
		except IndexError:
			pass
		try:
			newData['HeraldId'] = s.searchMemberPersName( self.packItm['field_herald'].get() )[0]
		except IndexError:
			pass
		try:
			newData['MarshalId'] = s.searchMemberPersName( self.packItm['field_marshal'].get() )[0]
		except IndexError:
			pass
		try:
			newData['YearEndFunds'] = float( self.packItm['field_endFunds'].get() )
		except ValueError:
			newData['YearEndFunds'] = 0.0
		try:
			newData['YearlyDues'] = float( self.packItm['field_prevDues'].get() )
		except ValueError:
			newData['YearlyDues'] = 0.0
		
		#print newData
		
		if self.curUid:
			s.updateUnit(self.curUid,newData)
			
		else:
			if newData['UnitName'] != '' and newData['LeaderId']:
				s.createUnit(newData)
			
		self.clearUnit()
		self.updateUnitList()

		return
	
	def clearUnit(self):
		self.curUid = None;
		self.packItm['field_unitName'].delete(0,Tk.END)
		self.packItm['field_unitZip'].delete(0,Tk.END)
		self.packItm['field_unitLeader'].delete( 0, Tk.END )
		self.packItm['field_lordRep'].delete( 0, Tk.END )
		self.packItm['field_commonRep'].delete( 0, Tk.END )
		self.packItm['field_herald'].delete( 0, Tk.END )
		self.packItm['field_marshal'].delete( 0, Tk.END )
		self.packItm['field_endFunds'].delete(0,Tk.END)
		self.packItm['field_prevDues'].delete(0,Tk.END)
		self.field_UnitType.set("Select Type")
	
	def deleteUnit(self):
		if self.curUid:
			s.deleteUnit(self.curUid)
		self.clearUnit()
		self.updateUnitList()
	
	def updateUnitList(self):
		self.units = s.fetchAllUnitNames()
		self.packItm['unitBox'].delete(0,Tk.END)
		self.packItm['unitBox'].insert(Tk.END, *self.units)
	
	def unitScreen(self):
	
		# Unit Column
	 	self.packItm['unitCol'] = Tk.Label(self)
	 	self.packItm['unitCol'].pack(side=Tk.LEFT)
		# Unit Box
		self.packItm['unitBox'] = ScrolledListbox(self)
		self.updateUnitList()
		self.packItm['unitBox'].pack(in_=self.packItm['unitCol'])
		self.packItm['unitBox'].bind("<Double-Button-1>",self.loadUnit)
		
		# Btns
		self.packItm['btn_update'] = Tk.Button(self, text="Submit", command=self.updateUnit)
		self.packItm['btn_update'].pack(in_=self.packItm['unitCol'],side=Tk.LEFT)
		
		self.packItm['btn_clear'] = Tk.Button(self, text="Clear", command=self.clearUnit)
		self.packItm['btn_clear'].pack(in_=self.packItm['unitCol'],side=Tk.LEFT)
		
		self.packItm['btn_del'] = Tk.Button(self, text="Delete", command=self.deleteUnit)
		self.packItm['btn_del'].pack(in_=self.packItm['unitCol'],side=Tk.LEFT)
		
		# Columns
		self.packItm['rightCol'] = Tk.Label(self)
		self.packItm['rightCol'].pack(side=Tk.RIGHT)
		self.packItm['labelCol'] = Tk.Label(self)
		self.packItm['labelCol'].pack(in_=self.packItm['rightCol'],
		side=Tk.LEFT)
		
		# Unit Name
		self.packItm['label_unitName'] = Tk.Label(self, text="Name:", font=FONT)
		self.packItm['label_unitName'].pack(in_=self.packItm['labelCol'])
		self.packItm['field_unitName'] = Tk.Entry(self)
		self.packItm['field_unitName'].pack(in_=self.packItm['rightCol'])
		# Unit Type
		self.packItm['label_unitType'] = Tk.Label(self, text="Type:", font=FONT)
		self.packItm['label_unitType'].pack(in_=self.packItm['labelCol'])
		
		self.field_UnitType = Tk.StringVar(self)
		self.field_UnitType.set("Select Type")
		
		self.unitTypeOptions = [
								"Household",
								"Village",
								"Shire",
								"Town",
								"University",
								"Guild",
								"Barony",
								"County",
								"Marquistate",
								"Duchy",
								]
		
		self.packItm['field_unitType'] = Tk.OptionMenu(self,self.field_UnitType,*self.unitTypeOptions)
		self.packItm['field_unitType'].pack(in_=self.packItm['rightCol'])
		
		# Unit Zip Codes
		self.packItm['label_unitZip'] = Tk.Label(self, text="Zips:", font=FONT)
		self.packItm['label_unitZip'].pack(in_=self.packItm['labelCol'])
		self.packItm['field_unitZip'] = Tk.Entry(self)
		self.packItm['field_unitZip'].pack(in_=self.packItm['rightCol'])
		
		MemberList = s.fetchAllMemberNames()
		# Unit Leader
		self.packItm['label_unitLeader'] = Tk.Label(self, text="Leader:", font=FONT)
		self.packItm['label_unitLeader'].pack(in_=self.packItm['labelCol'])
		self.packItm['field_unitLeader'] = AutocompleteEntry(self)
		self.packItm['field_unitLeader'].set_completion_list(MemberList)
		self.packItm['field_unitLeader'].pack(in_=self.packItm['rightCol'])
		
		# Unit Lords Rep
		self.packItm['label_lordRep'] = Tk.Label(self, text="Lords Rep:", font=FONT)
		self.packItm['label_lordRep'].pack(in_=self.packItm['labelCol'])
		self.packItm['field_lordRep'] = AutocompleteEntry(self)
		self.packItm['field_lordRep'].set_completion_list(MemberList)
		self.packItm['field_lordRep'].pack(in_=self.packItm['rightCol'])
		
		# Unit Common Rep
		self.packItm['label_commonRep'] = Tk.Label(self, text="Common Rep:", font=FONT)
		self.packItm['label_commonRep'].pack(in_=self.packItm['labelCol'])
		self.packItm['field_commonRep'] = AutocompleteEntry(self)
		self.packItm['field_commonRep'].set_completion_list(MemberList)
		self.packItm['field_commonRep'].pack(in_=self.packItm['rightCol'])
		
		# Unit Herald
		self.packItm['label_herald'] = Tk.Label(self, text="Herald:", font=FONT)
		self.packItm['label_herald'].pack(in_=self.packItm['labelCol'])
		self.packItm['field_herald'] = AutocompleteEntry(self)
		self.packItm['field_herald'].set_completion_list(MemberList)
		self.packItm['field_herald'].pack(in_=self.packItm['rightCol'])
		
		# Unit Marshal
		self.packItm['label_marshal'] = Tk.Label(self, text="Marshal:", font=FONT)
		self.packItm['label_marshal'].pack(in_=self.packItm['labelCol'])
		self.packItm['field_marshal'] = AutocompleteEntry(self)
		self.packItm['field_marshal'].set_completion_list(MemberList)
		self.packItm['field_marshal'].pack(in_=self.packItm['rightCol'])
		
		# Previous Year-end Funds
		self.packItm['label_endFunds'] = Tk.Label(self, text="Year-end Funds:", font=FONT)
		self.packItm['label_endFunds'].pack(in_=self.packItm['labelCol'])
		self.packItm['field_endFunds'] = Tk.Entry(self)
		self.packItm['field_endFunds'].pack(in_=self.packItm['rightCol'])
		
		# Previous Yearly Dues
		self.packItm['label_prevDues'] = Tk.Label(self, text="Previous Dues:", font=FONT)
		self.packItm['label_prevDues'].pack(in_=self.packItm['labelCol'])
		self.packItm['field_prevDues'] = Tk.Entry(self)
		self.packItm['field_prevDues'].pack(in_=self.packItm['rightCol'])



######################### Unit Membership Screen #######################



	def loadUnitMembership(self,e):
		self.clearUnitMembership()
		i = self.packItm['unitBox'].index(Tk.ACTIVE)
		self.curUid = s.searchUnitName(self.units[i])[0]
		self.membersOfUnit = s.getMemberNamesInUnit(self.curUid)
		self.packItm['memberBox'].insert(Tk.END, *self.membersOfUnit)
		
	def loadMembership(self,e):
		self.clearMemberField()
		i = self.packItm['memberBox'].index(Tk.ACTIVE)
		memberName = self.membersOfUnit[i]
		self.curMid = s.searchMemberPersName(memberName)
		if self.membersOfUnit:
			self.packItm['field_activeMember'].insert( 0, memberName)
	
	def clearMemberField(self):
		self.curMid = None
		self.packItm['field_activeMember'].delete(0,Tk.END)
	
	def clearUnitMembership(self):
		self.packItm['memberBox'].delete(0,Tk.END)
		self.curUid = None
		self.clearMemberField()
		
	def joinMemberToUnit(self):
		name = self.packItm['field_activeMember'].get()
		if name not in self.membersOfUnit:
			try:
				userId = s.searchMemberPersName(name)[0]
				if userId:
					s.insertUserInUnit(userId,self.curUid)
			except IndexError:
				print "Member Not Found"
		else:
			print "user already in unit"
		self.loadUnitMembership(None)
		
	def deleteMemberFromUnit(self):
		name = self.packItm['field_activeMember'].get()
		if name in self.membersOfUnit:
			try:
				userId = s.searchMemberPersName(name)[0]
				s.removeUserFromUnit(userId,self.curUid)
			except IndexError:
				print "Member Not Found"
		self.loadUnitMembership(None)
		
	def unitMembershipScreen(self):
		ALLUSERS = s.fetchAllMemberNames()
		self.packItm['unitCol'] = Tk.Label(self)
	 	self.packItm['unitCol'].pack(side=Tk.LEFT)
	 	
	 	self.packItm['memberCol'] = Tk.Label(self)
	 	self.packItm['memberCol'].pack(side=Tk.LEFT)
	 	
		# Unit Box
		self.packItm['unitBox'] = ScrolledListbox(self)
		self.updateUnitList()
		self.packItm['unitBox'].pack(in_=self.packItm['unitCol'])
		self.packItm['unitBox'].bind("<Double-Button-1>",self.loadUnitMembership)
		
		# Member Box
		self.packItm['memberBox'] = ScrolledListbox(self)
		#self.updateUnitList()
		self.packItm['memberBox'].pack(in_=self.packItm['memberCol'])
		self.packItm['memberBox'].bind("<Button-1>",self.loadMembership)
		
		# Member Name
		self.packItm['field_activeMember'] = AutocompleteEntry(self)
		self.packItm['field_activeMember'].set_completion_list(ALLUSERS)
		self.packItm['field_activeMember'].pack(in_=self.packItm['memberCol'])
		
		# Buttons		
		self.packItm['btn_ungroupMember'] = Tk.Button(self, text="Leave Group", command=self.deleteMemberFromUnit)
		self.packItm['btn_ungroupMember'].pack(in_=self.packItm['memberCol'],side=Tk.LEFT)
				
		self.packItm['btn_groupMember'] = Tk.Button(self, text="Join Group", command=self.joinMemberToUnit)
		self.packItm['btn_groupMember'].pack(in_=self.packItm['memberCol'], side=Tk.LEFT)
		


######################### Awards Screen ################################



	def updateAwardsList(self):
		self.units = s.fetchAllUnitNames()
		self.packItm['awardBox'].delete(0,Tk.END)
		self.packItm['awardBox'].insert(Tk.END, *self.units)

	def awardsScreen(self):
		# Awards box
		self.packItm['awardBox'] = ScrolledListbox(self)
		#self.updateUnitList()
		self.packItm['awardBox'].pack(side=Tk.LEFT)
		self.packItm['awardBox'].bind("<Double-Button-1>",self.loadMember)
		
		# Columns
		self.packItm['rightCol'] = Tk.Label(self)
		self.packItm['rightCol'].pack(side=Tk.RIGHT)
		self.packItm['labelCol'] = Tk.Label(self)
		self.packItm['labelCol'].pack(in_=self.packItm['rightCol'],
		side=Tk.LEFT)



####################### Awards Management Screen #######################





####################### Fighter Practice Screen ########################


	def loadFighterInfo(self,e):
		self.clearFighterInfo()
		i = self.packItm['memberBox'].index(Tk.ACTIVE)
		memberName = self.members[i]
		try:
			self.curMid = s.searchMemberPersName(memberName)[0]
		except IndexError:
			print "member not found"
			return
		allMemberData = s.fetchMemberCard(self.curMid)
		self.packItm['label_name'].config(text=allMemberData['PersName'])
		if allMemberData['PracticeHours'] == None:
			allMemberData['PracticeHours'] = 0.0
		self.packItm['field_curHours'].config(text=allMemberData['PracticeHours'])
		
		# Get All Certifications for member.
		
		return
	
	def clearFighterInfo(self):
		self.curMid = None
		self.packItm['label_name'].config(text="Select Fighter")
		self.packItm['field_hours'].delete(0,Tk.END)
		return	
	
	def updateFighterHours(self):
		if self.curMid:
			current = float(self.packItm['field_curHours'].cget("text"))
			adjustBy = float(self.packItm['field_hours'].get())
			s.updateHours(self.curMid,current+adjustBy)
			self.loadFighterInfo(None)
		else:
			print "MID not set"

	def fighterScreen(self):
		# Columns
	 	self.packItm['memberCol'] = Tk.Label(self)
	 	self.packItm['memberCol'].pack(side=Tk.LEFT)
	 	
	 	self.packItm['rightCol'] = Tk.Label(self)
		self.packItm['rightCol'].pack(side=Tk.LEFT)
		
		self.packItm['hourSec'] = Tk.Label(self)
		
		self.packItm['midSec'] = Tk.Label(self)
	 	
		# Member Box
		self.packItm['memberBox'] = ScrolledListbox(self)
		self.updateMemberList()
		self.packItm['memberBox'].pack(in_=self.packItm['memberCol'], side=Tk.TOP)
		self.packItm['memberBox'].bind("<Double-Button-1>",self.loadFighterInfo)
		
		# Name Label
		
		self.packItm['label_name'] = Tk.Label(self, text= "Select Fighter", font=("Helvetica",18))
		self.packItm['label_name'].pack(in_=self.packItm['rightCol'])
		
		#pack here
		self.packItm['hourSec'].pack(in_=self.packItm['rightCol'])
		
		# Practice Hours Label
		
		self.packItm['label_hours'] = Tk.Label(self, text="Practice Hours: ", font=FONT)
		self.packItm['label_hours'].pack(in_=self.packItm['hourSec'], side=Tk.LEFT)
		
		self.packItm['field_curHours'] = Tk.Label(self, text="0",font=FONT)
		self.packItm['field_curHours'].pack(in_=self.packItm['hourSec'], side=Tk.LEFT)
		
		# pack here
		self.packItm['midSec'].pack(in_=self.packItm['rightCol'])
		
		# Increase Practice Field
		self.packItm['field_hours'] = Tk.Entry(self)
		self.packItm['field_hours'].pack(in_=self.packItm['midSec'],side=Tk.LEFT)
		
		# Increase Practice time Button
		self.packItm['btn_subHours'] = Tk.Button(self,text="Adjust hours",command=self.updateFighterHours)
		self.packItm['btn_subHours'].pack(in_=self.packItm['midSec'],side=Tk.LEFT)
		
		# Certifications label
		self.packItm['label_certs'] = Tk.Label(self, text="Certifications")
		self.packItm['label_certs'].pack(in_=self.packItm['rightCol'])
		
		# Certifications checkboxes. Auto synch
		AllCert = s.getAllCerts()
		
		i = 0
		self.certIds = []
		for cert in AllCert:
			self.certIds.append(cert[0])
			self.packItm['container'+str(cert[0])] = Tk.Label(self,width=20)
			self.packItm['container'+str(cert[0])].pack(in_=self.packItm['rightCol'])
			print cert
			self.packItm['field_certs'+str(cert[0])] = Tk.Checkbutton(self,text=cert[1],width=30)
			self.packItm['field_certs'+str(cert[0])].pack(in_=self.packItm['container'+str(i)])


	def __init__(self,master = None):
		Tk.Frame.__init__(self,master)
		self.packItm = {}
		self.curMid = None
		self.curUid = None
		self.pack()
		self.switchMembers()
		
root = Tk.Tk()
root.minsize(300,300)
root.geometry("500x500")

app = AMRSClientGUI()

menubar = Tk.Menu(root)
NAVFONT = ("Helvetica",9)
menubar.add_command(label = "Members",command=app.switchMembers, font=NAVFONT)
menubar.add_command(label = "Units", command=app.switchUnits, font=NAVFONT)
menubar.add_command(label = "Unit Membership", command=app.switchUnitMembership, font=NAVFONT)
menubar.add_command(label = "Awards", command=app.switchAward, font=NAVFONT)
menubar.add_command(label = "Manage Awards", command=app.switchAward, font=NAVFONT)
menubar.add_command(label = "Fighter Practice", command=app.switchPractice, font=NAVFONT)
menubar.add_command(label = "Exit", command=root.quit, font=NAVFONT)
root.config(menu=menubar)

app.mainloop()
root.destroy()
