from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from cStringIO import StringIO

contact_info = {}

def string_to_key(string):
    #collects string before colon and converts it to the proper csv snakecase
    # disregarding extra whitespace following the colon
    return string.split(':')[0].lower().replace(' ','_')

def get_name_and_credit_address(array):
    start_index = array.index('Name:')
    end_index = start_index + 4
    raw_name_and_credit_info = array[start_index:end_index]
    raw_keys = raw_name_and_credit_info[:2]
    raw_values = raw_name_and_credit_info[-2:]
    char = set(',')
    exclude = set(':,')
    find_address = [value for value in raw_values if char & set(value)]
    credit_address = find_address[0] if 0 < len(find_address) else ''
    not_name = [value for value in raw_values if exclude & set(value)]
    find_name = [x for x in raw_values if x not in not_name]
    name = find_name[0] if 0 < len(find_name) else ''
    contact_info[string_to_key(raw_keys[0])] = name
    contact_info[string_to_key(raw_keys[1])] = credit_address


def get_phone_email_info(array, search_strings_array):
    for string in search_strings_array:
        start_index = array.index(string)
        end_index = start_index + 4
        raw_contact_info = array[start_index:end_index]
        raw_keys = raw_contact_info[:2]
        raw_values = raw_contact_info[-2:]
        char = set('@')
        exclude = set(':@')
        find_email = [value for value in raw_values if char & set(value)]
        email = find_email[0] if 0 < len(find_email) else ''
        not_phone = [value for value in raw_values if exclude & set(value)]
        find_phone = [x for x in raw_values if x not in not_phone]
        phone = find_phone[0] if 0 < len(find_phone) else ''
        contact_info[string_to_key(raw_keys[0])] = phone
        contact_info[string_to_key(raw_keys[1])] = email

def get_ssn(array):
    start_index = array.index('SSN: ')
    end_index = start_index + 2
    raw_contact_info = array[start_index:end_index]
    raw_keys = raw_contact_info[:1]
    raw_values = raw_contact_info[-1:]
    char = set('-')
    find_ssn = [value for value in raw_values if char & set(value)]
    ssn = find_ssn[0] if 0 < len(find_ssn) else ''
    contact_info[string_to_key(raw_keys[0])] = ssn

def get_msisdn(array):
    start_index = array.index('MSISDN:')
    end_index = start_index + 3
    raw_contact_info = array[start_index:end_index]
    raw_keys = raw_contact_info[:2]
    raw_values = raw_contact_info[-2:]
    char = set('()')
    find_msisdn = [value for value in raw_values if char & set(value)]
    msisdn = find_msisdn[0] if 0 < len(find_msisdn) else ''
    contact_info[string_to_key(raw_keys[0])] = msisdn

def get_imsi(array):
    ismi_index = [ i for i, key in enumerate(array) if key.startswith('IMSI') ][0]
    raw_key_value_pair = array[ismi_index].split(':')
    ismi_key = raw_key_value_pair[0].strip().lower()
    ismi_value = raw_key_value_pair[1].strip()
    contact_info[ismi_key] = ismi_value

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

    search_strings = ['Contact Home Phone:', 'Contact Work Phone:']

    get_name_and_credit_address(text_list)
    get_ssn(text_list)
    get_msisdn(text_list)
    get_imsi(text_list)
    get_phone_email_info(text_list, search_strings)

    fp.close()
    device.close()
    retstr.close()


    return contact_info

print(convert_pdf_to_txt('TestReport.pdf'))
