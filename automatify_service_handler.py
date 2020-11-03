def handle_service(msg:str):
    msg = msg.strip()
    if(msg.lower().startswith('adata')):
        return 'adata will be added.'