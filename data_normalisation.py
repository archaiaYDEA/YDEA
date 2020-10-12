#READ FILE, CONVERT TO STRING, REMOVE EMPTY VALUES
from pandas import DataFrame, Series
data_frame = pd.read_csv('DuraEuropos.csv')
data_frame = data_frame.astype(str)
data_frame['Medium'] = data_frame['Medium'].str.lower()
data_frame['Culture'] = data_frame['Culture'].str.lower()

#REMOVE LINE BREAKS
data_frame = data_frame.replace(r'\\n',' ', regex=True)
data_frame = data_frame.replace(r'\n',' ', regex=True)
data_frame = data_frame.replace(r'\\r',' ', regex=True)
data_frame = data_frame.replace(r'\r',' ', regex=True)
data_frame = data_frame.replace(r'  ',' ', regex=True)

#TURN FLOAT OBJECT NUMBERS TO STR
data_frame['Sort']=data_frame['Sort'].str.replace(r'([0-9])( )+?([0-9])',r'\1.\3')
data_frame['Sort']=data_frame['Sort'].str.replace(r'( )+','-')
data_frame['ObjectNumber'] = 'inv. ' + data_frame['Sort']

#ADD COLLECTION
data_frame['Collection'] = 'Yale University Art Gallery'

#COllECTION REFERENCE
data_frame['Reference'] = 'https://artgallery.yale.edu/collections/objects/' + data_frame['ID'].astype(str)

#DROP COLUMNS, DROP FACSIMILES, MOVE COINS
data_frame.drop(['BeginDate','EndDate','Sort','Geography','RightsType', 'WebChat','CreditLine', 'Department'], axis=1, inplace=True) 
data_frame.drop(data_frame.loc[data_frame['Culture'].str.contains("american")].index, inplace=True)
#data_frame.drop(data_frame.loc[data_frame['Medium'].str.contains("plaster cast")].index, inplace=True)
#data_frame.loc[data_frame['Classification'].str.contains("Numismatics")].to_csv('/Users/kyleconrau-lewis/Google Drive/dura_europos/coins.csv',index=False)
data_frame.drop(data_frame.loc[data_frame['Classification'].str.contains("Numismatics")].index, inplace=True)
                 
#MAKERS (remove unknown artists) # what to do with Roman?
data_frame['Makers'] = data_frame['Makers'].str.replace('Maker: Unknown', 'anonymous') 
data_frame['Makers'] = data_frame['Makers'].str.replace('Artist: Unknown', 'anonymous')
data_frame['Makers'] = data_frame['Makers'].str.replace('Carver: Unknown', 'anonymous')
data_frame['Makers'] = data_frame['Makers'].str.replace('Roman', '')
data_frame['Makers'] = data_frame['Makers'].str.replace('Parthian', '')

#DATE 
data_frame['Date'] = data_frame['Date'].str.lower()
data_frame['Date'] = data_frame['Date'].str.replace('century','')
data_frame['Date'] = data_frame['Date'].str.replace('n.d.','')
data_frame['Date'] = data_frame['Date'].str.replace('–','to')
data_frame['Date'] = data_frame['Date'].str.replace('-', 'to')
data_frame['Date'] = data_frame['Date'].str.replace('/', 'to')
data_frame['Date'] = data_frame['Date'].str.replace('midto','mid ')
data_frame['Date'] = data_frame['Date'].str.replace('first','1st')
data_frame['Date'] = data_frame['Date'].str.replace('second','2nd')
data_frame['Date'] = data_frame['Date'].str.replace('third','3rd')

#DATES WITHOUT BC/AD, ASSUME AD
data_frame.loc[(data_frame['Date'].str.contains("b.c|b.c.|a.d|a.d.", na=True)==False)&(data_frame['Date'].str.contains("[0-9]", na=False)), 'Date'] = 'a.d. ' + data_frame.loc[(data_frame['Date'].str.contains("b.c|b.c.|a.d|a.d.", na=True)==False)&(data_frame['Date'].str.contains("[0-9]", na=False)), 'Date']

#CONVERT EARLY, MID, LATE, 1st, 2nd, 3rd (this is only when working with A.D.)
data_frame['Date'] = data_frame['Date'].str.replace('early 3rd', 'ca. 225')
data_frame['Date'] = data_frame['Date'].str.replace('early 2nd', 'ca. 125')
data_frame['Date'] = data_frame['Date'].str.replace('early 1st', 'ca. 25')
data_frame['Date'] = data_frame['Date'].str.replace('mid 3rd', 'ca. 250')
data_frame['Date'] = data_frame['Date'].str.replace('mid 2nd', 'ca. 150')
data_frame['Date'] = data_frame['Date'].str.replace('mid 1st', 'ca. 50')
data_frame['Date'] = data_frame['Date'].str.replace('late 3rd', 'ca. 275')
data_frame['Date'] = data_frame['Date'].str.replace('late 2nd', 'ca. 175')
data_frame['Date'] = data_frame['Date'].str.replace('late 1st', 'ca. 75')

#PARSE "BEFORE"
data_frame['Date'] = data_frame['Date'].str.replace('before', 'ca. 323b.c. to')

#CHANGE DATES TO EARLIEST AND LATEST, PARSE 'ca.' AND 'probably'
data_frame['DateCertainty'] = data_frame['Date'].apply(lambda x: 'circa' if 'ca.' in x else 'probably' if 'probably' in x else '')
data_frame['Date'] = data_frame['Date'].str.replace('ca.|probably', '')
data_frame[['EarliestDate','LatestDate']] = data_frame['Date'].str.split(pat='to', expand=True)
data_frame['Date'] = data_frame['Date'].apply(lambda x: x if 'to' not in x else '')

#CONVERTING bc/ad TO STANDARD TIME
data_frame[['Date', 'EarliestDate', 'LatestDate']] = data_frame[['Date', 'EarliestDate', 'LatestDate']].stack().str.replace('b.c.', '-', regex=False).unstack()
data_frame[['Date', 'EarliestDate', 'LatestDate']] = data_frame[['Date', 'EarliestDate', 'LatestDate']].stack().str.replace('a.d.', '+', regex=False).unstack()
data_frame[['Date', 'EarliestDate', 'LatestDate']] = data_frame[['Date', 'EarliestDate', 'LatestDate']].stack().str.replace('b.c', '-', regex=False).unstack()
data_frame[['Date', 'EarliestDate', 'LatestDate']] = data_frame[['Date', 'EarliestDate', 'LatestDate']].stack().str.replace('a.d', '+', regex=False).unstack()
data_frame[['Date', 'EarliestDate', 'LatestDate']] = data_frame[['Date', 'EarliestDate', 'LatestDate']].stack().str.replace(' ', '').unstack()

#ADDING bce OR ad TO COLUMN, MOVING TO START OF COLUMN
data_frame.loc[(data_frame["EarliestDate"].str.contains("+", na=False, regex=False)) & (data_frame["LatestDate"].str.contains("+", na=False, regex=False)==False), "LatestDate"] = "+" + data_frame.loc[(data_frame["EarliestDate"].str.contains("+", na=False, regex=False)) & (data_frame["LatestDate"].str.contains("+", na=False, regex=False)==False), "LatestDate"]
data_frame.loc[(data_frame["LatestDate"].str.contains("-", na=False, regex=False)) & (data_frame["EarliestDate"].str.contains("-", na=False,regex=False)==False), "EarliestDate"] = "-" + data_frame.loc[(data_frame["LatestDate"].str.contains("-", na=False, regex=False)) & (data_frame['EarliestDate'].str.contains('-', na=False, regex=False)==False), "EarliestDate"] 
data_frame.loc[(data_frame["LatestDate"].str.contains("+", na=False, regex=False)) & (data_frame["EarliestDate"].str.contains('+', na=False, regex=False)==False) & (data_frame["EarliestDate"].str.contains('-', na=False, regex=False)==False), "EarliestDate"] = '+' + data_frame.loc[(data_frame["LatestDate"].str.contains("+", na=False, regex=False)) & (data_frame["EarliestDate"].str.contains('+', na=False, regex=False)==False) & (data_frame["EarliestDate"].str.contains('-', na=False, regex=False)==False), "EarliestDate"]

data_frame.loc[data_frame['Date'].str.contains('-', na=False, regex=False), 'Date'] = '-' + data_frame.loc[data_frame['Date'].str.contains('-', na=False, regex=False), 'Date'].str.replace('-','')
data_frame.loc[data_frame['Date'].str.contains('+', na=False, regex=False), 'Date'] = '+' + data_frame.loc[data_frame['Date'].str.contains('+', na=False, regex=False), 'Date'].str.replace('+','')

data_frame.loc[data_frame['EarliestDate'].str.contains('-', na=False, regex=False), 'EarliestDate'] = '-' + data_frame.loc[data_frame['EarliestDate'].str.contains('-', na=False, regex=False), 'EarliestDate'].str.replace('-','')
data_frame.loc[data_frame['EarliestDate'].str.contains('+', na=False, regex=False), 'EarliestDate'] = '+' + data_frame.loc[data_frame['EarliestDate'].str.contains('+', na=False, regex=False), 'EarliestDate'].str.replace('+','')

data_frame.loc[data_frame['LatestDate'].str.contains('-', na=False, regex=False), 'LatestDate'] = '-' + data_frame.loc[data_frame['LatestDate'].str.contains('-', na=False, regex=False), 'LatestDate'].str.replace('-','')
data_frame.loc[data_frame['LatestDate'].str.contains('+', na=False, regex=False), 'LatestDate'] = '+' + data_frame.loc[data_frame['LatestDate'].str.contains('+', na=False, regex=False), 'LatestDate'].str.replace('+','')

#DELETE DUPLICATE INFORMATION IN DATE FIELD
data_frame.loc[data_frame['Date'].str.contains('[0-9]'), 'EarliestDate'] = data_frame.loc[data_frame['Date'].str.contains('[0-9]'), 'EarliestDate'].str.replace('.*', '')

