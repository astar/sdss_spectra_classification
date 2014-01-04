#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys
import time
import logging
import inspect
import subprocess
import datetime as dt
from google.protobuf import text_format
from google.protobuf.internal.containers import RepeatedScalarFieldContainer

try:
    sys.path += eval(os.environ['GAUSSTESTMODULEPATH']).split(':')
except:
    pass
sys.path.append('common')





class Glopt(object):

    """
    glopt = logging and option for gauss project

    """
    logger = None
    output_redirected = False

    def __init__(self, prg, args, debug, config_file):
        """
        prg = name of the program
        args = args from docopt
        debug = debug option [True/False]
        config_file = protobufer config file
        """
        Glopt.prg = prg
        Glopt.args = args
        Glopt.output_redirected = False
        Glopt.logger = logging.getLogger(self.prg)

        Glopt.is_debug = False
        if Glopt.decode_debug(debug) == logging.DEBUG:
            Glopt.is_debug = True

        Glopt.msg = None
        level = Glopt.decode_debug(debug)
        Glopt.logger.setLevel(level)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        Glopt.logger.setLevel(Glopt.decode_debug(debug))
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = MultiLineFormatter('%(asctime)s.%(msecs).03d %(process)d %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        ch.setFormatter(formatter)
        Glopt.logger.addHandler(ch)

        if config_file:
            Glopt.msg = config_pb2.MsgConfig()
            Glopt.read_config(config_file)



    @staticmethod
    def decode_debug(level):
        return {
            0: logging.NOTSET,
            1: logging.INFO,
            2: logging.DEBUG
        }.get(level, logging.DEBUG)



    @staticmethod
    def encode_debug(debug):
        return {
            0: '',
            1: '-D',
            2: '-DD'
        }.get(debug, '-DD')



    @staticmethod
    def read_config(config_file):
        try:
            text_format.Merge(file(config_file).read(), Glopt.msg)
        except Exception as e:
            Glopt.error("Wrong --config '{}': {}".format(config_file, e))



    @staticmethod
    def update_config(config_file, key, value, new_file=None):
        if not value:
            Glopt.debug("No value for key: {} (not an error)".format(key))
            return False
        # if ne_file is not specified just update original file
        if not new_file:
            new_file = config_file
        new_msg = config_pb2.MsgConfig()
        try:
            old_msg_txt = file(config_file).read()
            text_format.Merge(old_msg_txt, new_msg)
        except Exception, e:
            Glopt.fatal("ERROR: Wrong --config '{}': {}\n".format(config_file, e))

        whole_key = 'new_msg.' + key
        whole_key_eval = eval(whole_key)
        #check type
        Glopt.debug("Key: {} is type: {}".format(key, type(whole_key_eval)))
        if isinstance(whole_key_eval, RepeatedScalarFieldContainer):
            for item in value:
                whole_key_eval.append(item)
        elif isinstance(whole_key_eval, float):
            exp = "{} = {}".format(whole_key, value)
            Glopt.exec_exp(exp, new_msg)
        elif isinstance(whole_key_eval, unicode):
            exp = "{} = {}".format(whole_key, '\"{}\"'.format(value))
            Glopt.exec_exp(exp, new_msg)
        else:
            Glopt.fatal("Unknown type of key: {}, type {} : {}".format(whole_key, type(whole_key, e)))

        Glopt.save_file(new_file, new_msg)

    @staticmethod
    def save_file(filename, msg):
        Glopt.debug("going to write filename: {}".format(filename))
        try:
            with open(filename, 'w') as f:
                f.write(str(msg))
                Glopt.debug("Succesfully wrote to file {}".format(filename))
        except Exception, e:
            Glopt.fatal("Cannot write to file '{}': {}".format(filename, e))

    @staticmethod
    def exec_exp(exp, new_msg):
        try:
            exec(exp)
            Glopt.debug("Succesfully execute expresion   {}".format(exp))
        except Exception, e:
            Glopt.error("ERROR: Cannot execute expresion {} : {}\n".format(exp, e))



    @staticmethod
    def get_opt(opt_name, proto_name, default=None):
        if Glopt.logger:
            Glopt.logger.debug("OPT '{}'".format(opt_name))

        opt = default
        if Glopt.logger:
            Glopt.logger.debug("OPT    default: '{}'".format(opt))

        if Glopt.msg and proto_name:
            try:
                opt = eval('Glopt.msg.{}'.format(proto_name))
                if Glopt.logger:
                    Glopt.logger.debug("OPT    proto Glopt.msg.{}: '{}'".format(proto_name, opt))
            except Exception as e:
                Glopt.error("Option not set name: {}: {}".format(proto_name, e))

        if opt_name:
            if '--' + opt_name in Glopt.args:
                if Glopt.args['--' + opt_name] is not None:
                    opt = Glopt.args['--' + opt_name]
                    if Glopt.logger:
                        Glopt.logger.debug("OPT    cmd --{}: '{}'".format(opt_name, opt))

        if Glopt.logger:
            Glopt.logger.debug("OPT    final: '{}'".format(opt))

        return opt


    @staticmethod
    def run_cmd(cmd, **qwargs):

        can_failed_without_an_error = qwargs.get('can_failed_without_an_error', False)

        try:
            with Timer('going to run (can_failed:{}): {}'.format(int(can_failed_without_an_error), str(cmd))):
                proc = subprocess.Popen(cmd)
                proc.wait()
                if proc.returncode and (not can_failed_without_an_error):
                    Glopt.error('ERROR: execution failed (return code: {}): {}'.format(proc.returncode, str(cmd)))
        except Exception, e:
            Glopt.error("ERROR: execution failed: ({}): ".format(str(cmd), e))



    @staticmethod
    def debug(msg, **kwargs):
        Glopt.logger.debug(Glopt.log_msg(msg, **kwargs))


    @staticmethod
    def info(msg, **kwargs):
        Glopt.logger.info(Glopt.log_msg(msg, **kwargs))



    @staticmethod
    def warning(msg, **kwargs):
        Glopt.logger.warning(Glopt.log_msg(msg, **kwargs))



    @staticmethod
    def error(msg, **kwargs):
        Glopt.logger.error(Glopt.log_msg(msg, **kwargs))



    @staticmethod
    def fatal(msg, **kwargs):
        Glopt.logger.fatal(Glopt.log_msg(msg, **kwargs))
        sys.stderr.write('CRITICAL: '+msg+'\n')
        os._exit(1)



    @staticmethod
    def log_msg(msg, **kwargs):

        obj = kwargs.get('self')
        uuid = kwargs.get('uuid')
        name = getattr(kwargs.get('self'), 'name', '')
        caller = kwargs.get('caller', None)

        if name:
            name = name + '@'

        msg_prefix = ''
        if obj:
            msg_prefix += '[{}{}]'.format(name, obj.__class__.__name__)
        if uuid:
            msg_prefix += '[{}]'.format(uuid)
        if msg_prefix:
            msg_prefix += ' '

        if caller:
            return '{}: {}BFLMPSVZ_prefix{}'.format(caller, msg_prefix, str(msg))
        else:
            return 'BFLMPSVZ_script:BFLMPSVZ_lineno:BFLMPSVZ_fce(): {}BFLMPSVZ_prefix{}'.format(msg_prefix, str(msg))



class Timer(object):

    def __init__(self, msg=''):
        self.msg = msg

    def __enter__(self):
        if Glopt.logger:
            if Glopt.logger.isEnabledFor(logging.DEBUG):
                if self.msg:
                    Glopt.logger.debug("Timer has started ({})".format(self.msg))
                else:
                    Glopt.logger.debug("Timer has started".format(self.msg))
                self.start = time.time()

    def __exit__(self, type, value, traceback):
        if Glopt.logger:
            if Glopt.logger.isEnabledFor(logging.DEBUG):
                elapsed = time.time() - self.start
                if self.msg:
                    end_msg = "Timer has ended ({}) Elapsed time: {}".format(self.msg, str(dt.timedelta(seconds=elapsed)))
                else:
                    end_msg = "Elapsed time: {}".format(str(dt.timedelta(seconds=elapsed)))
                Glopt.logger.debug(end_msg)


class MultiLineFormatter(logging.Formatter):


    def format(self, record):

        whole = logging.Formatter.format(self, record)
        header, NULL = whole.split(record.message)

        current = inspect.currentframe().f_back.f_back.f_back.f_back.f_back.f_back.f_back.f_back.f_back
        calling_fce = current.f_code.co_name
        calling_fn = current.f_code.co_filename
        calling_lineno = current.f_lineno
        script_name = os.path.basename(calling_fn)
        if script_name.endswith('.pyc') and os.path.exists(calling_fn[:-1]):
            script_name = script_name[:-1]

        posfix_header = ''
        real_msg = record.message
        try:
            posfix_header, real_msg = record.message.split('BFLMPSVZ_prefix', 1)
        except:
            pass

        record.message = real_msg
        header = header+posfix_header

        header = header.replace('BFLMPSVZ_script', script_name, 1)
        header = header.replace('BFLMPSVZ_fce', calling_fce, 1)
        header = header.replace('BFLMPSVZ_lineno', str(calling_lineno), 1)

        to_output = [it for it in record.message.split('\n') if it]
        return header + ('\n' + header).join(to_output)



def test():

    print "This is ment to be imported. Running tests\n"

    from glopt import Glopt

    # debug is
    # 0 no logs
    # 1 info or more
    # 2 all
    debug = 2
    Glopt(None, None, debug, None)

    class A(object):
        def __init__(self, name):
            self.name = name

    class B(object):
        def __init__(self):
            pass

    a = A(name='kokot')
    b = B()

    Glopt.debug('Dada je sexy;-)', self=b)
    Glopt.info('fatal error', self=a)
    Glopt.warning('Dada je sexy;-)', caller='kokutek.py:22:fce()')
    Glopt.error('Dada je sexy;-)', uuid='666')
    Glopt.error('Dada je sexy;-)', self=a, uuid='666', caller='kokutek.py:22:fce()')

    Glopt.debug('line1\nline', self=b)
    Glopt.info('fatal error', self=a)
    Glopt.warning('line1\nline2', caller='kokutek.py:22:fce()')
    Glopt.error('line1\nline2', uuid='666')
    Glopt.error('line1\nline2', self=a, uuid='666', caller='kokutek.py:22:fce()')

    Glopt.fatal('fatal error')

if __name__ == '__main__':
    test()



# vim: set cin et ts=4 sw=4 ft=python :
