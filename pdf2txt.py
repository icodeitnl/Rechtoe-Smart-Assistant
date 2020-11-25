import PyPDF2
import re
import os

for root,dirs,files in os.walk(r"/Users/CWC/Documents/2020/Hackathon/pdf/"):

    for file in files:
    
        object = PyPDF2.PdfFileReader(os.path.join(root,file))
        pages = object.getNumPages()
        quote = "beslissing"
        
        for pgs in range(0, pages):
        
            page = object.getPage(pgs)
            print("Page Number " + str(pgs)) 
            content = page.extractText() 
            print(content)
            Quatation = re.search(quote, content)
            print(Quatation)
