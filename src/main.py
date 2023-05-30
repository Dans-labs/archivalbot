from datetime import datetime
import logging

from src.modules.ldn_inbox_poller import LDN_Inbox_Poller

from commons import settings


def main():
    inbox_poller = LDN_Inbox_Poller(settings.LDN_INBOX_SERVICE_URL, settings.POLLING_INTERVAL)
    inbox_poller.run()


if __name__ == "__main__":
    logging.info(f'Start archival bot at {datetime.now().strftime("%H:%M:%S")}')
    logging.info(f'Inbox URL: {settings.LDN_INBOX_SERVICE_URL}. Interval: {settings.POLLING_INTERVAL}')
    main()
