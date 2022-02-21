"""subclass EmailMessage to simplify file attachments and building/sending an email"""
from typing import Union
from email.message import EmailMessage
import mimetypes
import smtplib
import os
from dotenv import load_dotenv

load_dotenv()

EMAIL_ADDRESS = os.environ.get("OUTLOOK_EMAIL_ADDRESS")
EMAIL_PASSWORD = os.environ.get("OUTLOOK_EMAIL_PASSWORD")
print(EMAIL_ADDRESS, EMAIL_PASSWORD)

class CustomEmailMessage(EmailMessage):
    """
    adding a method that simplifies adding file attachments
    """
    def new_file_attachment(self, _file:str):
        """Takes a filepath and attaches the file to an email"""
        ctype, _ = mimetypes.guess_type(_file)
        maintype, subtype = ctype.split('/', 1)
        with open(_file,'rb') as handler:
            self.add_attachment(
                handler.read(),
                maintype=maintype,
                subtype=subtype,
                filename=os.path.basename(_file)
            )
    def new_attachment_bytestream(self, buffer: bytes, filename: str):
        """Takes an BytesIO-generated bytes and desired filename and attaches it as a file"""
        maintype, _, subtype = (
            mimetypes.guess_type(filename)[0] or 'application/octet-stream'
            ).partition("/")
        self.add_attachment(
            buffer,
            maintype=maintype,
            subtype=subtype,
            filename=filename
        )


def send_email(recipients, subject, template_msg, msg_list, 
        msg_signature, attachments: Union[str,list,tuple]=None):
    """
    conveinece function for building and sending an email
        using the function variables
    """
    email = CustomEmailMessage()
    email['Subject'] = subject
    email['To'] = recipients
    email['From'] = EMAIL_ADDRESS
    email.set_content("")
    email.add_alternative(f"""
        <font face="Roboto, sans-serif">
        <p>{template_msg}</p>
        <p>{msg_list}</p>
        <p>{msg_signature}</p>
        </font>
        """, subtype='html')

    if attachments:
        # does not account for a list of tuples!
        if isinstance(attachments,list):
            for attachment in attachments:
                email.new_file_attachment(attachment)
        elif isinstance(attachments,tuple):
            file_data, file_name = attachments
            email.new_attachment_bytestream(buffer=file_data,filename=file_name)
        else:
            email.new_file_attachment(attachments)

    # send Email
    print(EMAIL_ADDRESS, EMAIL_PASSWORD)
    mailserver = smtplib.SMTP('smtp.office365.com',587)
    mailserver.starttls()
    mailserver.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    mailserver.send_message(email)
    mailserver.quit()