#JUST A PRELIMINARY REPRESENTATION OF CENTURY FIELDS (these could be expressed at precision 9--CENTURY-- but then it difficult to convert to integer to expand abbreviations)
data_frame['EarliestDate'] = data_frame['EarliestDate'].str.replace('+1st', '+1', regex=False)
data_frame['EarliestDate'] = data_frame['EarliestDate'].str.replace('+2nd', '+100', regex=False)
data_frame['EarliestDate'] = data_frame['EarliestDate'].str.replace('+3rd', '+200', regex=False)
data_frame['EarliestDate'] = data_frame['EarliestDate'].str.replace('+4th', '+300', regex=False)
data_frame['EarliestDate'] = data_frame['EarliestDate'].str.replace('-1st', '-99', regex=False)
data_frame['EarliestDate'] = data_frame['EarliestDate'].str.replace('-2nd', '-199', regex=False)
data_frame['EarliestDate'] = data_frame['EarliestDate'].str.replace('-3rd', '-299', regex=False)
data_frame['EarliestDate'] = data_frame['EarliestDate'].str.replace('-4th', '-399', regex=False)

data_frame['LatestDate'] = data_frame['LatestDate'].str.replace('+1st', '+99', regex=False)
data_frame['LatestDate'] = data_frame['LatestDate'].str.replace('+2nd', '+199', regex=False)
data_frame['LatestDate'] = data_frame['LatestDate'].str.replace('+3rd', '+299', regex=False)
data_frame['LatestDate'] = data_frame['LatestDate'].str.replace('+4th', '+399', regex=False)
data_frame['LatestDate'] = data_frame['LatestDate'].str.replace('-1st', '-1', regex=False)
data_frame['LatestDate'] = data_frame['LatestDate'].str.replace('-2nd', '-101', regex=False)
data_frame['LatestDate'] = data_frame['LatestDate'].str.replace('-3rd', '-201', regex=False)
data_frame['LatestDate'] = data_frame['LatestDate'].str.replace('-4th', '-301', regex=False)

#EXPANDING ABBREVIATED DATES
data_frame['EarliestDate'] = pd.to_numeric(data_frame['EarliestDate'], errors='coerce')
data_frame['LatestDate'] = pd.to_numeric(data_frame['LatestDate'], errors='coerce')
data_frame.loc[(data_frame.EarliestDate > 100) &(data_frame.EarliestDate > data_frame.LatestDate), 'LatestDate'] = np.floor(data_frame.loc[(data_frame.EarliestDate >100) & (data_frame.EarliestDate > data_frame.LatestDate), 'EarliestDate'] /100 )*100+ data_frame.loc[(data_frame.EarliestDate >100) &(data_frame.EarliestDate > data_frame.LatestDate), 'LatestDate']
data_frame.loc[(1 < data_frame.EarliestDate) & (data_frame.EarliestDate < 100) & (data_frame.EarliestDate > data_frame.LatestDate), 'LatestDate'] = np.floor(data_frame.loc[(1 < data_frame.EarliestDate) & (data_frame.EarliestDate < 100) & (data_frame.EarliestDate > data_frame.LatestDate), 'EarliestDate'] /10 )*10 + data_frame.loc[(1 < data_frame.EarliestDate) & (data_frame.EarliestDate < 100) &(data_frame.EarliestDate > data_frame.LatestDate), 'LatestDate']

#CHANGE YEAR 0 to 1
data_frame.loc[data_frame['EarliestDate'] == 0, 'EarliestDate'] = data_frame.loc[data_frame['EarliestDate'] == 0, 'EarliestDate'] + 1

#DEALING WITH CENTURIES        
data_frame['Date'] = data_frame['Date'].str.replace('+1st', '+0100-00-00T00:00:00Z/7', regex=False)
data_frame['Date'] = data_frame['Date'].str.replace('+2nd', '+0200-00-00T00:00:00Z/7', regex=False)
data_frame['Date'] = data_frame['Date'].str.replace('+3rd', '+0300-00-00T00:00:00Z/7', regex=False)
data_frame['Date'] = data_frame['Date'].str.replace('+4th', '+0400-00-00T00:00:00Z/7', regex=False)
data_frame['Date'] = data_frame['Date'].str.replace('+5th', '+0500-00-00T00:00:00Z/7', regex=False)
data_frame['Date'] = data_frame['Date'].str.replace('-1st', '-0100-00-00T00:00:00Z/7', regex=False)
data_frame['Date'] = data_frame['Date'].str.replace('-2nd', '-0200-00-00T00:00:00Z/7', regex=False)
data_frame['Date'] = data_frame['Date'].str.replace('-3rd', '-0300-00-00T00:00:00Z/7', regex=False)
data_frame['Date'] = data_frame['Date'].str.replace('-4th', '-0400-00-00T00:00:00Z/7', regex=False)

#REVERT DATES TO STRING (only works for years), CONVERT TO DATE_TIME (go back and correct centuries), exclude nan
data_frame['EarliestDate'] = data_frame['EarliestDate'].astype(str)
data_frame['LatestDate'] = data_frame['LatestDate'].astype(str)
data_frame['EarliestDate'] =data_frame['EarliestDate'].str.replace('.0','',regex=False)
data_frame['LatestDate'] =data_frame['LatestDate'].str.replace('.0','',regex=False)
data_frame['EarliestDate'] = data_frame['EarliestDate'].str.zfill(4)
data_frame['EarliestDate'] =  data_frame['EarliestDate'].apply(lambda x: x.zfill(5) if '-' in x else x)
data_frame['LatestDate'] = data_frame['LatestDate'].str.zfill(4)
data_frame['LatestDate'] =  data_frame['LatestDate'].apply(lambda x: x.zfill(5) if '-' in x else x)
data_frame['EarliestDate'] = data_frame['EarliestDate'].apply(lambda x: '+'+x if '-'not in x else x)
data_frame['LatestDate'] = data_frame['LatestDate'].apply(lambda x: '+'+x if '-'not in x else x)

data_frame['EarliestDate'] = data_frame['EarliestDate'].str.replace('0-','-0', regex=False)
data_frame['EarliestDate'] = data_frame['EarliestDate'].str.replace('0-','-0', regex=False)

data_frame['LatestDate'] = data_frame['LatestDate'].str.replace('0-','-0', regex=False)
data_frame['LatestDate'] = data_frame['LatestDate'].str.replace('0-','-0', regex=False)
data_frame['LatestDate'] = data_frame['LatestDate'].str.replace('0-','-0', regex=False)

data_frame['EarliestDate'] = data_frame['EarliestDate']+'-00-00T00:00:00Z/9'
data_frame['LatestDate'] = data_frame['LatestDate']+'-00-00T00:00:00Z/9'
data_frame.loc[data_frame['EarliestDate'].str.contains('0nan'), 'EarliestDate'] = data_frame.loc[data_frame['EarliestDate'].str.contains('0nan'), 'EarliestDate'].str.replace(r'.*', '')
data_frame.loc[data_frame['LatestDate'].str.contains('0nan'), 'LatestDate'] = data_frame.loc[data_frame['LatestDate'].str.contains('0nan'), 'LatestDate'].str.replace(r'.*', '')

data_frame.loc[(data_frame['Date'].str.contains('[0-9]', na=False)) & (data_frame['Date'].str.contains('-', na=True)==False), 'Date'] = data_frame.loc[(data_frame['Date'].str.contains('[0-9]', na=False)) & (data_frame['Date'].str.contains('-', na=True)==False), 'Date'].str.zfill(5)
data_frame['Date']=data_frame['Date'].str.replace('0+', '+0', regex=False)
data_frame['Date']=data_frame['Date'].str.replace('0+', '+0', regex=False)
data_frame.loc[(data_frame['Date'].str.contains('[0-9]', na=False)) & (data_frame['Date'].str.contains('-', na=True)==False), 'Date']=data_frame.loc[(data_frame['Date'].str.contains('[0-9]', na=False)) & (data_frame['Date'].str.contains('-', na=True)==False), 'Date']+'-00-00T00:00:00Z/9'

#REMOVE ITEMS WITH MULTIPLE PARTS, USING COMPONENT IDs
#(DIMENSIONS / MEDIUM MUST BE PARSED SEPARATELY)
comp_ids = pd.read_csv('/Users/kyleconrau-lewis/Google Drive/dura_europos/Dura_Comps.csv')
comp_ids['ID']=comp_ids['ID'].astype(str)
data_frame['ID']=data_frame['ID'].astype(str)
multiples = comp_ids.loc[comp_ids.duplicated(subset=['ID'])==True]

multiples= data_frame.merge(multiples,on='ID')
multiples=multiples[['ID','Title','ObjectNumber','CompID','ComponentNum','CompName','Dimensions','Collection','Reference','Date','DateCertainty','Date','EarliestDate','LatestDate','Classification','Culture','Period','Medium','Provenance','Copyright','Bibliography']]
multiples.to_csv('/Users/kyleconrau-lewis/Google Drive/dura_europos/subcomponent_objects.csv',index=False)

for row in multiples['ID']:
    data_frame.drop(data_frame.loc[data_frame['ID']==row].index, inplace=True)



#REMOVE OXFORD COMMA
data_frame['Medium'] = data_frame['Medium'].str.replace(', and','and')
#CORRECT SPELLING
data_frame['Medium'] = data_frame['Medium'].str.replace('pigmenrt','pigment', regex=False)
data_frame['Medium'] = data_frame['Medium'].str.replace('withp','pigment', regex=False)

#PARSE OUT COLOURS; NORMALISE EXPRESSIONS
data_frame['Title']=data_frame['Title'].str.replace(' ware', 'ware')
data_frame['Title']=data_frame['Title'].str.replace('grey', 'gray')
data_frame['Medium']=data_frame['Medium'].str.replace('grey', 'gray')
data_frame['Title']=data_frame['Title'].str.replace('Grey', 'Gray')
data_frame['Medium']=data_frame['Medium'].str.replace('Grey', 'Gray')

data_frame['Colors']=data_frame['Title'].str.lower()+' ' + data_frame['Medium'].str.lower()
colours=['red','coral','blue','cream','iridescent','purple','blue-green','black','brown-green','blue-green', 'brown','colorless','beige','white','sage','yellow','dark','opaque','pink','gray']
pat=rf"\b(?:{'|'.join(colours)})"
data_frame['Colors']=data_frame['Colors'].astype(str)
data_frame['Colors']=data_frame['Colors'].str.findall(pat).str.join(', ')

#REMOVE COLOURS, NON-MEDIUM EXPRESSIONS
data_frame['Medium'] = data_frame['Medium'].str.replace('; traces of red on lips and eyes','')
data_frame['Medium'] = data_frame['Medium'].str.replace('bitumen on upper part of plaque','bitumen')
data_frame['Medium'] = data_frame['Medium'].str.replace('bitumen on lower part of back','bitumen')
data_frame['Medium'] = data_frame['Medium'].str.replace('on upper border','')
data_frame['Medium'] = data_frame['Medium'].str.replace('fragment of wall painting from middle mithraeum','')

