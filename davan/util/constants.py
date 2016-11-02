'''
Created on 27 okt. 2016

@author: Wilma
'''

UPS_SERVICE_NAME = "Ups"
HTML_TABLE_END = "</table>"
HTML_TABLE_START = """<style>
table {
    font-family: arial, sans-serif;
    border-collapse: collapse;
    width: 100%;
}

td, th {
    border: 1px solid #dddddd;
    text-align: left;
    padding: 8px;
}

tr:nth-child(even) {
    background-color: #dddddd;
}
</style><table> <tr>
    <th>Service</th>
    <th>Successful</th> 
    <th>Error</th>
  </tr>"""
