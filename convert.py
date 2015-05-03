import requests
from bs4 import BeautifulSoup


for location in ['huebner', 'broadway', 'gastropub', 'thebridge']:
    content = requests.get('http://bighops.com/taplist-{0}/'.format(location))
    soup = BeautifulSoup(content.text)
    table = soup.find('tbody')
    rows = table.findAll('tr')
    for tr in rows:
        cols = tr.findAll('td')
        entry = [x.text for x in cols]
        print(entry)
        print(location)
        if entry[0] and entry[0][-1] == '*':
            entry[0] = entry[0].replace('*', "'")
            entry[0] = entry[0][:-1]
            entry[0] += '*'
        else:
            entry[0] = entry[0].replace('*', "'")

        payload = {
            "brewery": entry[0].title(),
            "beername": entry[1].title().replace('*', "'"),
            "beertype": entry[2].title().replace('*', "'"),
            "alcohols": entry[4].strip('%').strip(),
            "active": True
        }

        if '/' in entry[3]:
            payload["pricepint"] = entry[3].split('/')[-1]
            print(payload["pricepint"])
        else:
            payload["notes"] = entry[3]

        try:
            r = requests.post('http://localhost:4000/{0}/entry'.format(location), data=payload)
        except Exception as exc:
            payload['pricepint'] = entry[3]
            r = requests.post('http://localhost:4000/{0}/entry'.format(location), data=payload)