data_frame['Medium'] = data_frame['Medium'].str.replace('glassred', 'glass red')
data_frame['Medium'] = data_frame['Medium'].str.replace('(?<![a-z])red(?![a-z])','')
data_frame['Medium'] = data_frame['Medium'].str.replace('blue-green','')
data_frame['Medium'] = data_frame['Medium'].str.replace('brown-green','')
data_frame['Medium'] = data_frame['Medium'].str.replace('blue ','')
data_frame['Medium'] = data_frame['Medium'].str.replace(' l. ','', regex=False)
data_frame['Medium'] = data_frame['Medium'].str.replace('black ','')
data_frame['Medium'] = data_frame['Medium'].str.replace('colorless\s?','')
data_frame['Medium'] = data_frame['Medium'].str.replace('brown ','')
data_frame['Medium'] = data_frame['Medium'].str.replace('beige ','')
data_frame['Medium'] = data_frame['Medium'].str.replace('white ','')
data_frame['Medium'] = data_frame['Medium'].str.replace('sage ','')
data_frame['Medium'] = data_frame['Medium'].str.replace('dark ','')
data_frame['Medium'] = data_frame['Medium'].str.replace('opaque ','')
data_frame['Medium'] = data_frame['Medium'].str.replace('yellow ','')
data_frame['Medium'] = data_frame['Medium'].str.replace('yellow,','')
data_frame['Medium'] = data_frame['Medium'].str.replace('pink ','')
data_frame['Medium'] = data_frame['Medium'].str.replace('thick yellowish ','')
data_frame['Medium'] = data_frame['Medium'].str.replace('grayish','')
data_frame['Medium'] = data_frame['Medium'].str.replace('gray  ','')
data_frame['Medium'] = data_frame['Medium'].str.replace('light ','')
data_frame['Medium'] = data_frame['Medium'].str.replace('corroded','')
data_frame['Medium'] = data_frame['Medium'].str.replace('pinkish','')

data_frame.loc[data_frame['Medium'].str.contains('spoon'), 'Medium'] = data_frame.loc[data_frame['Medium'].str.contains('spoon'), 'Medium'].str.replace('spoon','bronze')

data_frame['Medium'] = data_frame['Medium'].str.replace('green','')
data_frame['Medium'] = data_frame['Medium'].str.replace('spots','')
data_frame['Medium'] = data_frame['Medium'].str.replace('light yellowish-gray','')
data_frame['Medium'] = data_frame['Medium'].str.replace('multi-colored','')
data_frame['Medium'] = data_frame['Medium'].str.replace('wool, undyed','undyed wool')

#WHAT DOES "VARIOUS" MEAN? How to deal with prose descriptions?
data_frame['Medium'] = data_frame['Medium'].str.replace('B is','')
data_frame['Medium'] = data_frame['Medium'].str.replace('various','')
data_frame['Medium'] = data_frame['Medium'].str.replace('natural','')
data_frame['Medium'] = data_frame['Medium'].str.replace('photograph is of the cast','stone')
data_frame['Medium'] = data_frame['Medium'].str.replace('in barrel shape', '')
data_frame['Medium'] = data_frame['Medium'].str.replace('in 5 pieces','')
data_frame['Medium'] = data_frame['Medium'].str.replace('slightly in breaks','')
data_frame['Medium'] = data_frame['Medium'].str.replace('incrustation in sections in relief','')
data_frame['Medium'] = data_frame['Medium'].str.replace('joined','')
data_frame['Medium'] = data_frame['Medium'].str.replace('moldmade','')
data_frame['Medium'] = data_frame['Medium'].str.replace('single','')
data_frame['Medium'] = data_frame['Medium'].str.replace('pieced','')
data_frame['Medium'] = data_frame['Medium'].str.replace('mixed','')
data_frame['Medium'] = data_frame['Medium'].str.replace('conglomerate','')
data_frame['Medium'] = data_frame['Medium'].str.replace('considerable','')
data_frame['Medium'] = data_frame['Medium'].str.replace('several','')
data_frame['Medium'] = data_frame['Medium'].str.replace('areas','')
data_frame['Medium'] = data_frame['Medium'].str.replace('prov: synagogue l7','')
data_frame['Medium'] = data_frame['Medium'].str.replace('synagogue l7','')
data_frame['Medium'] = data_frame['Medium'].str.replace('was','')
data_frame['Medium'] = data_frame['Medium'].str.replace('formerly','')
data_frame['Medium'] = data_frame['Medium'].str.replace('partly','')
data_frame['Medium'] = data_frame['Medium'].str.replace('originally','')
data_frame['Medium'] = data_frame['Medium'].str.replace('traces? of','')
data_frame['Medium'] = data_frame['Medium'].str.replace('semi-precious','')
data_frame['Medium'] = data_frame['Medium'].str.replace('fragments','')
data_frame['Medium'] = data_frame['Medium'].str.replace('made in a mold','')
data_frame['Medium'] = data_frame['Medium'].str.replace(',on interior','')
data_frame['Medium'] = data_frame['Medium'].str.replace('on lower part of back','')
data_frame['Medium'] = data_frame['Medium'].str.replace('pierced','')
data_frame['Medium'] = data_frame['Medium'].str.replace('inlay','')
data_frame['Medium'] = data_frame['Medium'].str.replace('interior','')
data_frame['Medium'] = data_frame['Medium'].str.replace('inside','')
data_frame['Medium'] = data_frame['Medium'].str.replace('somewhat rough','')
data_frame['Medium'] = data_frame['Medium'].str.replace('used in inscription','')
data_frame['Medium'] = data_frame['Medium'].str.replace('some', '')
data_frame['Medium'] = data_frame['Medium'].str.replace('media', '')
data_frame['Medium'] = data_frame['Medium'].str.replace('shapes?', '')
data_frame['Medium'] = data_frame['Medium'].str.replace('solid', '')
data_frame['Medium'] = data_frame['Medium'].str.replace('. moldmade (single mold).','')
data_frame['Medium'] = data_frame['Medium'].str.replace('layer of painted plaster',' paint, plaster')
data_frame['Medium'] = data_frame['Medium'].str.replace('painted','paint,')
data_frame['Medium'] = data_frame['Medium'].str.replace('painting','paint,')
data_frame['Medium'] = data_frame['Medium'].str.replace('enameled','enamel,')
data_frame['Medium'] = data_frame['Medium'].str.replace('retouched','enamel,')
data_frame['Medium'] = data_frame['Medium'].str.replace('part','')
data_frame['Medium'] = data_frame['Medium'].str.replace('\(','')
data_frame['Medium'] = data_frame['Medium'].str.replace('\)','')
data_frame['Medium'] = data_frame['Medium'].str.replace('etc\.','')
data_frame['Medium'] = data_frame['Medium'].str.replace(' a ','')
data_frame['Medium'] = data_frame['Medium'].str.replace('[0-9]','')
data_frame['Medium'] = data_frame['Medium'].str.replace('\'s','', regex=True)

#HOW TO DEAL WITH 'OR' and ??
data_frame['Medium'] = data_frame['Medium'].str.replace('(?)','?', regex=False)
data_frame['Medium Certainty'] = data_frame['Medium'].apply(lambda x: 'possibly' if '?' in x else 'possibly' if ' or ' in x else 'probably' if 'probably' in x else 'visible under microscope' if 'enamel visible under microscope' in x else 'possibly' if 'possible' in x else '')
data_frame['Medium'] = data_frame['Medium'].str.replace('?', '', regex=False)
data_frame['Medium'] = data_frame['Medium'].str.replace('uncertain', '', regex=False)
data_frame['Medium'] = data_frame['Medium'].str.replace('probably', '', regex=False)
data_frame['Medium'] = data_frame['Medium'].str.replace('possible', '', regex=False)
data_frame['Medium'] = data_frame['Medium'].str.replace('enamel visible under microscope', '', regex=False)

#REMOVE STRANDED DELIMITERS (,.;)
#data_frame['Medium'] = data_frame['Medium'].str.replace(r'([,:\.;])([,:\.;])*?', r'\1')
#data_frame['Medium'] = data_frame['Medium'].str.replace('etc.', 'etc', regex=False)
data_frame['Medium'] = data_frame['Medium'].str.replace(' with ', ',')
data_frame['Medium'] = data_frame['Medium'].str.replace(' or ', ',')
data_frame['Medium'] = data_frame['Medium'].str.replace('and ', ',')
data_frame['Medium'] = data_frame['Medium'].str.replace(';', ',')
data_frame['Medium'] = data_frame['Medium'].str.replace(' on ', ',')
data_frame['Medium'] = data_frame['Medium'].str.replace(':', ',')
data_frame['Medium'] = data_frame['Medium'].str.replace('/', ',')
data_frame['Medium'] = data_frame['Medium'].str.replace('.', ',', regex=False)
data_frame['Medium'] = data_frame['Medium'].str.strip(', ')
data_frame['Medium'] = data_frame['Medium'].str.replace(r',+', ',')
data_frame['Medium'] = data_frame['Medium'].str.replace(', ,',',')


#SPLIT MEDIUM, DOES NOT EXCLUDE CASES INVOLVING COLOURS
data_frame['Medium'] = data_frame['Medium'].str.split(',')
data_frame['Medium'] = data_frame['Medium'].astype(str)
data_frame['Medium'] = data_frame['Medium'].str.replace('[','')
data_frame['Medium'] = data_frame['Medium'].str.replace(']','')
data_frame['Medium'] = data_frame['Medium'].str.replace('\'','')
#data_frame = data_frame.explode('Medium')
#data_frame['Medium'] = data_frame['Medium'].str.replace('nan', '')


#DELETE INCH TRANSLATION FROM DIMENSIONS
data_frame['Dimensions'] = data_frame['Dimensions'].astype(str)
data_frame['Dimensions'] = data_frame['Dimensions'].str.lower()
data_frame['Dimensions'] = data_frame['Dimensions'].replace(r'\([^)]*\)','', regex=True)

