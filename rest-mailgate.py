#!/usr/bin/env python3

import sys
import logging.config
import argparse
from configparser import ConfigParser
import email
import platform

if __name__ == '__main__':
    exit_code = 0

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--config',
                            default='/etc/telegram-mailgate/main.cf',
                            help='use a custom configuration file')
    arg_parser.add_argument('--from',
                            help='overwrite field "From" from the header. '
                                 'Ignored if --raw is specified.')
    arg_parser.add_argument('--queue-id',
                            default=0,
                            help='specify the queue ID of the message for logging')
    arg_parser.add_argument('to',
                            nargs='+',
                            help='the recipients')
    group = arg_parser.add_mutually_exclusive_group()
    group.add_argument('--raw',
                       action='store_true',
                       help='include all sections, header and attachments')
    group.add_argument('--simple-header',
                       action='store_true',
                       help='include a header in a separate message')
    args = arg_parser.parse_args()

    cfg = ConfigParser()
    cfg.read(args.config)

    logging.config.fileConfig(cfg['core']['logging_conf_file'])
    logger = logging.getLogger()

    logger.debug('%s: Reading aliases', args.queue_id)
    aliases = open(cfg['core']['aliases'], encoding='utf8').readlines()
    aliases = dict([x.strip().split(' ') for x in aliases])

    logger.debug('%s: Validating API key', args.queue_id)
    api_key = cfg['api']['key']

    logger.debug('%s: Reading message content', args.queue_id)
    raw_content = sys.stdin.read()
    if args.raw:
        content = raw_content
    else:
        mail = email.message_from_string(raw_content)
        content = mail.get_payload()
    for rcpt in args.to:
        try:
            chat_id = aliases[rcpt]
        except KeyError as e:
            print(e)
            exit_code = 69  # EX_UNAVAILABLE
        logger.info('%s: Sending to %s(%s)', args.queue_id, chat_id, rcpt)
        if args.simple_header:
            sender = getattr(args, 'from') or mail['From']
            msg = 'New mail on {} from {}'.format(platform.node(), sender)
    exit(exit_code)
