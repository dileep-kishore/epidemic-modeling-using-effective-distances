#!/usr/bin/env python3
#
#
#
country_pair_traffic_dict={}
output_list=[]

with open("avia_paocc.tsv",'r') as in_stream:
  for line in in_stream:
    skipped_country=['EU','EA']

    if line[4:12]=='PAS_CRD,' and \
       line[12:14] not in skipped_country and \
       line[15:17] not in skipped_country: #skip EU, which is not a country
      source=line[12:14]
      dest=line[15:17]
      traffic=0
      try:
        traffic=int(line.split('\t')[31]) # data column for year 2015
      except:
        pass
      source=min(source,dest)
      dest=max(source,dest)
      if (source,dest) in country_pair_traffic_dict:
        country_pair_traffic_dict[(source,dest)].append(traffic)
      else:
        country_pair_traffic_dict[(source,dest)]=[traffic]

for key,val in country_pair_traffic_dict.items():
  country_pair_traffic_dict[key]=sum(country_pair_traffic_dict[key])/len(country_pair_traffic_dict[key])

for key in sorted(country_pair_traffic_dict.keys()):
  output_list.append( ",".join( [key[0],
                                 key[1],
                                 str(country_pair_traffic_dict[key])
                                ]
                              )
                    )

with open("EU_2015_AirTraffic_Country_Pair.csv",'w') as out_stream:
  out_stream.write('\n'.join(output_list))
