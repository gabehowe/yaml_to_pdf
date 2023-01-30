import csv
import pandas as pd
from yaml_to_pdf import form
from datetime import datetime, timedelta

if __name__ == '__main__':
    # Load csv with the product information
    reader = pd.read_csv('example/sold.csv')
    # Drop first column
    data = reader.drop('#', axis=1).to_dict()
    # Sort data into map: header to values
    products_sold = {k: [str(i) for i in list(v.values())] for k, v in data.items()}
    total = sum([float(it) for it in products_sold['cost']])

    form('example/test.pdf', 'example/invoice_template.yaml', billing='Sam Joe\\n1345 Woodpecker Driver\\nJonesville, MT 67163',
         invoice_no='0x00f4',
         due_date=(datetime.now() + timedelta(days=14)).timestamp(),
         products=products_sold, total=total,
         due_amount=total)
