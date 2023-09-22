import imaplib
import email
from tqdm import tqdm
import os


class EmailScraper:
    def __init__(self, imap_server, username, password, inbox):
        self.client = self._login(imap_server, username, password, inbox)
        self.queue = None

  
    def _login(self, imap_server, username, password, inbox):
        client = imaplib.IMAP4_SSL(imap_server)
        try:
            client.login(username, password)
            client.select(inbox)
        except imaplib.IMAP4.error as e:
            raise RuntimeError(f'Login Failed: {e}')
        return client

  
    def logout(self):
        if self.client:
            self.client.logout()
            self.client = None

  
    def create_queue(self, subject, startdate: 'YYYY-MM-DD' = None, 
               enddate: 'YYYY-MM-DD' = None):
        
        search_str = f'SUBJECT "{subject}"'
        
        if startdate and enddate:
            search_str += f' (SINCE {startdate} BEFORE {enddate})'
        elif startdate or enddate:
            raise AttributeError('Provide a start and end date.')
            
        status, email_ids = self.client.search(None, search_str)
        self.queue = email_ids[0].split(b' ')
        
        return self.queue

  
    def collect_msg(self, email_id):
        status, data = self.client.fetch(email_id, '(RFC822)')
        msg = email.message_from_bytes(data[0][1])
        return msg

  
    def collect_attachment(self, msg, save_dir='./', mime='text/csv', strict=False):
        for part in msg.walk():
            part_mime = part.get_content_type()

            if part_mime==mime:
                data = part.get_payload(decode=True)
                if save_dir:
                    self._save_attachment(data, save_dir, part.get_filename())
                    
                return data
        # Raise if strict and no match
        if strict:
            raise ValueError(f'Message did not provide {mime}.')

  
    def _save_attachment(self, data, save_dir, filename):
        file_path = os.path.join(save_dir, filename)
        with open(file_path, 'wb') as f:
            f.write(data)

  
    def collect_queue(self, save_dir, queue=None):
        queue = queue or self.queue
        with tqdm(total=len(queue), desc="Processing Emails") as pbar:
            for email_id in queue:
                msg = self.collect_msg(email_id)
                self.collect_attachment(msg, save_dir)
                pbar.update(1)
