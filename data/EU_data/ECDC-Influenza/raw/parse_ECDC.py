#!/usr/bin/env python3
#
EU_countries=["AT","BE","BG","CH","CY","CZ","DE","DK","EE","EL","ES","FI","FR","HR","HU","IE","IS","IT","LT","LU","LV","MT","NL","NO","PL","PT","RO","SE","SI","SK","TR","UK"]

influenza_dict={}
output_list=[]

with open("ECDC_surveillance_data_Influenza-1.csv",'r') as in_stream:
  in_stream.readline()
  for line in in_stream:
    items=line.strip().split(',')
    time=items[4]
    country_code=items[5][0:2]
    count=int(items[7])
    if time not in influenza_dict:
      influenza_dict[time]={country:0 for country in EU_countries}
    if country_code in EU_countries:
      influenza_dict[time][country_code]+=count

for time in sorted(influenza_dict.keys()):
  for country in EU_countries:
    output_list.append(','.join((time,country,str(influenza_dict[time][country]))))

with open("EU_influenza.csv",'w') as out_stream:
  out_stream.write('\n'.join(output_list))
