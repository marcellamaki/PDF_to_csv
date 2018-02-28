import pprint
import json
import csv


from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from cStringIO import StringIO

pp = pprint.PrettyPrinter(indent=4)

# def save_subscriber_json(data_object):
#     with open('subscriber_json.txt', 'w') as outfile:
#         json.dump(data_object, outfile)

def parse_subscribers_to_csv(json_object):
    subscriber_parsed = json.loads(json_object)
    sub_data = subscriber_parsed['subscriber_details']
    subscriber_data = open('./subscribers.csv', 'w+')
    csvwriter = csv.writer(subscriber_data)
    count = 0
    for subscriber in sub_data:
          if count == 0:
                 header = subscriber.keys()
                 csvwriter.writerow(header)
                 count += 1
          csvwriter.writerow(subscriber.values())
    subscriber_data.close()

def separate_each_subscriber(array):
  # creates an array to hold all arrays of each subscribers data
  all_subscribers_array = []
  start_index = 0
  # identifies the value of each index that terminates a particular subscribers information
  ending_indices = [ i for i, key in enumerate(array) if key.startswith('\x0c') ]
  # iterates through all of the ending indices and appends each to array of arrays
  for end_index in ending_indices:
    single_subscriber_array = array[start_index:end_index]
    all_subscribers_array.append(single_subscriber_array)
    start_index = start_index + end_index + 1
  #maps through all_subscribers_array and creates an array of parsed subscriber objects
  subscribers_object_array = map(return_subscriber_object, all_subscribers_array)
  # pp.pprint(subscribers_object_array)
  subscriber_data = {}
  subscriber_data['subscriber_details'] = subscribers_object_array
  subscriber_data_json = json.dumps(subscriber_data)
  # print(subscriber_data_json)
  parse_subscribers_to_csv(subscriber_data_json)

def return_subscriber_object(subscriber_data):
    # converts each array of raw data into parsed subscriber object with necessary information
    # contact_info begins as an empty object, and each successive function adds the additional necessary data to the subscriber object
    contact_info = {}
    search_strings = ['Contact Home Phone:', 'Contact Work Phone:']
    contact_info = get_phone_email_info(subscriber_data, search_strings, contact_info)
    contact_info = get_name_and_credit_address(subscriber_data, contact_info)
    contact_info = get_ssn(subscriber_data, contact_info)
    contact_info = get_msisdn(subscriber_data, contact_info)
    contact_info = get_imsi(subscriber_data, contact_info)
    return contact_info

def string_to_key(string):
    #collects string before colon and converts it to the proper csv snakecase
    # disregarding extra whitespace following the colon
    return string.split(':')[0].lower().replace(' ','_')

def get_name_and_credit_address(array, contact_info):
    # searches user raw data for the bundle of keys and values
    start_index = array.index('Name:')
    end_index = start_index + 4
    raw_name_and_credit_info = array[start_index:end_index]
    raw_keys = raw_name_and_credit_info[:2]
    raw_values = raw_name_and_credit_info[-2:]
    char = set(',')
    exclude = set(':,')
    find_address = [value for value in raw_values if char & set(value)]
    credit_address = find_address[0] if 0 < len(find_address) else 'none'
    not_name = [value for value in raw_values if exclude & set(value)]
    find_name = [x for x in raw_values if x not in not_name]
    name = find_name[0] if 0 < len(find_name) else 'none'
    contact_info[string_to_key(raw_keys[0])] = name
    contact_info[string_to_key(raw_keys[1])] = credit_address
    return contact_info


def get_phone_email_info(array, search_strings_array, contact_info):
    # searches user raw data for the bundle of keys and values
    for string in search_strings_array:
        start_index = array.index(string)
        end_index = start_index + 4
        raw_contact_info = array[start_index:end_index]
        raw_keys = raw_contact_info[:2]
        raw_values = raw_contact_info[-2:]
        char = set('@')
        exclude = set(':@')
        find_email = [value for value in raw_values if char & set(value)]
        email = find_email[0] if 0 < len(find_email) else 'none'
        not_phone = [value for value in raw_values if exclude & set(value)]
        find_phone = [x for x in raw_values if x not in not_phone]
        phone = find_phone[0] if 0 < len(find_phone) else 'none'
        contact_info[string_to_key(raw_keys[0])] = phone
        contact_info[string_to_key(raw_keys[1])] = email
    return contact_info

def get_ssn(array, contact_info):
    # searches user raw data for the bundle of keys and values
    start_index = array.index('SSN: ')
    end_index = start_index + 2
    raw_contact_info = array[start_index:end_index]
    raw_keys = raw_contact_info[:1]
    raw_values = raw_contact_info[-1:]
    char = set('-')
    find_ssn = [value for value in raw_values if char & set(value)]
    ssn = find_ssn[0] if 0 < len(find_ssn) else 'none'
    contact_info[string_to_key(raw_keys[0])] = ssn
    return contact_info

def get_msisdn(array, contact_info):
    # searches user raw data for the bundle of keys and values
    start_index = array.index('MSISDN:')
    end_index = start_index + 3
    raw_contact_info = array[start_index:end_index]
    raw_keys = raw_contact_info[:2]
    raw_values = raw_contact_info[-2:]
    char = set('()')
    find_msisdn = [value for value in raw_values if char & set(value)]
    msisdn = find_msisdn[0] if 0 < len(find_msisdn) else 'none'
    contact_info[string_to_key(raw_keys[0])] = msisdn
    return contact_info

def get_imsi(array, contact_info):
    # searches user raw data for index that contains all ismi info
    ismi_index = [ i for i, key in enumerate(array) if key.startswith('IMSI') ][0]
    raw_key_value_pair = array[ismi_index].split(':')
    ismi_key = raw_key_value_pair[0].strip().lower()
    ismi_value = raw_key_value_pair[1].strip()
    contact_info[ismi_key] = ismi_value
    return contact_info

def convert_pdf_to_txt(path):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = file(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos=set()

    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)

    text = retstr.getvalue()
    text_list = text.splitlines()
    text_list = [x for x in text_list if x != '']

    separate_each_subscriber(text_list)


    fp.close()
    device.close()
    retstr.close()


print(convert_pdf_to_txt('TestReport.pdf'))
