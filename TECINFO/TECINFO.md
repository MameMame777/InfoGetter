
web sccanning for following URLs

## FPGA IPS

### Xilinx Info URL
https://docs.amd.com/search/all?query=Versal&value-filters=Document_Type_custom~%2522Data+Sheet%2522_%2522User+Guides+%2526+Manuals%2522*Product_custom~%2522IP+Cores+(Adaptive+SoC+%2526+FPGA)%2522_%2522%25E3%2582%25A2%25E3%2583%2580%25E3%2583%2597%25E3%2583%2586%25E3%2582%25A3%25E3%2583%2596+SoC%25E3%2580%2581FPGA%2522&date-filters=ft%253AlastEdition~last_month&content-lang=en-US

### Altera Info URL
https://www.intel.com/content/www/us/en/products/details/fpga/stratix/10/docs.html?q=DSP&s=Relevancy

### Arxiv Info URL about How to use the API
get latest papers from arxiv API 
output the json file with the following structure:
```json
{
  "title": "Machine Learning for Quantum Systems",
  "abstract": "This paper explores the application of machine learning techniques...",
  "link": "http://arxiv.org/abs/2507.06127v1"
}
```
https://info.arxiv.org/help/api/index.html
get cs.AR"  # Hardware Architecture
get cs.AI"  # Artificial Intelligence


### IEEE Info URL
Metadata Search API

## operation of this script
# This script is used to scan the above URLs for FPGA IPs and extract relevant information.
  1. get the HTML/pdf content of the URLs.
  2. output the json file with the following structure:
     {
       "name": "document name",
       "url": "URL to the IP documentation"
     }
  3. send email to the user.

each scrapaer should implement individual code.
also email sending should be implemented in a separate module.
this is intend to easyly add new scrapers in the future.

main script should call the individual scrapers and collect the results.