import re
from unidecode import unidecode

print "\n\n"

months = {"janvier": 1, "fevrier": 2, "mars": 3, "avril": 4, "mai": 5, "juin": 6, "juillet": 7, "aout": 8, "septembre": 9, "octobre": 10, "novembre": 11, "decembre": 12}
all_pres_dates = {}
class Date(object):
    def __init__(self, year, month, day, ref, form, line):
        self.year = int(year)
        self.month = int(month)
        self.day = int(day)
        self.ref = ref
        self.form = form
        self.line = line

    def add_to_dict(self):
        if self.year in all_pres_dates:
            if self.month in all_pres_dates[self.year]:
                if self.day in all_pres_dates[self.year][self.month]:
                    all_pres_dates[self.year][self.month][self.day].append(self.ref)
                else:
                    all_pres_dates[self.year][self.month][self.day] = [self.ref]
            else:
                all_pres_dates[self.year][self.month] = {self.day:[]}
                all_pres_dates[self.year][self.month][self.day].append(self.ref)
        else:
            all_pres_dates[self.year] = {self.month:{self.day:[]}}
            all_pres_dates[self.year][self.month][self.day].append(self.ref)

#This is used to list the dates in order        
def date_sort():
    global all_pres_dates
    for date in dates:
        date.add_to_dict()
    all_pres_yrs = sorted(all_pres_dates)
    all_pres_months = {}
    all_pres_days = {}
    for year_1 in all_pres_yrs:
        all_pres_months = sorted(all_pres_dates[year_1])
        for month_1 in all_pres_months:
            all_pres_days = sorted(all_pres_dates[year_1][month_1])
            for day_1 in all_pres_days:
                for entry in all_pres_dates[year_1][month_1][day_1]:
                    print "%s/%s/%s: %s" % (day_1, month_1, year_1, entry)
    all_pres_dates = {}

#Used later to change other dates in reference to split_code
def encode_other_dates(date):
    for other_date in dates:
        date.ref = re.sub(other_date.form, "split_code", date.ref)
        date.line = re.sub(other_date.form, "split_code", date.line)
def remove_obsolete_words(date):
    for item in ["date_code0", "split_code"]:
        for word in ["en ", "le ", "depuis "]:
            date.ref = re.sub(word+item, item, date.ref)
            date.line = re.sub(word+item, item, date.line)
def clean_date(date):
    if date.ref != None:
        date.ref = re.sub("endline_code", "", date.ref)
        date.ref = re.sub("date_code0", "", date.ref)
        date.ref = re.sub("split_code", "", date.ref)
        date.ref = re.sub("^(\W+)", "", date.ref)
            
filename = raw_input("Please enter the file you wish to scan, with the extension (e.g. \".txt\"): ")
print "\n"
with open(filename, "r+") as f: #This line sets which file to open
    i = 0
    num_of_lines = 0
    file = " "
    lines = []
  
    while i < 1:
        line = unidecode(str(f.readline()).strip().decode(encoding='UTF-8',errors='ignore'))
        if filter(lambda x: x!= " ", line) == "":
            i += 1
        lines.append(line)
        line = line + "endline_code "
        num_of_lines += 1
        file = file + line
        


dated_lines = {}
dated_lines2 = {}

#This part attempts to find dates using regexes

#This creates all the regex strings used to identify dates
month_year_str = "janvier\W[0-9]{2,4}"
day_month_year_str = "[0-9]{1,2}\sjanvier\W[0-9]{2,4}"
for key in months:
    month_year_str = month_year_str + "|%s\W[0-9]{2,4}" % key
    day_month_year_str = day_month_year_str + "|[0-9]{1,2}\s%s\W[0-9]{2,4}" % key
dd_mm_yy_str = '([0-9]{1,2})\W([0-9]{1,2})\W([0-9]{2,4})'
mm_yy_yy_str = '([0-9]{1,2})\W([0-9]{2,4})'
yy_yy_str = '([0-9]{4})'
gen_reg_str = re.sub("\(|\)", "", "%s|%s|%s|%s|%s" % (dd_mm_yy_str, mm_yy_yy_str, yy_yy_str, day_month_year_str, month_year_str))

#This compiles the regex patterns

