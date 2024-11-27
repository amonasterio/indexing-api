import params as p
from googleapiclient.discovery import build
from google.oauth2 import service_account
from oauth2client import client
from oauth2client import file
import httplib2
import json
import os
import pandas as pd
import argparse
from oauth2client import tools

INPUT_FILE="input/urls_list.csv"
authorized='authorizedcreds_'+p.cuenta+'.dat' #guardará credenciales cuando nos hayamos logado
key='../credentials/client_secrets_'+p.cuenta+'.json'


def authorize_creds(creds,authorizedcreds=authorized):
    '''
    Authorize credentials using OAuth2.
    '''
    print('Authorizing Creds')
    # Variable parameter that controls the set of resources that the access token permits.
    SCOPES = ['https://www.googleapis.com/auth/indexing']
 
    # Path to client_secrets.json file
    CLIENT_SECRETS_PATH = creds
 
    # Create a parser to be able to open browser for Authorization
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[tools.argparser])
    flags = parser.parse_args([])
 
    # Creates an authorization flow from a clientsecrets file.
    # Will raise InvalidClientSecretsError for unknown types of Flows.
    flow = client.flow_from_clientsecrets(
        CLIENT_SECRETS_PATH, scope = SCOPES,
        message = tools.message_if_missing(CLIENT_SECRETS_PATH))
 
    # Prepare credentials and authorize HTTP
    # If they exist, get them from the storage object
    # credentials will get written back to the 'authorizedcreds.dat' file.
    storage = file.Storage(authorizedcreds)
    credentials = storage.get()
 
    # If authenticated credentials don't exist, open Browser to authenticate
    if credentials is None or credentials.invalid:
        credentials = tools.run_flow(flow, storage, flags)      # Add the valid creds to a variable
 
    # Take the credentials and authorize them using httplib2   
    http = httplib2.Http()                                      # Creates an HTTP client object to make the http request
    http = credentials.authorize(http=http)                     # Sign each request from the HTTP client with the OAuth 2.0 access token
    webmasters_service = build('indexing', 'v3', credentials=credentials)   # Construct a Resource to interact with the API using the Authorized HTTP Client.
 
    print('Auth Successful')
    return webmasters_service






def index_urls(service, urls):
    """
    Envía solicitudes de indexación para varias URLs.
    """
    ENDPOINT = 'https://indexing.googleapis.com/v3/urlNotifications:publish'
    for url in urls:
        try:
            # Cuerpo de la solicitud
            content = {
                "url": url,
                "type": "URL_UPDATED"  # O "URL_DELETED" si se elimina
            }
            
            # Llamada a la API
            request = service._http.request(ENDPOINT, method='POST', body=json.dumps(content))
            status_code = request[0].status
            response_content = json.loads(request[1].decode('utf-8'))
            
            # Imprimir el resultado
            print(f"URL: {url} | Status Code: {status_code} | Response: {response_content}")
        except Exception as e:
            print(f"Error al indexar {url}: {e}")


if __name__ == '__main__':
    creds = key
    service = authorize_creds(creds) 
    # Lista de URLs que quieres indexar
    df_entrada=pd.read_csv(INPUT_FILE,header=None)
    urls_to_index=df_entrada[0].values.tolist()

    # Llamada a la función para indexar
    index_urls(service,urls_to_index)