#DROP DIMENSIONS DISTINGUISHING WARP, WEFT, INNER, FRAGMENT
data_frame['Dimensions']=data_frame['Dimensions'].str.replace('warp ', 'warp: ')
data_frame['Dimensions']=data_frame['Dimensions'].str.replace('weft ', 'weft: ')
data_frame.drop(data_frame.loc[data_frame['Dimensions'].str.contains(':')].index, inplace=True)
data_frame.drop(data_frame.loc[data_frame['Dimensions'].str.contains('vari.*')].index, inplace=True)
data_frame.drop(data_frame.loc[data_frame['Dimensions'].str.contains('research')].index, inplace=True)
data_frame.drop(data_frame.loc[data_frame['Dimensions'].str.contains('approx')].index, inplace=True)
data_frame.drop(data_frame.loc[data_frame['Dimensions'].str.contains('irregular')].index, inplace=True)

#NORMALISE
data_frame['Dimensions'] =data_frame['Dimensions'].str.replace('  ', ' ')
#data_frame['Medium'] = data_frame['Medium'].str.replace('  ',' ')
#data_frame['Medium'] = data_frame['Medium'].str.strip()
#data_frame.drop_duplicates(inplace=True)

#REMOVE IMPLICIT MULTIPLES 
data_frame.drop(data_frame.loc[data_frame['Dimensions'].str.contains('in. [0-9]')].index, inplace=True)
data_frame.drop(data_frame.loc[data_frame['Dimensions'].str.contains('in. [a-z]')].index, inplace=True)
data_frame.drop(data_frame.loc[data_frame['Dimensions'].str.contains('cm [0-9]')].index, inplace=True)
data_frame.drop(data_frame.loc[data_frame['Dimensions'].str.contains('cm [a-z]')].index, inplace=True)

#REMOVE ITEMS WITH MIXED CM/IN EXPRESSIONS (NOT EQUIVALENT)
data_frame.drop(data_frame.loc[(data_frame['Dimensions'].str.contains('cm')) & (data_frame['Dimensions'].str.contains('in.'))].index, inplace=True)

#CREATE WEIGHT COLUMN
data_frame['Weight'] = data_frame['Dimensions'].str.extract(r'(?<=,)(.*?)(?:kg|oz| g)')
data_frame[['Dimensions', 'Weight_unit']] = data_frame['Dimensions'].str.split(pat=r'(?=kg)|(?= g )|(?=oz\.)', expand=True)

#DROP ITEMS WITH 4 DIMENSIONS
data_frame.drop(data_frame.loc[data_frame['Dimensions'].str.count('×')>2].index, inplace=True)

#TURN ' INTO 'inch'
data_frame['Dimensions']= data_frame['Dimensions'].str.replace('\'', 'in.')

#REMOVE INVENTORY NUMBERS FROM DIMENSIONS
data_frame['Dimensions']= data_frame['Dimensions'].str.replace('1934.490', '')
data_frame['Dimensions']= data_frame['Dimensions'].str.replace('1933.452', '')

#SPLIT DIMENSIONS
data_frame[['Dimensions', 'Dimensions_unit']] = data_frame['Dimensions'].str.split(pat=r'(?=in\.)|(?=cm)', expand=True, n=1)
data_frame.loc[data_frame['Dimensions_unit'].str.contains('in\.', na=False), 'Dimensions_unit']='inch'
data_frame.loc[data_frame['Dimensions_unit'].str.contains('cm', na=False), 'Dimensions_unit']='centimeter'

data_frame[['Height', 'Width', 'Depth']] = data_frame['Dimensions'].str.split(pat='×', expand=True, n=2)
data_frame['Height']=data_frame['Height'].str.replace('in.', '', regex=False)
data_frame['Height']=data_frame['Height'].str.replace('cm', '', regex=False)
data_frame['Width']=data_frame['Width'].str.replace('in.', '', regex=False)
data_frame['Width']=data_frame['Width'].str.replace('cm', '', regex=False)
data_frame['Depth']=data_frame['Depth'].str.replace('in.', '', regex=False)
data_frame['Depth']=data_frame['Depth'].str.replace('cm', '', regex=False)

#CONVERT FRACTIONS TO INTEGERS
def number(row):
    for item in row:
        if '/' in row:
            left, right = row.split()
            left, right = eval(left), eval(right)
            return left + right
def fraction(row):
    for item in row:
        if '/' in row:
            return eval(row)
data_frame.loc[data_frame['Height'].str.contains(r'[0-9] [0-9]', na=False), 'Height']=data_frame.loc[data_frame['Height'].str.contains(r'[0-9] [0-9]', na=False), 'Height'].apply(lambda x: number(x))
data_frame.loc[data_frame['Height'].str.contains('/', na=False), 'Height']=data_frame.loc[data_frame['Height'].str.contains('/', na=False), 'Height'].apply(lambda x: eval(x))

data_frame.loc[data_frame['Width'].str.contains(r'[0-9] [0-9]', na=False), 'Width']=data_frame.loc[data_frame['Width'].str.contains(r'[0-9] [0-9]', na=False), 'Width'].apply(lambda x: number(x))
data_frame.loc[data_frame['Width'].str.contains('/', na=False), 'Width']=data_frame.loc[data_frame['Width'].str.contains('/', na=False), 'Width'].apply(lambda x: fraction(x))

data_frame.loc[data_frame['Depth'].str.contains(r'[0-9] [0-9]', na=False), 'Depth']=data_frame.loc[data_frame['Depth'].str.contains(r'[0-9] [0-9]', na=False), 'Depth'].apply(lambda x: number(x))
data_frame.loc[data_frame['Depth'].str.contains('/', na=False), 'Depth']=data_frame.loc[data_frame['Depth'].str.contains('/', na=False), 'Depth'].apply(lambda x: fraction(x))

#REMOVE NAN EXPRESSSIONS
data_frame['Height'] = data_frame['Height'].astype(str)
data_frame['Width'] = data_frame['Width'].astype(str)
data_frame['Depth'] = data_frame['Depth'].astype(str)
data_frame['Height'] = data_frame['Height'].str.replace('nan', '')
data_frame['Width'] = data_frame['Width'].str.replace('None', '')
data_frame['Depth'] = data_frame['Depth'].str.replace('None', '')

#SPELLING: ADD WHITE SPACE TO JOINED WORDS, CORRECT MISSPELLINGS
data_frame['Title'] = data_frame['Title'].str.replace(r"(\.)([A-Z])", r"\1 \2").str.strip() 
data_frame['Title'] = data_frame['Title'].str.replace('  ', ' ')
data_frame['Title'] = data_frame['Title'].str.replace('- ', '-', regex=False)
data_frame['Title'] = data_frame['Title'].str.replace('( ', '(', regex=False)


data_frame['Title']=data_frame['Title'].str.replace('graffitt', 'grafitt')
data_frame['Title']=data_frame['Title'].str.replace('carnelain', 'carnelian')
data_frame['Title']=data_frame['Title'].str.replace('arowehead', 'arrowhead')
data_frame['Title']=data_frame['Title'].str.replace('Arrrowhead', 'arrowhead')
data_frame['Title']=data_frame['Title'].str.replace('arowhead', 'arrowhead')
data_frame['Title']=data_frame['Title'].str.replace('arrowehead', 'arrowhead')
data_frame['Title']=data_frame['Title'].str.replace('arrow head', 'arrowhead')
data_frame['Title']=data_frame['Title'].str.replace('arrow shaft', 'arrowshaft')
data_frame['Title']=data_frame['Title'].str.replace('phyrgian', 'phrygian')
data_frame['Title']=data_frame['Title'].str.replace('Haltera', 'Halter')
data_frame['Title']=data_frame['Title'].str.replace('of a negro head', 'of an African male head')
data_frame['Title']=data_frame['Title'].str.replace('Curiass', 'Cuirass')
data_frame['Title']=data_frame['Title'].str.replace('Trunkated', 'truncated')
data_frame['Title']=data_frame['Title'].str.replace('sdie', 'side')
data_frame['Title']=data_frame['Title'].str.replace('Commoneware', 'Commonware')
data_frame['Title']=data_frame['Title'].str.replace('Triuncated', 'Truncated')
data_frame['Title']=data_frame['Title'].str.replace('Sabbard', 'Scabbard')
data_frame['Title']=data_frame['Title'].str.replace('Bridal', 'bridle')
data_frame['Title']=data_frame['Title'].str.replace('Perorated', 'Perforated')
data_frame['Title']=data_frame['Title'].str.replace('Depinto', 'Dipinto')
data_frame['Title']=data_frame['Title'].str.replace('Rount', 'Round')
data_frame['Title']=data_frame['Title'].str.replace('Herakles', 'Heracles')
data_frame['Title']=data_frame['Title'].str.replace('(Frag\.?)(?![a-z])', 'fragment')
data_frame['Title']=data_frame['Title'].str.replace('framents', 'fragment')
data_frame['Title']=data_frame['Title'].str.replace('(frag\.?)(?![a-z])', 'fragment')
data_frame['Title']=data_frame['Title'].str.replace('Frac\.', 'fragment')
data_frame['Title']=data_frame['Title'].str.replace('Br\.', 'bronze')


#NORMALISE WORDS: CONVERT PLURAL TO SINGULAR
data_frame['stuff']=data_frame['Title'].str.lower()
data_frame['stuff']=data_frame['stuff'].str.replace('styli', 'stylus')
data_frame['stuff']=data_frame['stuff'].str.replace('tunica','tunic')
data_frame['stuff']=data_frame['stuff'].str.replace('mould','mold')
data_frame['stuff']=data_frame['stuff'].str.replace('molds','mold')
data_frame['stuff']=data_frame['stuff'].str.replace('stamps','stamp')
data_frame['stuff']=data_frame['stuff'].str.replace('stamping','stamp')
data_frame['stuff']=data_frame['stuff'].str.replace('stamped','stamp')
data_frame['stuff']=data_frame['stuff'].str.replace('vases','vase')
data_frame['stuff']=data_frame['stuff'].str.replace('bread stamp','bread_stamp')

data_frame['stuff']=data_frame['stuff'].str.replace('fragments', 'fragment')
data_frame['stuff']=data_frame['stuff'].str.replace('(?<![a-z])(die)(?![a-z])', 'dice')

