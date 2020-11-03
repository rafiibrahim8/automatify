from adata import get_detail_text

def handle_service(msg:str):
    msg = msg.strip()
    if(msg.lower().startswith('adata')):
        return get_detail_text()
    
    return None