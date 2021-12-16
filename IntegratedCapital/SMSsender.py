import csv
import requests
import json

class SMSSender:
    """
    Control the process of reading client information from a csv file and sending transactional SMS to those clients.
    """

    def __init__(self, fileName):

        """
        Parameters:
            fileName : String
                The csv file containing the client information
        """

        self.fileName = fileName
        self.clientData = self.readFile()

        # Authorization token for using the Mailjet API
        self.access_token = 'ENTER_YOUR_TOKEN_HERE'

        self.sendSMS()
        self.retrieveFailedSendsData()
    
    def readFile(self):

        """
        Reads the given file instantiated in the constructor containing the client information.

        Returns:
            clientData : Array[]
                An array of arrays containing the client infomration in order of (client name, state, mobile number, message)
        """

        clientData = []

        with open(self.fileName, mode='r', encoding='utf-8-sig') as file:
            reader = csv.reader(file, delimiter=',')
            for line in reader:
                clientData.append(line); 

        return clientData; 

    def sendSMS(self):

        """
        Sends the transactional SMS for each client using the Mailjet API.
        """

        sendURL = 'https: // api.mailjet.com/v4/sms-send'
    
        for i in range(len(self.clientData)):
            headers = {'Authorization': 'Bearer {}'.format(self.access_token),
                    'Content-Type': 'application/json'}
            
            data = {
                'Text': self.clientData[i][3],
                'To': self.clientData[i][2],
                'From': self.clientData[i][0]
            }

            response = requests.post(url=sendURL, headers=headers, data=data)

    def retrieveSuccessfulSendsCount(self):

        """
        gets the count of successfull transactional SMS that were processed in sendSMS()

        Returns:
            successfullCount : integer
                Number of successfull SMS
        """

        countURL = 'https://api.mailjet.com/v4/sms/count'

        headers = {'Authorization': 'Bearer {}'.format(self.access_token)}
        params = {'StatusCode': 3}

        response = requests.get(url=countURL, params=params)
        successfullCount = response.json().get('Count')

        return successfullCount

    def retrieveFailedSendsCount(self):

        """
        gets the count of unsuccessfull/rejected transactional SMS that were processed in sendSMS()

        Returns:
            unsuccessfullCount : integer
                Number of unsuccessfull SMS
        """

        countURL = 'https://api.mailjet.com/v4/sms/count'

        headers = {'Authorization': 'Bearer {}'.format(self.access_token)}
        response = requests.get(url=countURL, params={})

        totalSentMessages = response.json().get('Count')

        # Number of unsuccessfull/rejected messages is the difference between the sucessfull and all messages sent
        unsuccessfullCount = totalSentMessages - self.retrieveSuccessfulSendsCount()

        return unsuccessfullCount
    
    def retrieveFailedSendsData(self):

        """
        Retrieves all transactional information regarding the failed/rejected SMS and provides a URL to 
        download a csv of all the rejected SMS sends. 

        Prints:
            csvURL : String
                The URL of csv file containing information of the rejected SMS
        """

        print('Sucessful SMS sent count: {}'.format(self.retrieveSuccessfulSendsCount()))
        print('Unsuccessful SMS sent count: {}'.format(self.retrieveFailedSendsCount()))


        # The export requests collects the rejected information in a JSON file that can be downloaded

        exportURL = 'https://api.mailjet.com/v4/sms/export'

        headersPost = {'Authorization': 'Bearer {}'.format(self.access_token),
                        'Content-Type': 'application/json'}


        # StatusCode 3 and 4 are for rejected SMS as highlighted in the Mailjet API Documentation
        dataPost = {
            'FromTS': '1631729690',
            'ToTS': '1639628114',
            'StatusCode': 3,
            'StatusCode': 4
        }

        reponsePost = requests.post(exportURL, headers=headersPost, data=dataPost)

        # After calling the export method above, the download method is done by getting the information from the export call
        # with matching JobID and accessing the URL key from the returned JSON file. 

        downloadCsvUrl = 'https://api.mailjet.com/v4/sms/export/{}'.format(reponsePost.json().get('ID'))

        headersGet = {'Authorization': 'Bearer {}'.format(self.access_token)}
        
        responseGet = requests.get(downloadCsvUrl, headersGet, data={})

        csvURL = responseGet.json.get('URL')

        print('Download the csv file from: {}'.format(csvURL))

if __name__ == '__main__':
    fileName = input('Enter the file name (ensure it is in the same directory): ')
    sender = SMSSender(fileName); 
