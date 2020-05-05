import requests
import re
from collections import defaultdict
url = 'https://baike.baidu.com/item/%E5%8C%97%E4%BA%AC%E5%9C%B0%E9%93%81/408485?fr=aladdin'
regex_map = {
    'line_url':r'<td width="204" align="center" valign="middle" colspan="1" rowspan="2"><a target=_blank href="(\/item\/\S*\w*)"\s*(data-lemmaid="\d+")?>(\w+)',
    'station_name':r'<tr>(<th width="\d+">\d+</th>)?(<td)+\s*((width="\d+")?\s*(align="center")?\s*(valign="middle")?\s*(valign="center")?\s*(colspan="1")?\s*(rowspan="\d+")?>(\w+)?</td>)?(<td)?((align="middle")?\s*(valign="center")?\s*(width="\d+")?\s*(height="\d+")?\s*(align="center")?\s*(valign="(middle|center)")?\s*(class="coloredcell")?\s*(colspan="\d+")?\s*(rowspan="\d+")?\s*(valign="center")?\s*(class="coloredcell")?\s*>)?(<div class="para" label-module="para">)?(<a target=_blank href="\/item\/\S*\w*\s*)?\s*(data-lemmaid="\d+")?>(<i>)?(\w+)'
}
def get_regex(content,regex):
    pattern = re.compile(regex)
    return pattern.findall(content)
def get_response(url):
    session = requests.session()
    session.headers[
        'user-agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'
    response = session.get(url)
    return response.content.decode('utf-8')
def get_station_name(likes):
    station_name = []
    for line in likes:
        station_name.append(list(line)[-1])
    return station_name
likes = get_regex(get_response(url),regex_map['line_url'])
line_info = {}
for line in likes:
    line_url,line_name = line[0],line[-1]
    line_info[line_name] = 'https://baike.baidu.com' + line_url
keys = line_info.keys()
station_info = {}
station_connection_src = {}
station_connection = defaultdict(list)
for key in keys:
    station_info[key] = get_station_name(get_regex(get_response(line_info[key]),regex_map['station_name']))
    for i, item in enumerate(station_info[key]):
        if item not in station_connection_src:
            station_connection_src[item] = set()
        if i == 0:
            station_connection_src[item].add(station_info[key][i+1])
        else :
            if i == len(station_info[key]) -1:
                station_connection_src[item].add(station_info[key][i - 1])
            else:
                station_connection_src[item].add(station_info[key][i + 1])
                station_connection_src[item].add(station_info[key][i - 1])
station_connection.update(station_connection_src)
def search(start,destination,connection_graph,sort_candidate):
    pathes = [[start]]
    visited = set()
    while pathes:
        path = pathes.pop(0)
        frontier = path[-1]
        if frontier in visited:continue
        successors = connection_graph[frontier]
        for station in successors:
            if station in path: continue
            new_path = path + [station]
            pathes.append(new_path)
            if station == destination: return new_path
        visited.add(frontier)
        pathes = sort_candidate(pathes)
def min_transfer(pathes):
    if len(pathes) <=1: return pathes
    def get_line_count(path):
        if len(path) < 3: return 0
        line_count = 0
        for i in range(len(path)):
            if i == len(path) - 2: break
            station = path[i]
            station_next = path[i+1]
            station_next_next = path[i+2]
            if find_line(station, station_next) != find_line(station_next, station_next_next): line_count += 1
        return line_count
    return sorted(pathes,key=get_line_count)
def find_line(station,station_next):
    for key in keys:
        if station in station_info[key] and station_next in station_info[key] : return key
def pretty_path(path):
    route = ''
    if path and len(path) > 1:
        route = route + (path[0]) + '->乘坐'  + find_line(path[0], path[1]) + '->'
        j = 0
        for i in range(len(path)):
            j += 1
            if i == len(path) - 2:
                route = route + str(j) + '站'
                break
            station = path[i]
            station_next = path[i + 1]
            station_next_next = path[i + 2]
            pre_line = find_line(station, station_next)
            next_line = find_line(station_next, station_next_next)
            if pre_line != next_line:
                temp = ''
                temp =  str(j) + '站->'  + station_next + '->换乘' + next_line + '->'
                route = route + temp
                j = 1
        route = route +('->抵达终点' + path[-1] + '下车')
    return route

path = search('立水桥站','北京西站',station_connection,sort_candidate=min_transfer)
print(pretty_path(path))