dd_mm_yy = re.compile(dd_mm_yy_str)
mm_yy_yy = re.compile(mm_yy_yy_str)
day_month_year = re.compile(day_month_year_str, re.IGNORECASE)
month_year = re.compile(month_year_str, re.IGNORECASE)
yy_yy = re.compile(yy_yy_str)
p = re.compile(gen_reg_str, re.IGNORECASE|re.UNICODE)

#This searches each line for dates and adds 'date:line' entries to a dictionary

for line in lines:
    if p.findall(line) != []:
        for date in p.findall(line):
            dated_lines[date] = re.sub(r'%s' % date, "date_code0", file)
            dated_lines2[date] = re.sub(r'%s' % date, "date_code0", line)

dates = []
i = 0
for date_1 in dated_lines:
    dates.insert(i, date_1)
#Checks if date is in the day_month_year format and if so reads out day month year
    if re.match(day_month_year, date_1) != None:
        for month_1 in months:
            match = re.match(r'([0-9]{1,2})\s(%s)\W([0-9]{2,4})' % month_1, date_1, re.IGNORECASE)
            if match != None:
                dates[i] = Date(match.group(3), months[month_1], match.group(1), dated_lines[dates[i]], date_1, dated_lines2[dates[i]])
#Checks if date is in the month_year format, and if so reads out month and year
    if re.match(month_year, date_1) != None:
        for month_1 in months:
            match = re.match(r'(%s)\W([0-9]{2,4})' % month_1, date_1, re.IGNORECASE) 
            if match != None:
                dates[i] = Date(match.group(2), months[month_1], 0, dated_lines[dates[i]], date_1, dated_lines2[dates[i]])
#Checks if date is in the dd_mm_yy format, and if so reads out day, month and year
    elif re.match(dd_mm_yy, date_1) != None:
        match = dd_mm_yy.search(date_1)
        dates[i] = Date(match.group(3), match.group(2), match.group(1), dated_lines[dates[i]], date_1, dated_lines2[dates[i]])
#Checks if date is in the mm_yy_yy format, and if so reads out month and year               
    elif re.match(mm_yy_yy, date_1) != None:
        match = mm_yy_yy.search(date_1)
        dates[i] = Date(match.group(2), match.group(1), 0, dated_lines[dates[i]], date_1, dated_lines2[dates[i]])
#Checks if date is in the yy_yy format, and if so reads out year
    elif re.match(yy_yy, date_1) != None:
        match = yy_yy.search(date_1)
        dates[i] = Date(match.group(1), 0, 0, dated_lines[dates[i]], date_1, dated_lines2[dates[i]])
    i += 1

#Here, add a set of filters to remove dates that aren't actually dates
dates = [date for date in dates if re.search("Gleason date_code0", date.ref) == None]
dates = [date for date in dates if re.match("[0-9]{2}\.[0-9]{2}", date.form) == None or re.match("[0-9]{2}\.[0-9]{4}", date.form) != None]
for date in dates:
    for other_date in dates:
        if re.search("date_code0 au %s" % other_date.form, date.ref) != None:
            other_date.year = 99999
dates = [date for date in dates if date.year != 99999]


for date in dates:
    encode_other_dates(date)
    remove_obsolete_words(date)
    date.ref = re.sub("(?<=-)(.(?!split_code|-))+.split_code\)", "split_code", date.ref)
    date.line = re.sub("(?<=-)(.(?!split_code|-))+.split_code\)", "split_code", date.line)

    #Selects info to grab
for date in dates:
    line_splitter = re.search(r"(?<=date_code0)(.(?!split_code))+", date.ref, re.DOTALL)
    other_date_search = re.search("split_code", date.line)
    before_date_search = re.search("(?<=-)(.(?!date_code0|-))+.date_code0\)", date.ref, re.DOTALL)
    if other_date_search == None:
        date.ref = date.line
    elif before_date_search != None:
        date.ref = before_date_search.group()
    elif line_splitter != None:
        date.ref = line_splitter.group()          
    else:
        date.ref = re.search(r"(?<=date_code0)(.+)", date.ref, re.DOTALL)
        if line_splitter != None:
            date.ref = line_splitter.group()
            
    clean_date(date)

for date in dates:
    if 0 <= date.year <= 50:
        date.year = date.year + 2000
    elif 51 <= date.year <= 99:
        date.year = date.year + 1900
        
date_sort()


print "\n\n"