data_frame['stuff']=data_frame['stuff'].str.replace('blades', 'blade')
data_frame['stuff']=data_frame['stuff'].str.replace('spatulas', 'spatula')
data_frame['stuff']=data_frame['stuff'].str.replace('arrows', 'arrow')
data_frame['stuff']=data_frame['stuff'].str.replace('sherds', 'sherd')
data_frame['stuff']=data_frame['stuff'].str.replace('beads', 'bead')
data_frame['stuff']=data_frame['stuff'].str.replace('ostraca', 'ostracon')
data_frame['stuff']=data_frame['stuff'].str.replace('handles', 'handle')
data_frame['stuff']=data_frame['stuff'].str.replace('horns', 'horn')
data_frame['stuff']=data_frame['stuff'].str.replace('tusks', 'tusk')
data_frame['stuff']=data_frame['stuff'].str.replace('buttons', 'button')
data_frame['stuff']=data_frame['stuff'].str.replace('bottoms', 'bottom')
data_frame['stuff']=data_frame['stuff'].str.replace('bottles', 'bottle')
data_frame['stuff']=data_frame['stuff'].str.replace('balsamaria', 'balsamarium')
data_frame['stuff']=data_frame['stuff'].str.replace('needles', 'needle')
data_frame['stuff']=data_frame['stuff'].str.replace('links', 'link')
data_frame['stuff']=data_frame['stuff'].str.replace('rings', 'ring')
data_frame['stuff']=data_frame['stuff'].str.replace('finger ring', 'finger_ring')
data_frame['stuff']=data_frame['stuff'].str.replace('hair ring', 'hair_ring')
data_frame['stuff']=data_frame['stuff'].str.replace('vessels', 'vessel')
data_frame['stuff']=data_frame['stuff'].str.replace('nails', 'nail')
data_frame['stuff']=data_frame['stuff'].str.replace('pegs', 'peg')
data_frame['stuff']=data_frame['stuff'].str.replace('pendants', 'pendant')
data_frame['stuff']=data_frame['stuff'].str.replace('ornaments', 'ornament')
data_frame['stuff']=data_frame['stuff'].str.replace('counters', 'counter')
data_frame['stuff']=data_frame['stuff'].str.replace('fibulas', 'fibula')
data_frame['stuff']=data_frame['stuff'].str.replace('gold threads', 'gold_thread')
data_frame['stuff']=data_frame['stuff'].str.replace('bull head', 'bull_head')
data_frame['stuff']=data_frame['stuff'].str.replace('jugs', 'jug')
data_frame['stuff']=data_frame['stuff'].str.replace('figurines', 'figurine')
data_frame['stuff']=data_frame['stuff'].str.replace('with rod', 'with_rod')
data_frame['stuff']=data_frame['stuff'].str.replace('lids', 'lid')
data_frame['stuff']=data_frame['stuff'].str.replace('pots', 'pot')
data_frame['stuff']=data_frame['stuff'].str.replace('stands', 'stand')
data_frame['stuff']=data_frame['stuff'].str.replace('sets', 'set')
data_frame['stuff']=data_frame['stuff'].str.replace('doves', 'dove')
data_frame['stuff']=data_frame['stuff'].str.replace('rivets', 'rivet')
data_frame['stuff']=data_frame['stuff'].str.replace('hippo-shoe', 'horseshoe', regex=False)
data_frame['stuff']=data_frame['stuff'].str.replace('lamps', 'lamp')
data_frame['stuff']=data_frame['stuff'].str.replace('pegs', 'peg')
data_frame['stuff']=data_frame['stuff'].str.replace('tacks', 'tack')
data_frame['stuff']=data_frame['stuff'].str.replace('shells', 'shell')
data_frame['stuff']=data_frame['stuff'].str.replace('barrel-shaped', 'barrel')
data_frame['stuff']=data_frame['stuff'].str.replace('oval-shaped', 'oval')
data_frame['stuff']=data_frame['stuff'].str.replace('beardless head', 'beardless_head')
data_frame['stuff']=data_frame['stuff'].str.replace('spear-tip', 'spear tip')
data_frame['stuff']=data_frame['stuff'].str.replace('oddments', 'fragment')
data_frame['stuff']=data_frame['stuff'].str.replace('spear-tip', 'spear point')
data_frame['stuff']=data_frame['stuff'].str.replace('guard-hilt', 'guard hilt')
data_frame['stuff']=data_frame['stuff'].str.replace('pot stand', 'pot_stand')
data_frame['stuff']=data_frame['stuff'].str.replace('circulular well', 'well (container)')
data_frame['stuff']=data_frame['stuff'].str.replace('spearhead', 'spear head')
data_frame['stuff']=data_frame['stuff'].str.replace('ram\s head', 'ram\'s_head')
data_frame['stuff']=data_frame['stuff'].str.replace('spear-point', 'spear point')
data_frame['stuff']=data_frame['stuff'].str.replace('ring shaped', 'ring-shaped')
data_frame['stuff']=data_frame['stuff'].str.replace('with loop', 'with_loop')

data_frame['stuff']=data_frame['stuff'].str.replace('bone perforated', 'perforated bone')
data_frame['stuff']=data_frame['stuff'].str.replace('bone tubular', 'tubular bone')


data_frame['stuff']=data_frame['stuff'].str.replace('.', '', regex=False)
data_frame['stuff']=data_frame['stuff'].str.replace(';', '')
data_frame['stuff']=data_frame['stuff'].str.replace(':', '')
data_frame['stuff']=data_frame['stuff'].str.replace('"', '')

#NULL MEDIUM VALUES--extract from Title
medium=['glass', 'iron', 'agate', 'wood', 'textile', 'terracotta', 'shell', 'bark','bronze','silver','copper alloy', 'stone', 'plaster'] 
def material(column):
    res=[]
    for item in medium:
        if item in column:
            res.extend([item])
    new = ','.join(res)
    return new
pat=rf"\b(?:{'|'.join(medium)})\b"
data_frame.loc[(data_frame['Medium'].isnull()) & (data_frame['stuff'].str.contains('zone')==False) & (data_frame['stuff'].str.findall(pat)), 'Medium']=data_frame.loc[(data_frame['Medium'].isnull()) & (data_frame['stuff'].str.contains('zone')==False) & (data_frame['stuff'].str.findall(pat)), 'stuff'].apply(lambda x: material(x))
data_frame['Medium'] = data_frame['Medium'].astype(str)
data_frame['Medium'] = data_frame['Medium'].str.replace('nan', '', regex=True)

#DISAMBIGUATION (e.g. box of from box)
data_frame['stuff']=data_frame['stuff'].str.replace('box of', 'box_of')
data_frame['stuff']=data_frame['stuff'].str.replace('bag of', 'bag_of')
data_frame['stuff']=data_frame['stuff'].str.replace('bits of', 'bits_of')
data_frame['stuff']=data_frame['stuff'].str.replace('drinking glass', 'drinking_glass')

