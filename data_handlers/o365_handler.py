import csv
from models.data_model import DataModel
from models.ip_model import IpModel
from models.alert_model import AlertModel
from models.rule_model import RuleModel
import ipinfo
from ipinfo.exceptions import RequestQuotaExceededError
import os
import time
from requests.exceptions import ReadTimeout
import json
import datetime
from datetime import date, timedelta
import sys


class o365:
    def __init__(self):
        # Setting up relative directories for file import and export
        self.base_path = os.path.dirname(os.path.realpath(__file__))
        self.base_path = os.path.dirname(self.base_path)
        # print(base_path)

        self.import_path = os.path.normpath(os.path.join(self.base_path, 'static/assets/csv_files/'))
        if not os.path.exists(self.base_path):
            os.mkdir(self.base_path)
        self.export_path = os.path.normpath(os.path.join(self.base_path, 'static/assets/csv_export/'))
        if not os.path.exists(self.export_path):
            os.mkdir(self.export_path)
        self.todays_date = datetime.datetime.today()


    def file_parser(self):
        # Retrieving the pass and raise rules for preliminary alerting
        pass_rule_object = RuleModel.find_one_by('type', 'pass')
        raise_rule_object = RuleModel.find_one_by('type', 'raise')
        pass_rule = str(pass_rule_object.rule)
        raise_rule = str(raise_rule_object.rule)

        # Getting today's date to check against ip expiry date
        # todays_date = datetime.datetime.today()

        # Setting up access token list for IP Info
        access_token = ['4b8a2af90147b5', 'd9c112d971b1bd', '4daea41e191295']

        #  Defining all thr columns that may be found in the audit logs for csv export
        csv_columns = ['ActorContextId', 'ApplicationDisplayName', 'ApplicationId', 'InternalLogonType', 'ClientIPAddress', 'LogonUserSid', 'ExternalAccess', 'DestinationRelativeUrl', 'MailboxOwnerUPN', 'FileId', 'ActorUserId', 'YammerNetworkId', 'VersionId', 'ActorYammerUserId', 'FileName',
                       'AzureActiveDirectoryEventType', 'ClientIP', 'CorrelationId', 'CreationTime', 'CustomUniqueId', 'DestinationFileExtension', 'DestinationFileName', 'OriginatingServer', 'MailboxOwnerSid', 'MailboxOwnerUPN,' 'DestinationRelativeUrl', 'OrganizationName', 'Port',
                       'EventData','EventSource', 'ExtendedProperties', 'ClientInfoString', 'LogonType', 'Item', 'MailboxGuid', 'LogonError', 'MailboxOwnerMasterAccountSid',  'DoNotDistributeEvent', 'FileSyncBytesCommitted', 'Id', 'ImplicitShare', 'InterSystemsId', 'IntraSystemId','ItemType', 'ListBaseType', 'ListId', 'ListItemUniqueId', 'ListTitle', 'ListBaseTemplateType', 'MachineDomainInfo', 'MachineId', 'ModifiedProperties','ObjectId', 'Operation', 'OrganizationId', 'RecordType', 'ResultStatus', 'SharingType', 'Site', 'SiteUrl', 'SourceFileExtension', 'SourceFileName', 'SourceRelativeUrl', 'SupportTicketId','Target', 'TargetContextId', 'TargetUserOrGroupName','TargetUserOrGroupType','UniqueSharingId', 'UserAgent', 'UserId', 'UserKey', 'UserType','Version', 'WebId', 'Workload','city', 'region', 'country', 'latitude', 'longitude', 'location', 'postal', 'org']
        # Give exported file a name
        export_file_name = str(datetime.datetime.now()) + '.csv'
        export_file_name = export_file_name.replace(' ', '_')
        export_file_name = export_file_name.replace(':', '-')

        #  Opening files with reader
        with open(os.path.normpath(os.path.join(self.export_path, export_file_name)), 'w') as file_write:
            writer = csv.DictWriter(file_write, fieldnames=csv_columns)
            writer.writeheader()

            # Iterate through files in the import directory
            for file in os.listdir(self.import_path):
                f = time.perf_counter()
                with open(os.path.join(self.import_path, file), 'r') as csvfile:
                    print(csvfile)
                    reader = csv.DictReader(csvfile)
                    ips = []
                    rows = []

                    # Iterate through rows in a file
                    for row in reader:
                        try:
                            # Open each row with jason loads
                            audit_data = row['AuditData']
                            row_data = json.loads(audit_data)
                        except:
                            # Try except needed as some rows in data set are malformed
                            pass

                        try:
                            ip = row_data['ClientIP']

                            # If uni IP set it to uni default
                            if '141.163.' in ip and not '.141.163.' in ip:
                                ip = '141.163.1.250'

                            # If no IP set to default
                            elif ip == "" or ip == '<null>':
                                row_data['ClientIP'] = '0.0.0.0'
                                ip = '141.163.1.250'

                            # If ip is followed by a port number handel
                            port = ''
                            if ':' in ip and '.' in ip:
                                ip_address_split = ip.split(":")
                                ip = ip_address_split[0]
                                # over wright row data with new ip
                                row_data['ClientIP'] = ip
                                port = ip_address_split[1]
                            row_data['Port'] = port

                            rows.append(row_data)
                            ips.append(ip)
                        except:
                            # Try except needed as first line does not have client IP
                            pass

                    unique_ips = set(ips)

                    # Handle the IPs, if it already know use those details, if not then call IpInfo API
                    ips_models = []
                    for ip in unique_ips:
                        # Search database to see if IP is known
                        try:
                            db_ip = IpModel.find_one_by('ip', ip)

                            # Check if known IP has expired
                            db_expiry_date = db_ip.expiry_date
                            if self.todays_date > db_expiry_date:
                                print(self.todays_date)
                                print(db_expiry_date)
                                print('Expired Break')
                                raise Exception

                            ips_models.append(db_ip)
                        except:
                            # If no ip is found except is triggered to create one
                            print('Get new ip')
                            pass
                            # print(ip)
                            bools = True
                            while bools == True:
                                try:
                                    api_ip = self.ip_info_func(ip, access_token)
                                    model_ip = IpModel(*api_ip)
                                    model_ip.replace_or_create_to_db({'ip': ip}, api_ip)
                                    db_ip = IpModel.find_one_by('ip', ip)
                                    ips_models.append(db_ip)
                                    bools = False
                                except ReadTimeout as e:
                                    print(e)
                    for row in rows:
                        row_attributes = {}
                        # try:
                        ip_address = row['ClientIP']
                        # Check if uni address
                        if '141.163' in ip_address and not '.141.163.' in ip_address:
                            ip_address = '141.163.1.250'
                        for ip in ips_models:
                            if ip_address == ip.ip:
                                client_ip = ip
                                # print('Assign client IP')
                        # except:
                        #     pass

                        # Iterate through key value pairs in json
                        for key, value in row.items():
                            if key in csv_columns:
                                # Write pairs to row_attributes
                                row_attributes[key] = value

                        # Try to add ip location data to row_attriputes
                        try:
                            row_attributes['city'] = client_ip.city
                            row_attributes['region'] = client_ip.region
                            row_attributes['country'] = client_ip.country
                            row_attributes['latitude'] = client_ip.latitude
                            row_attributes['longitude'] = client_ip.longitude
                            row_attributes['location'] = str(client_ip.latitude)+', '+str(client_ip.longitude)
                            row_attributes['postal'] = client_ip.postal
                            row_attributes['org'] = client_ip.org
                        except Exception as e:
                            print(e)
                            print(row)
                            print('fail')
                            sys.exit(0)

                        # Checking the row against rules, if a pass condition is met it wont check raise
                        try:
                            pass_condition = eval(pass_rule)
                            if pass_condition:
                                # print(pass_condition)
                                pass
                            else:
                                raise_condition = eval(raise_rule)
                                if raise_condition:
                                    alert_format = {
                                        'CreationTime': row['CreationTime'],
                                        'Id': row['Id'],
                                        'Operation': row['Operation'],
                                        'RecordType': row['RecordType'],
                                        'UserKey': row['UserKey'],
                                        'UserType': row['UserType'],
                                        'Version': row['Version'],
                                        'Workload': row['Workload'],
                                        'ClientIP': row['ClientIP'],
                                        'ObjectId': row['ObjectId'],
                                        'UserId': row['UserId'],
                                        'city': row_attributes['city'],
                                        'region': row_attributes['region'],
                                        'country': row_attributes['country'],
                                        'location': row_attributes['location'],
                                        'postal': row_attributes['postal'],
                                        'org': row_attributes['org']
                                    }
                                    try:
                                        alert_format['SourceFileName'] = row_attributes['SourceFileName']
                                    except:
                                        alert_format['SourceFileName'] = 'N/A'

                                    # Create alert object and save to DB
                                    alert = AlertModel(*alert_format)
                                    alert.replace_or_create_to_db({'Id': row['Id']}, alert_format)
                                else:
                                    pass
                                    # print(raise_condition)
                        except:
                            pass

                        # Output to csv file
                        writer.writerow(row_attributes)
                    elapsed = time.perf_counter() - f
                    print(f"File execute in {elapsed:0.2f} seconds.")
                #os.remove(base_path + file)


    def export_csv(self):

        datas = DataModel.all()
        csv_file = 'export.csv'
        b = {datas[i]: datas[i] for i in range(0, len(datas), 2)}


    def ip_info_func(self, ip_address, access_token):
        
        counter = 0
        while True:
            if counter == 3:
                sys.exit(0)
                break
            try:
                handler = ipinfo.getHandler(access_token[0])
                details = handler.getDetails(ip_address)
                break
            except RequestQuotaExceededError:
                print('Quota Exceeded')
                access_token.pop(0)
            except Exception as e:
                print('Other exception')
                print(e)
                counter = counter + 1
                # sys.exit(0)
                # break
        try:
            city = details.city
            region = details.region
            country = details.country
            loc_1 = details.loc
            try:
                postal = details.postal
            except:
                postal = 'N/A'
            org = details.org
            expiry_date = self.todays_date + timedelta(days=45)

        except:
            city = 'N/A'
            region = 'N/A'
            country = 'N/A'
            loc_1 = '0.0, 0.0'
            postal = 'N/A'
            org = 'N/A'
            expiry_date = self.todays_date

        loc_2 = loc_1.split(",")
        latitude = float(loc_2[0])
        longitude = float(loc_2[1])
        loc_dict = {}
        loc_dict['lon'] = longitude
        loc_dict['lat'] = latitude

        ip_format = {
            'ip': ip_address,
            'city': city,
            'region': region,
            'country': country,
            'latitude': latitude,
            'longitude': longitude,
            'loc': loc_dict,
            'postal': postal,
            'org': org,
            'expiry_date': expiry_date
        }
        print(ip_format['expiry_date'])
        return ip_format
