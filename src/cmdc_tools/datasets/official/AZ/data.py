import requests
import re
from bs4 import BeautifulSoup
import json
import pandas as pd

from ...base import DatasetBaseNoDate

def onAlias(it, value, cstring):
    return value[it] if (it >= 0) else cstring["dataValues"][abs(it)-1]

class Arizona(DatasetBaseNoDate):
    def get(self):
        with requests.Session() as req:
            # Find the URL of the data.
            resp = req.get("https://tableau.azdhs.gov/views/ELRcovid/LaboratoryTestingExternalDraft?:isGuestRedirectFromVizportal=y&:embed=y")
            soup = BeautifulSoup(resp.text, "html.parser")
            tableau_tag = soup.find("textarea", {"id": "tsConfigContainer"})
            tableau_data = json.loads(tableau_tag.text)
            data_url = f'https://tableau.azdhs.gov/{tableau_data["vizql_root"]}/bootstrapSession/sessions/{tableau_data["sessionid"]}'
            
            # Request the data.
            resp = requests.post(data_url, data= {"sheet_id": tableau_data["sheetId"],})

            # Parse the response.
            # The response contains multiple chuncks of the form
            # `<size>;<json>` where `<size>` is the number of bytes in `<json>`
            resp_text = resp.text
            data = []
            while len(resp_text) != 0:
                size, rest = resp_text.split(";", 1)
                chunck = json.loads(rest[:int(size)])
                data.append(chunck)
                resp_text = rest[int(size):]
            

            tableau_data = data[0]["worldUpdate"]["applicationPresModel"]["workbookPresModel"]["dashboardPresModel"]

            views = tableau_data["viewIds"]
            zones = tableau_data["zones"]

            '''
            for key, zone in zones.items():
                if ('presModelHolder' in zone):
                    #print('\n\n')
                    if 'worksheet' in zone:
                        print(zone['worksheet'])

                    else:
                        print('NO WORKSHEET')
                        print(zone)                
                     #(zone['worksheet'] == 'Total Tests Conducted') and 
                    if ('visual' in zone['presModelHolder']):
                        for k, v in zone['presModelHolder']['visual'].items():
                            print(k)
                            print(v)
                        if 'scene' in zone['presModelHolder']['visual']:
                            secondBottom = zone['presModelHolder']['visual']['scene']
                            if 'runtimeRenderInputDatastore' in secondBottom:
                                hexText = secondBottom['runtimeRenderInputDatastore']
                                #print(' '.join([hexText[i:i+2] for i in range(0, len(hexText), 2)]))
                                #print(' '.join([hexText[i:i+4] for i in range(0, len(hexText), 4)]))
                                #print(bytearray.fromhex(hexText).decode('ascii'))
                                #print(bytes.fromhex(hexText).decode('utf-8'))
            '''
            
            valueInfo = data[1]['secondaryInfo']['presModelMap']['vizData']['presModelHolder']['genPresModelMapPresModel']['presModelMap']
            dataFull = data[1]["secondaryInfo"]["presModelMap"]["dataDictionary"]["presModelHolder"]["genDataDictionaryPresModel"]["dataSegments"]["0"]["dataColumns"]

            for metric in valueInfo:
                print('\n')
                print(metric)
                metricsDict = valueInfo[metric]['presModelHolder']['genVizDataPresModel']

                columnsData = metricsDict['paneColumnsData'] #['vizDataColumns']
                result = [ {
                        "fieldCaption": t.get("fieldCaption", ""), 
                        "valueIndices": columnsData["paneColumnsList"][t["paneIndices"][0]]["vizPaneColumns"][t["columnIndices"][0]]["valueIndices"],
                        "aliasIndices": columnsData["paneColumnsList"][t["paneIndices"][0]]["vizPaneColumns"][t["columnIndices"][0]]["aliasIndices"],
                        "dataType": t.get("dataType"),
                        "paneIndices": t["paneIndices"][0],
                        "columnIndices": t["columnIndices"][0]
                        }
                        for t in columnsData["vizDataColumns"]
                        if t.get("fieldCaption")
                ]
                frameData = {}
                cstring = [t for t in dataFull if t["dataType"] == "cstring"][0]
                for t in dataFull:
                    for index in result:
                        if (t["dataType"] == index["dataType"]):
                            if len(index["valueIndices"]) > 0:
                                frameData[f'{index["fieldCaption"]}-value'] = [t["dataValues"][abs(it)] for it in index["valueIndices"]]
                            if len(index["aliasIndices"]) > 0:
                                frameData[f'{index["fieldCaption"]}-alias'] = [onAlias(it, t["dataValues"], cstring) for it in index["aliasIndices"]]

                df = pd.DataFrame.from_dict(frameData, orient='index').fillna(0).T
                with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.width', 1000):
                    print(df)
                
            return data