#Create "Instance of", "Depicts", "Dedication", "Named", "Execution" 
Instances = ['cord','hammer', 'peg','gold leaf','shovel','harness','bit','longsword','glass set','inlay','refractor','plaque','halter','stick','writing tool','bark','block','pot_stand','stand','water_jar','lid','finial','drainage_pipe','statue_niche','sword','arrowhead','arrowshaft','brittle_ware','arrow','hair_ring','funerary_stele','funerary_inscription','earthenware','spool','plaster','signet_ring','goblet','wheel_hub','awl','plate_join','tab','ring_key','socket','fastening catch','rivet','beaker','engagement_ring','weight','loom_weight','strap_terminal','cast','mouth_piece', 'blackware','blade','knife_blade','sword_blade','tab','strap_mount','spindle_wheel','spindle_whorl','lamp', 'cork','pestle', 'rod', 'spear','bullet','juglet', 'peestle', 'ostracon', 'bolt', 'drinking_glass', 'plate','finger_ring', 'necklace', 'ring', 'spike', 'hasp', 'tripod', 'lance', 'ingot', 'drapery', 'fish_mandible', 'standard bearer', 'wall_painting', 'stopper', 'stud', 'tack', 'horseshoe_pendant', 'bead', 'jar', 'brick', 'scabbard', 'chape', 'patera', 'pouch', 'strainer', 'gold_thread', 'pyxis', 'slab', 'slide', 'stylus', 'textile', 'mask', 'relief', 'altar', 'tapestry', 'bottle','water bottle', 'box', 'trunk', 'loop', 'board', 'nail', 'shield','horn', 'tusk', 'altarette', 'scales', 'toilet instrument', 'disk', 'basket', 'basketry', 'dagger', 'vessel', 'hinge', 'phalara', 'phalaron', 'clapper', 'comb', 'stele', 'signet', 'spoke', 'amulet', 'boss', 'ware', 'chain', 'chain_link','cabochon', 'ball', 'scutum', 'unguentarium', 'balsamarium', 'brooch','coin', 'dart', 'clasp', 'trepon', 'cylinder', 'commonware', 'rope', 'beam', 'bridle_mount', 'doll','doll_pedestal', 'dome', 'patter', 'theriomorph', 'wheel', 'bell', 'bowl', 'needle', 'knob', 'plumb', 'fibula', 'hook', 'aryballos', 'spoon', 'wall', 'fresco', 'frieze', 'graffiti', 'graffito', 'mirror', 'figurine', 'statue', 'statuette', 'seat', 'furniture', 'gemstone', 'jewel', 'earring', 'pin', 'flute', 'saw', 'cup', 'pendant', 'spatula', 'locket', 'funnel', 'cloth', 'boot', 'bracelet', 'pedestal', 'tweezers', 'saucer', 'ward', 'counter', 'bobbin', 'ostrich', 'pilgrim’s flask', 'flask', 'helmet', 'sandal', 'thymiaterion', 'applique', 'oinochoe', 'medallion', 'weapon', 'caltrop', 'knife', 'key', 'bread_stamp', 'carding_board', 'tesserae', 'dish', 'tile', 'vase', 'nursing_bottle', 'strigil', 'palette', 'catapult ball', 'catapult stone', 'pot', 'scraper', 'column capital', 'cornice', 'tube', 'cuirass', 'bow', 'crossbow', 'vial', 'fish_hook', 'perforator', 'pitcher', 'hanger', 'tablet', 'hoe', 'skewer', 'ornament', 'visor', 'bag', 'dice', 'tray', 'sleeve', 'bodkin', 'cauldron', 'pipe', 'container', 'lentil', 'patella', 'seal', 'garment', 'utensil', 'sculpture', 'krater', 'redware', 'grayware', 'holder', 'baldric', 'alabastron', 'needle_book', 'tool', 'umbo', 'coffin', 'tureen', 'tunic', 'intaglio', 'hairpin', 'ballistic', 'funerary', 'cuisse', 'chainmail', 'lorica', 'shell', 'screen', 'buckle', 'curl', 'wire', 'quiver', 'stake', 'circlet', 'pile', 'scalpel', 'axe', 'spindle', 'armor', 'lancet', 'link', 'gourd', 'pottery', 'urn', 'bust', 'dipinto', 'button', 'shoe', 'horseshoe', 'flint', 'kettle', 'skeleton', 'amphora', 'case', 'quarrel', 'mantle', 'carafe', 'guard-hilt', 'olive_branch', 'inkwell','well (container)', 'disc', 'epiphysis', 'lantern', 'shrine', 'string', 'jug']
Depicts = ['nike','female figure','rose', 'oranges','parthian figure','torch','draped female','pegasus','reclining_figure','beardless_head', 'ram\'s_head','bull_head', 'sacrifice', 'zeus', 'horse\'s head', 'bull', 'tauroctony', 'dog\'s head', 'male head', 'female head', 'camel\'s head', 'bull\'s head', 'zeus_kyrios-baalshamin', 'scarab', 'zeus_megistos', 'heracles', 'mithras', 'gazelle', 'bird', 'silenus', 'horse', 'good_shepherd', 'adam_and_eve', 'avtenius_artemis', 'hermes', 'palmyrene_child', 'christ_walking_on_water', 'amazonomachy', 'hand', 'parthian head', 'tripartite hairdo', 'eagle', 'ram’s_head', 'sketch_of_man', 'man', 'torso', 'banquet_scene', 'nemesis', 'goddess', 'woman', 'woman_at_the_well', 'cock', 'peacock' 'pegasus', 'iliad', 'arsu', 'atargatis', 'hadad', 'tyche', 'dove', 'horseman', 'aphrodite', 'erotes', 'face', 'female_face', 'male', 'male_face', 'hyena', 'clibanarius', 'snake', 'nemean_lion','lion','mythological_scene', 'camel', 'cavalry', 'animal', 'christ_healing_the_paralytic', 'sun', 'wreath', 'nimbate', 'nude', 'heliodoros_actuarius', 'club', 'bacchic_head', 'fish', 'rider', 'bearded_god', 'bearded_man', 'sea monster','serpent','deer', 'grapes', 'athena', 'sacrifice', 'sprigs', 'pine cones', 'swastika', 'centaur', 'nebo', 'diana', 'capricorn', 'warrior', 'human_face', 'leopard', 'rooster', 'gad_(fortune)', 'pomegranates', 'leaves', 'sheaves', 'iarhibol', 'cherub', 'pig']
Part_of = ['baptistery', 'Mithraeum']
Dedication=['to_zeus','to_zeus_soter', 'aphlad', 'to_artemis', 'to_turmasgade', 'to_artemis_azzanathkona', 'to_the_gods_of_palmyra', 'to_the_god_mithras']
Named=['julius terentius', 'julia domna', 'bouraidis']
Execution=['gardrooned', 'perforated', 'granulated', 'pitted', 'inscribed', 'marvered', 'hollowed', 'stitched', 'welded', 'unfused', 'imprinted', 'glazed', 'green-glazed', 'unglazed', 'embossed', 'pillar-molded', 'cuirassed', 'incised', 'janiform', 'barbed', 'bevelled', 'scalloped', 'enameled', 'burnished', 'engraved', 'stapled', 'corrugated', 'angled', 'blown', 'striated', 'ribbed', 'fin', 'pinched', 'vented', 'tipped']
Decoration=['trefoil', 'crowning', 'stamp', 'filigree-type']
Shape=['melon','lunate','globular','curved','socketed','tubular','flat','tabular', 'oval', 'barrel','conical','round','flat','tube','concave','convex','spherical','fusiform','cylindrical','lenticular','circular','bicone','oblate','rectangular'] 
State=['frag.', 'fragment', 'corroded', 'damaged', 'smashed']
Language=['latin', 'greek', 'aramaic']
Part=['hilt','cover','frame','foot', 'decoration','pommel','shaft', 'cap','neck','clip','tang','top','sherd','fastener','end','bottom', 'rim', 'side', 'handle', 'spout', 'base', 'shoulder', 'nozzle', 'mouth', 'tip', 'point']
Contains=['rivet','shank', 'vanes', 'inscription', 'gadget', 'acrostic', 'epitaph']
From= ['halebiyeh']

#DEALING WITH COLLOCATIONS//BIGRAMS
data_frame['stuff']=data_frame['stuff'].str.replace('chain mail', 'chainmail')
data_frame['stuff']=data_frame['stuff'].str.replace('zeus soter', 'zeus_soter')
data_frame['stuff']=data_frame['stuff'].str.replace('Zeus kyrios-baalshamin', 'zeus_kyrios-baalshamin')
data_frame['stuff']=data_frame['stuff'].str.replace('zeus megistos', 'zeus_megistos')
data_frame['stuff']=data_frame['stuff'].str.replace('good shepherd', 'good_shepherd')
data_frame['stuff']=data_frame['stuff'].str.replace('adam and eve', 'adam_and_steve')
data_frame['stuff']=data_frame['stuff'].str.replace('avtenius \(artemis\)', 'avtenius_artemis')
data_frame['stuff']=data_frame['stuff'].str.replace('palmyrene child', 'palmyrene_child')
data_frame['stuff']=data_frame['stuff'].str.replace('zeus kyrios-baalshamin', 'zeus_kyrios-baalshamin')
data_frame['stuff']=data_frame['stuff'].str.replace('zeus megistos', 'zeus_megistos')
data_frame['stuff']=data_frame['stuff'].str.replace('christ walking on water', 'christ_walking_on_water')
data_frame['stuff']=data_frame['stuff'].str.replace('zeus soter', 'zeus_soter')
data_frame['stuff']=data_frame['stuff'].str.replace('banquet scene', 'banquet_scene')
data_frame['stuff']=data_frame['stuff'].str.replace('woman at the well', 'woman_at_the_well')
data_frame['stuff']=data_frame['stuff'].str.replace('scenes from iliad', 'iliad')
data_frame['stuff']=data_frame['stuff'].str.replace('nemean lion', 'nemean_lion')
data_frame['stuff']=data_frame['stuff'].str.replace('water jar', 'water_jar')
data_frame['stuff']=data_frame['stuff'].str.replace('mythological scene', 'mythological_scene')
data_frame['stuff']=data_frame['stuff'].str.replace('christ healing the paralytic', 'christ_healing_the_paralytic')
data_frame['stuff']=data_frame['stuff'].str.replace('heliodoros, an actuarius', 'heliodoros_actuarius')
data_frame['stuff']=data_frame['stuff'].str.replace('bacchic head', 'bacchic_head')
data_frame['stuff']=data_frame['stuff'].str.replace('bearded man', 'bearded_man')
data_frame['stuff']=data_frame['stuff'].str.replace('bearded god', 'bearded_god')
data_frame['stuff']=data_frame['stuff'].str.replace('sprigs and pincones', 'sprigs, pinecones')
data_frame['stuff']=data_frame['stuff'].str.replace('chain-link', 'chain_link')
data_frame['stuff']=data_frame['stuff'].str.replace('chain link', 'chain_link')
data_frame['stuff']=data_frame['stuff'].str.replace('human face', 'human_face')
data_frame['stuff']=data_frame['stuff'].str.replace('votive tablet', 'votive_tablet')
data_frame['stuff']=data_frame['stuff'].str.replace('female face', 'female_face')
data_frame['stuff']=data_frame['stuff'].str.replace('male face', 'male_face')
data_frame['stuff']=data_frame['stuff'].str.replace('doll pedestal', 'doll_pedestal')
data_frame['stuff']=data_frame['stuff'].str.replace('doll\'s', 'doll')

data_frame['stuff']=data_frame['stuff'].str.replace(r'(doll.*?(head|arm))', r'\1 fragment')

data_frame['stuff']=data_frame['stuff'].str.replace('funerary stele', 'funerary_stele')
data_frame['stuff']=data_frame['stuff'].str.replace('funerary inscription', 'funerary_inscription')
data_frame['stuff']=data_frame['stuff'].str.replace('strap terminal', 'strap_terminal')
data_frame['stuff']=data_frame['stuff'].str.replace('loom weight', 'loom_weight')
data_frame['stuff']=data_frame['stuff'].str.replace('gad (fortune)', 'gad_\(fortune\)')

data_frame['stuff']=data_frame['stuff'].str.replace('to zeus', 'to_zeus')
data_frame['stuff']=data_frame['stuff'].str.replace('to artemis', 'to_artemis')
data_frame['stuff']=data_frame['stuff'].str.replace('to turmasgade', 'to_turmasgade')
data_frame['stuff']=data_frame['stuff'].str.replace('to the gods of palmyra', 'to_the_gods_of_palmyra')
data_frame['stuff']=data_frame['stuff'].str.replace('to the god mithras', 'to_the_god_mithras')

data_frame['stuff']=data_frame['stuff'].str.replace('toilet instrument', 'toilet_instrument')
data_frame['stuff']=data_frame['stuff'].str.replace('niche for statue', 'statue_niche')
data_frame['stuff']=data_frame['stuff'].str.replace('horseshoe pendant', 'horseshoe_pendant')
data_frame['stuff']=data_frame['stuff'].str.replace('bridle mount', 'bridle_mount')
data_frame['stuff']=data_frame['stuff'].str.replace("pilgrim's flask", "pilgrim's_flask")
data_frame['stuff']=data_frame['stuff'].str.replace('carding board', 'carding_board')
data_frame['stuff']=data_frame['stuff'].str.replace('nursing bottle', 'nursing_bottle')
data_frame['stuff']=data_frame['stuff'].str.replace('fish mandible', 'fish_mandible')
data_frame['stuff']=data_frame['stuff'].str.replace('fish hook', 'fish_hook')
data_frame['stuff']=data_frame['stuff'].str.replace('needle book', 'needle_book')
data_frame['stuff']=data_frame['stuff'].str.replace('olive branch', 'olive_branch')
data_frame['stuff']=data_frame['stuff'].str.replace('mouth piece', 'mouth_piece')
data_frame['stuff']=data_frame['stuff'].str.replace('spindle whorl', 'spindle_whorl')
data_frame['stuff']=data_frame['stuff'].str.replace('spindle wheel', 'spindle_wheel')
data_frame['stuff']=data_frame['stuff'].str.replace('strap mount', 'strap_mount')
data_frame['stuff']=data_frame['stuff'].str.replace('sword blade', 'sword_blade')
data_frame['stuff']=data_frame['stuff'].str.replace('knife blade', 'knife_blade')
data_frame['stuff']=data_frame['stuff'].str.replace('cult relief', 'cult_relief')
data_frame['stuff']=data_frame['stuff'].str.replace('ring key', 'ring_key')
data_frame['stuff']=data_frame['stuff'].str.replace('signet ring', 'signet_ring')
data_frame['stuff']=data_frame['stuff'].str.replace('wheel hub', 'wheel_hub')
data_frame['stuff']=data_frame['stuff'].str.replace('drainage pipe', 'drainage_pipe')
data_frame['stuff']=data_frame['stuff'].str.replace('reclining figure', 'reclining_figure')
data_frame['stuff']=data_frame['stuff'].str.replace('engagement ring', 'engagement_ring')
data_frame['stuff']=data_frame['stuff'].str.replace('plate join', 'plate_join')
data_frame['stuff']=data_frame['stuff'].str.replace('Common ware', 'Commonware')
data_frame['stuff']=data_frame['stuff'].str.replace('brittle ware', 'brittle_ware')


