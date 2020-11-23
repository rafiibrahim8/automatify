from adata import get_detail_text
from gdata import get_formated_data_bal

def handle_service(msg):
    msg = msg.strip()
    if(msg.lower().startswith('adata')):
        return get_detail_text()
    elif(msg.lower().startswith('gdata')):
        return get_formated_data_bal()
    return None
