# List and retrieve plots from Madrigal exp directory.
# Code adapted from'
# https://stackoverflow.com/questions/11023530/python-to-list-http-files-and-directories
import requests
from bs4 import BeautifulSoup
from os import path

def get_plots(url, tmpdir):

    file_list=[]
    ext='png'

    page = requests.get(url).text
    soup = BeautifulSoup(page, 'html.parser')
    plot_urls=[url + '/' + node.get('href') for node in soup.find_all('a') if node.get('href').endswith(ext)]

    

    for plot_url in plot_urls:

        outFile=path.join(tmpdir, path.basename(plot_url))

        r=requests.get(plot_url)
        with open(outFile, 'wb') as fd:
            fd.write(r.content)
        
        file_list.append(outFile)

    return(file_list)


        