data_frame['stuff']=data_frame['stuff'].str.replace('shape of an axe', 'shape_of_an_axe')
data_frame['stuff']=data_frame['stuff'].str.replace('wall painting', 'wall_painting')
data_frame['stuff']=data_frame['stuff'].str.replace('(nebo?)', 'nebo', regex=False)
data_frame['stuff']=data_frame['stuff'].str.replace('(zeus megistos?)', 'zeus_megistos', regex=False)

#REMOVE PUNCTUATION
data_frame['stuff']=data_frame['stuff'].str.replace('\(?\?\)?','')
data_frame['stuff']=data_frame['stuff'].str.replace('  ',' ')
data_frame['stuff'] = ' ' + data_frame['stuff'] + ' '

data_frame['stuff'] = data_frame['stuff'].str.replace(r'([a-z])(\?)', r'\1 \2')
data_frame['stuff'] = data_frame['stuff'].str.replace(r'([a-z])(\))', r'\1 \2')
data_frame['stuff'] = data_frame['stuff'].str.replace(r'(\()([a-z])', r'\1 \2')
data_frame['stuff'] = data_frame['stuff'].str.replace(r'([a-z])(\(\?\))', r'\1 \2')
data_frame['stuff'] = data_frame['stuff'].str.replace(r'([a-z])([,:;\.])', r'\1 \2')


Instances = [' {0} '.format(elem) for elem in Instances]
Dedication = [' {0} '.format(elem) for elem in Dedication]
Decoration = [' {0} '.format(elem) for elem in Decoration]
Depicts = [' {0} '.format(elem) for elem in Depicts]
Named = [' {0} '.format(elem) for elem in Named]
Execution = [' {0} '.format(elem) for elem in Execution]
State = [' {0} '.format(elem) for elem in State]
Part = [' {0} '.format(elem) for elem in Part]
Language = [' {0} '.format(elem) for elem in Language]
From = [' {0} '.format(elem) for elem in From]
Contains = [' {0} '.format(elem) for elem in Contains]

def insta(column):
    res=[]
    for item in Instances:
        if item in column:
            res.extend([item])
    new = ','.join(res)
    return new
data_frame['Instance']=data_frame['stuff'].apply(lambda x: insta(x))
data_frame['Instance'] = data_frame['Instance'].astype(str)
data_frame['Instance'] = data_frame['Instance'].str.replace('None', '', regex=True)
data_frame['Instance'] = data_frame['Instance'].str.replace('_', ' ')

def depicts(column):
    res=[]
    for item in Depicts:
        if item in column:
            res.extend([item])
    new = ','.join(res)
    return new
data_frame['Depicts']=data_frame['stuff'].apply(lambda x: depicts(x))
data_frame['Depicts'] = data_frame['Depicts'].astype(str)
data_frame['Depicts'] = data_frame['Depicts'].str.replace('None', '', regex=True)
data_frame['Depicts'] = data_frame['Depicts'].str.replace('_', ' ')

def Dedicated(column):
    res=[]
    for item in Dedication:
        if item in column:
            res.extend([item])
    new = ','.join(res)
    return new
data_frame['Dedication']=data_frame['stuff'].apply(lambda x: Dedicated(x))
data_frame['Dedication'] = data_frame['Dedication'].astype(str) 
data_frame['Dedication'] = data_frame['Dedication'].str.replace('None', '', regex=True)
data_frame['Dedication'] = data_frame['Dedication'].str.replace('_', ' ')
data_frame['Dedication'] = data_frame['Dedication'].str.replace('to', '')


def Naming(column):
    res=[]
    for item in Named:
        if item in column:
            res.extend([item])
    new = ','.join(res)
    return new
data_frame['Names']=data_frame['stuff'].apply(lambda x: Naming(x))
data_frame['Names'] = data_frame['Names'].astype(str) 
data_frame['Names'] = data_frame['Names'].str.replace('None', '', regex=True)

def sha(column):
    res=[]
    for item in Shape:
        if item in column:
            res.extend([item])
    new = ','.join(res)
    return new
data_frame['Shape']=data_frame['stuff'].apply(lambda x: sha(x))
data_frame['Shape'] = data_frame['Shape'].astype(str) 
data_frame['Shape'] = data_frame['Shape'].str.replace('None', '', regex=True)

def Exec(column):
    res=[]
    for item in Execution:
        if item in column:
            res.extend([item])
    new = ','.join(res)
    return new
data_frame['Execution']=data_frame['stuff'].apply(lambda x: Exec(x))
data_frame['Execution'] = data_frame['Execution'].astype(str) 
data_frame['Execution'] = data_frame['Execution'].str.replace('None', '', regex=True)


def Decorate(column):
    res=[]
    for item in Decoration:
        if item in column:
            res.extend([item])
    new = ','.join(res)
    return new
data_frame['Decoration']=data_frame['stuff'].apply(lambda x: Decorate(x))
data_frame['Decoration'] = data_frame['Decoration'].astype(str)
data_frame['Decoration'] = data_frame['Decoration'].str.replace('None', '', regex=True)

def sta(column):
    res=[]
    for item in State:
        if item in column:
            res.extend([item])
    new = ','.join(res)
    return new
data_frame['State']=data_frame['stuff'].apply(lambda x: sta(x))
data_frame['State'] = data_frame['State'].astype(str)
data_frame['State'] = data_frame['State'].str.replace('None', '', regex=True)

def lang(column):
    res=[]
    for item in Language:
        if item in column:
            res.extend([item])
    new = ','.join(res)
    return new
data_frame['Language']=data_frame['stuff'].apply(lambda x: lang(x))
data_frame['Language'] = data_frame['Language'].astype(str)
data_frame['Language'] = data_frame['Language'].str.replace('\[\'', '', regex=True)
data_frame['Language'] = data_frame['Language'].str.replace('\'\]', '', regex=True)
data_frame['Language'] = data_frame['Language'].str.replace('None', '', regex=True)

def cont(column):
    res=[]
    for item in Contains:
        if item in column:
            res.extend([item])
    new = ','.join(res)
    return new
data_frame['Contains']=data_frame['stuff'].apply(lambda x: cont(x))
data_frame['Contains'] = data_frame['Contains'].astype(str)
data_frame['Contains'] = data_frame['Contains'].str.replace('None', '', regex=True)

def geo(column):
    res=[]
    for item in From:
        if item in column:
            res.extend([item])
    new = ','.join(res)
    return new
data_frame['From']=data_frame['stuff'].apply(lambda x: geo(x))
data_frame['From'] = data_frame['From'].astype(str)
data_frame['From'] = data_frame['From'].str.replace('None', '', regex=True)

def part_of_(column):
    res=[]
    for item in Part_of:
        if item in column:
            res.extend([item])
    new = ','.join(res)
    return new
data_frame['Part_of']=data_frame['stuff'].apply(lambda x: part_of_(x))
data_frame['Part_of'] = data_frame['Part_of'].astype(str)
data_frame['Part_of'] = data_frame['Part_of'].str.replace('None', '', regex=True)

###HOW TO DEAL WITH PARTS, WITH, FRAGMENTS OF
def has(column):
    res=[]
    for item in Part:
        if item in column:
            res.extend([item])
    new = ','.join(res)
    return new
data_frame['Parts']=data_frame['stuff'].apply(lambda x: has(x))
data_frame['Parts'] = data_frame['Parts'].astype(str)
data_frame['Parts'] = data_frame['Parts'].str.replace('nan', '', regex=True)
pat = re.compile(rf"(?<=without)(?:{'|'.join(Part)})")
data_frame['stuff']=data_frame['stuff'].str.replace(pat,"") 

#Identify 
pat = regex.compile(rf"(?<!with.*?)(?:{'|'.join(Part)})")
def regex_contains(s, rx):
    return bool(rx.search(s))

data_frame['bool']=data_frame['stuff'].apply(regex_contains, args=(pat,))
                                      
data_frame.loc[(data_frame['stuff'].str.contains(rf"\((?:{'|'.join(Part)})")|(data_frame['stuff'].str.contains('(section)|(fragment)|(part)|(piece)|(half)'))|(data_frame['bool']==True)),'of']=data_frame.loc[(data_frame['stuff'].str.contains(rf"\((?:{'|'.join(Part)})")|(data_frame['stuff'].str.contains('(section)|(fragment)|(part)|(piece)|(half)'))|(data_frame['bool']==True)),'Instance']
data_frame.loc[(data_frame['stuff'].str.contains(rf"\((?:{'|'.join(Part)})")|(data_frame['stuff'].str.contains('(section)|(fragment)|(part)|(piece)|(half)'))|(data_frame['bool']==True)),'Instance']='fragment'
                                                
#MODELLING MOLDS
data_frame.loc[(data_frame['stuff'].str.contains(' mold ')), 'of'] = data_frame.loc[(data_frame['stuff'].str.contains(' mold ')), 'stuff'].str.findall(rf"({'|'.join(Instances)})")
data_frame['of']=data_frame['of'].astype(str)
data_frame['of']=data_frame['of'].str.replace('[\[\]\(\)\']','')
data_frame.loc[(data_frame['stuff'].str.contains(' mold ')), 'Instance'] = 'mold'

