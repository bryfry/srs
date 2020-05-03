import requests

def set_printer(s):
  max_i = max([i[0] for i in list(s)])
  out = (max_i+1) * "_"
  out_list = list(out)
  for i in list(s):
    out_list[i[0]] = i[1]
  print("".join(out_list))

port = input()
flag = set()
while True:
  #print (f"{port}")
  try:
    r = requests.get(f'http://srs.trustme.click:{port}')
    data = r.json()
    port = data['next']
    flag.add((data['flag-slice']['index'],data['flag-slice']['value']))
    set_printer(flag)
  except requests.exceptions.ConnectionError:
    pass
  except Exception as e :
    print(e)
    break