data_frame.loc[(data_frame['stuff'].str.contains(' mold '))&(data_frame['stuff'].str.contains('(fragment)|(part)|(piece)|(half)')), 'Instance']= data_frame.loc[(data_frame['stuff'].str.contains(' mold '))&(data_frame['stuff'].str.contains('(fragment)|(part)|(piece)|(half)')), 'Instance']+', fragment'
data_frame['of']=data_frame['of'].str.strip()

#DISAMBIGUATING SPEAR (DEPICTED VS. PART), HEAD, ARM, LEG
Class=r'^(Sculpture|Painting|Toy).*'
data_frame.loc[(data_frame['Classification'].str.contains(Class))&(data_frame['Instance'].str.contains('spear')), 'Instance']=data_frame.loc[(data_frame['Classification'].str.contains(Class))&(data_frame['Instance'].str.contains('spear')), 'Instance'].str.replace('spear','')
data_frame.loc[(data_frame['Classification'].str.contains(Class))&(data_frame['Instance'].str.contains('sword')), 'Instance']=data_frame.loc[(data_frame['Classification'].str.contains(Class))&(data_frame['Instance'].str.contains('sword')), 'Instance'].str.replace('sword','')

data_frame['Instance']=data_frame['Instance'].str.replace(r'^([ ,]*)([a-z])', r'\2')
Class=r'^(?!Sculpture|Painting|Toy).*'

pat=regex.compile(rf"^(?<!with.*)(?: leg )")
data_frame['bool']=data_frame['stuff'].apply(regex_contains, args=(pat,))

data_frame['stuff']=data_frame['stuff'].str.replace('legs','leg')
data_frame.loc[(data_frame['bool']==True)&(data_frame['Classification'].str.contains(Class)), 'of'] = data_frame.loc[(data_frame['bool']==True)&(data_frame['Classification'].str.contains(Class)), 'Instance']
data_frame.loc[(data_frame['bool']==True)&(data_frame['Classification'].str.contains(Class)), 'Instance'] = 'fragment'
data_frame.loc[(data_frame['bool']==True)&(data_frame['Classification'].str.contains(Class)), 'Parts'] = data_frame.loc[(data_frame['bool']==True)&(data_frame['Classification'].str.contains(Class)), 'Parts'] + ', leg'

pat=regex.compile(rf"^(?<!with.*)(?: head )")
data_frame['bool']=data_frame['stuff'].apply(regex_contains, args=(pat,))
data_frame.loc[(data_frame['bool']==True)&(data_frame['Classification'].str.contains(Class)), 'of'] = data_frame.loc[(data_frame['bool']==True)&(data_frame['Classification'].str.contains(Class)), 'Instance']
data_frame.loc[(data_frame['bool']==True)&(data_frame['Classification'].str.contains(Class)), 'Instance'] = 'fragment'
data_frame.loc[(data_frame['bool']==True)&(data_frame['Classification'].str.contains(Class)), 'Parts'] = data_frame.loc[(data_frame['bool']==True)&(data_frame['Classification'].str.contains(Class)), 'Parts'] + ', head'

pat=regex.compile(rf"^(?<!with.*)(?: arm )")
data_frame['bool']=data_frame['stuff'].apply(regex_contains, args=(pat,))
data_frame.loc[(data_frame['bool']==True)&(data_frame['Classification'].str.contains(Class)), 'of'] = data_frame.loc[(data_frame['bool']==True)&(data_frame['Classification'].str.contains(Class)), 'Instance']
data_frame.loc[(data_frame['bool']==True)&(data_frame['Classification'].str.contains(Class)), 'Instance'] = 'fragment'
data_frame.loc[(data_frame['bool']==True)&(data_frame['Classification'].str.contains(Class)), 'Parts'] = data_frame.loc[(data_frame['bool']==True)&(data_frame['Classification'].str.contains(Class)), 'Parts'] + ', arm'

Class=r'^(?:Sculpture|Paintings|Toys)'
data_frame.loc[(data_frame['stuff'].str.contains('head'))&(data_frame['Classification'].str.contains(Class)), 'Depicts'] = data_frame.loc[(data_frame['stuff'].str.contains('head'))&(data_frame['Classification'].str.contains(Class)), 'Depicts'] +', head'
data_frame.loc[(data_frame['stuff'].str.contains('arm(?![a-z])'))&(data_frame['Classification'].str.contains(Class)), 'Depicts'] = data_frame.loc[(data_frame['stuff'].str.contains('arm(?![a-z])'))&(data_frame['Classification'].str.contains(Class)), 'Depicts'] +', arm'
data_frame['Parts']=data_frame['Parts'].str.replace(r'^([ ,]*)([a-z])', r'\2')
data_frame['Depicts']=data_frame['Depicts'].str.replace(r'^([ ,]*)([a-z])', r'\2')

#How to deal with expressions like "figurine from a bowl"
pat = regex.compile(rf"(?<=from.*?)(?:{'|'.join(Instances)})")
data_frame['bool']=data_frame['stuff'].apply(regex_contains, args=(pat,))
data_frame.loc[(data_frame['bool']==True)&(data_frame['Instance'].str.contains('frag', na=False)==False), 'placeholder']=data_frame.loc[(data_frame['bool']==True)&(data_frame['Instance'].str.contains('frag', na=False)==False), 'stuff'].str.replace(r'.*?(?=from)','')
data_frame.loc[(data_frame['bool']==True)&(data_frame['Instance'].str.contains('frag', na=False)==False), 'of']=data_frame.loc[(data_frame['bool']==True)&(data_frame['Instance'].str.contains('frag', na=False)==False), 'placeholder'].str.findall(rf"({'|'.join(Instances)})")
data_frame['of']=data_frame['of'].astype(str)
data_frame['of']=data_frame['of'].str.replace('[\[\]\(\)\']','')

pat = re.compile(r"(.*?)(?=from)")
data_frame.loc[(data_frame['stuff'].str.contains(pat))&(data_frame['Instance'].str.contains('frag', na=False)==False), 'placeholder']=data_frame.loc[(data_frame['stuff'].str.contains(pat))&(data_frame['Instance'].str.contains('frag', na=False)==False), 'stuff'].str.replace(r'(?<=from).*','')
data_frame.loc[((data_frame['stuff'].str.contains(pat))&(data_frame['Instance'].str.contains('frag', na=False)==False)), 'Instance']=data_frame.loc[(data_frame['stuff'].str.contains(pat))&(data_frame['Instance'].str.contains('frag', na=False)==False), 'placeholder'].str.findall(rf"({'|'.join(Instances)})")
data_frame.loc[((data_frame['stuff'].str.contains(pat))&(data_frame['Instance'].str.contains('frag', na=False)==False)), 'Instance']=data_frame.loc[((data_frame['stuff'].str.contains(pat))&(data_frame['Instance'].str.contains('frag', na=False)==False)), 'Instance'].astype(str)

data_frame['of']=data_frame['of'].astype(str)
data_frame['of']=data_frame['of'].str.replace('[\[\]\(\)\']','')
data_frame['of']=data_frame['of'].str.replace('nan','')
data_frame['of']=data_frame['of'].str.replace(', ,',',')
data_frame['of']=data_frame['of'].str.replace('(, )$','')
data_frame['of']=data_frame['of'].str.strip()

data_frame['Instance']=data_frame['Instance'].astype(str)
data_frame['Instance']=data_frame['Instance'].str.replace('[\[\]\(\)\']','')
data_frame['Instance']=data_frame['Instance'].str.replace('nan','')
data_frame['Instance']=data_frame['Instance'].str.replace('(, )$','')
data_frame['Instance']=data_frame['Instance'].str.strip()

#REMOVE "INSTANCE OF" "FRAGMENT" "OF FRAGMENT"
data_frame.loc[data_frame['of'].str.contains('fragment', na=False), 'of']=data_frame.loc[data_frame['of'].str.contains('fragment', na=False), 'stuff'].str.findall(rf"({'|'.join(Instances)})")

data_frame['of']=data_frame['of'].astype(str)
data_frame['of']=data_frame['of'].str.replace('[\[\]\(\)\']','')
data_frame['of']=data_frame['of'].str.replace('nan','')
data_frame['of']=data_frame['of'].str.replace('(, ?)$','')
data_frame['of']=data_frame['of'].str.strip()

data_frame.loc[data_frame['stuff'].str.contains(r'(square )$'), 'Instance'] = 'square'
data_frame.loc[data_frame['stuff'].str.contains(r'(bone )$'), 'Instance'] = 'bone'
data_frame.loc[data_frame['stuff'].str.contains(r'(stone )$'), 'stone'] = 'bone'


#REFORMAT
data_frame['Dedication'] = data_frame['Dedication'].str.strip()
data_frame['Instance'] = data_frame['Instance'].str.strip()
data_frame['Depicts'] = data_frame['Depicts'].str.strip()
data_frame['Language'] = data_frame['Language'].str.strip()
data_frame['Parts'] = data_frame['Parts'].str.strip()
data_frame['State'] = data_frame['State'].str.strip()
data_frame['Decoration'] = data_frame['Decoration'].str.strip()
data_frame['Execution'] = data_frame['Execution'].str.strip()
data_frame['Names'] = data_frame['Names'].str.strip()
   
#PROVENANCE and SITE
data_frame['Site'] = data_frame['Provenance'].str.extract('(?<=\()(.*?)(?=\))')
data_frame['Provenance'] = 'Yale-French Excavations at Dura-Europos, present-day Syria, 1928–37; Yale University Art Gallery'

#CERTAINTY
data_frame['ItemCertainty'] = data_frame['Title'].apply(lambda x: 'possibly' if '?' in x else 'possibly' if ' or ' in x else 'possibly' if 'possibly' in x else 'possibly' if 'Possibly' in x else '')

#SUPPLY PLACEHOLDER DATE VALUE--DATE PRECISION
data_frame.loc[data_frame['Date'].isna(), 'Date']='somevalue'
data_frame['ObjectNumber'] = 'inv. ' + data_frame['ObjectNumber']

data_frame.loc[data_frame['Title'].str.contains('(\.)$'), 'Title']=data_frame.loc[data_frame['Title'].str.contains('(\.)$'), 'Title'].str.replace('(\.)$','')

#ADD IMAGE WEBSITE
assets.drop(['asset','format'],axis=1, inplace=True)
assets.drop_duplicates(subset=['ID'],keep='last', inplace=True)

data_frame = data_frame.merge(assets, on='ID', how='left')

#WRITE
data_frame.to_csv('/Users/kyleconrau-lewis/Google Drive/dura_europos/DuraEuropos_output.csv',index=False)
