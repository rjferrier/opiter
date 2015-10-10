"""
Note: the functions and classes in this module are *not* supported
by tests.  Consider them recipes rather than part of the source code.
"""

import os
import multiprocessing
import subprocess
import sys
from options_dict import Sequence, unlink, Check, Remove, \
    unpicklable, missing_dependencies

try:
    import jinja2
    HAVE_JINJA2 = True
except:
    HAVE_JINJA2 = False

    
## DIAGNOSTIC FUNCTIONS

def pretty_print(options_tree, keys=[]):
    """
    Prints options_tree in tree form and optionally the values
    corresponding to some keys.
    """
    if isinstance(keys, str):
        keys = [keys]
    for od in options_tree.collapse():
        print od.get_string(formatter='tree')
        for k in keys:
            print '{}{}: {}'.format(od.indent(), k, od[k])


## PROCESSING FUNCTIONS

def smap(functor, options_tree, message=None, dict_hooks=[], item_hooks=[]):
    """
    Serial processing.  The user may specify custom transformations on
    the items in the preprocessing list (e.g. [unlink]).
    """
    functor.check_processing(False)
    options_dicts = options_tree.collapse()

    # apply hooks
    for opt in options_dicts:
        for func in dict_hooks:
            func(opt)
        opt.transform_items(Sequence(item_hooks), recursive=True)

    # processing
    functor.preamble(options_dicts[0])
    if message:
        print '\n' + message
    else:
        print
    map(functor, options_dicts)
    functor.postamble(options_dicts[-1])
    

def pmap(functor, options_tree, message=None, nprocs_max=None,
         in_reverse=False, dict_hooks=[], item_hooks=[
             Check(missing_dependencies), unlink, Check(unpicklable)]):
    """
    Parallel processing.

    Default preprocessing functions that are applied to each item
    include checking for missing dependencies, unlinking, and checking
    that the item is picklable.  The user may remove the checks by
    supplying an empty preprocessing argument, but unlinking will
    always be performed since dependent items cause pickling
    problems.
    """
    
    functor.check_processing(True)
    options_dicts = options_tree.collapse()
    nprocs = get_nprocs(len(options_dicts), nprocs_max)

    # default and apply hooks
    if unlink not in preprocessing:
        preprocessing.append(unlink)
    for opt in options_dicts:
        for func in dict_hooks:
            func(opt)
        opt.transform_items(Sequence(item_hooks), recursive=True)

    if in_reverse:
        options_dicts.reverse()
        
    # processing
    functor.preamble(options_dicts[0])
    p = multiprocessing.Pool(nprocs)
    if message:
        print '\n{} with {} processor(s)'.format(message, nprocs)
    else:
        print '\nWith {} processor(s)'.format(nprocs)
    p.map(functor, options_dicts)
    p.close()
    functor.postamble(options_dicts[-1])


## HELPERS

def get_nprocs(iterable_length, nprocs_max=None):
    """
    Returns an appropriate number of processors to be used for
    multiprocessing.
    """
    nprocs = os.getenv('NPROC')
    if not nprocs:
        nprocs = multiprocessing.cpu_count()
    if nprocs_max:
        nprocs = min(nprocs, nprocs_max)        
    nprocs = min(nprocs, iterable_length)
    return nprocs

class State:
    def __init__(self, msg=''):
        self.msg = msg
    def __str__(self):
        return self.msg

class Success(State):
    successful = True
        
class Failure(State, Exception):
    successful = False
    
def check_file_exists(input_filename):
    if input_filename:
        if not os.path.isfile(input_filename):
            raise Failure(input_filename
    + " not found")

class ChDir:
    "Context manager that temporarily changes working directory"
    def __init__(self, new_path):
        self.new_path = os.path.expanduser(new_path)
    def __enter__(self):
        self.saved_path = os.getcwd()
        os.chdir(self.new_path)
    def __exit__(self, etype, value, traceback):
        os.chdir(self.saved_path)


## FUNCTOR BASE CLASSES

class Functor:
    """
    Do not subclass me; subclass SerialFunctor or ParallelFunctor
    instead.
    """
    def preamble(self, options):
        "Code to be executed before iteration"
        pass
    
    def postamble(self, options):
        "Code to be executed after iteration"
        pass
        
    def boilerplate(self, options, operations, dependencies=[], 
                    target_name=''):
        self.print_start(target_name, options)
        if isinstance(dependencies, str):
            dependencies = [dependencies]
        try:
            for dep in dependencies:
                check_file_exists(dep)
            for op in operations:
                op()
            state = Success(target_name)
        except Failure as state:
            pass
        self.print_end(state, options)
            
        
class SerialFunctor(Functor):
    "Subclass me."
    
    @staticmethod
    def check_processing(in_parallel):
        class ProcessingError(Exception):
            def __str__(self):
                return 'this functor is designed to be run in serial only.'
        if in_parallel:
            raise ProcessingError()

    def print_start(self, state, options=None, target=sys.stdout):
        pass

    def print_end(self, state, options=None, target=sys.stdout):
        msg = str(state)
        if options:
            if msg and '\n' not in msg:
                # assume successful unless proven otherwise
                sep = ' -> '
                try:
                    if not state.successful:
                        # failure
                        sep = ' -- '
                except AttributeError:
                    pass
            else:
                sep = ''
                msg = msg.replace('\n', '\n' + options.indent())
            branch = options.get_string(formatter='tree')
            target.write(branch + sep + msg + '\n')
        else:
            if msg:
                target.write(msg + '\n')
        
            
class ParallelFunctor(Functor):
    "Subclass me."
    
    @staticmethod
    def check_processing(in_parallel):
        # designed to be run either in serial or parallel
        pass

    def print_start(self, state, options=None, target=sys.stdout):
        msg = str(state)
        if msg:
            target.write(" "*4 + msg + ' ...\n')

    def print_end(self, state, options=None, target=sys.stdout):
        msg = str(state)
        # assume successful unless proven otherwise
        intro = 'finished '
        try:
            if not state.successful:
                # failure
                intro = ''
        except AttributeError:
            pass
        if msg:
            target.write(" "*8 + intro + msg + '\n')


## FUNCTOR HELPERS

class SimpleTemplateEngine:
    def __init__(self, nloops=1):
        self.nloops = nloops

    def get_operation(self, options, source_filename, target_filename,
                      source_dir, target_dir):
        "Creates and returns a closure that can be executed with no args"

        def operation():
            with open('{}/{}'.format(source_dir, source_filename), 'r') as src:
                buf = src.read()
                buf = options.expand_template_string(buf, self.nloops)
            with open('{}/{}'.format(target_dir, target_filename), 'w') as tgt:
                tgt.write(buf)

        return operation

            
class Jinja2TemplateEngine:
    def __init__(self, configuration={}, filters={}, globals={}, tests={}):
        if not HAVE_JINJA2:
            raise Exception('jinja2 not installed')
        # default configuration
        self.configuration = {'trim_blocks': True,
                              'lstrip_blocks': True,
                              'undefined': jinja2.StrictUndefined}
        self.configuration.update(configuration)
        self.filters = filters
        self.globals = globals
        self.tests = tests

    def render(self, source_filename, target_filename, source_dir,
               target_dir, **kwargs):
        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(source_dir),
            **self.configuration)
        env.filters.update(self.filters)
        env.globals.update(self.globals)
        env.tests.update(self.tests)
        template = env.get_template(source_filename)
        with open('{}/{}'.format(target_dir, target_filename), 'w') as f:
            f.write(template.render(kwargs))
            
    def get_operation(self, options, source_filename, target_filename, 
                      source_dir, target_dir):
        "Creates and returns a closure that can be executed with no args"
        
        def operation():
            # need to convert the nonstandard dictionary items
            # otherwise jinja2 will get confused
            options.transform_items(unlink, recursive=True)
            self.render(source_filename, target_filename, 
                        source_dir, target_dir, **options)
            
        return operation

    
## FUNCTOR CLASSES FOR PUBLIC USE

class ExpandTemplate(SerialFunctor):
    def __init__(self, source_filename_key, target_filename_key,
                 engine=SimpleTemplateEngine(), source_dir_key=None,
                 target_dir_key=None):
        self.source_filename_key = source_filename_key
        self.target_filename_key = target_filename_key
        self.engine = engine
        self.source_dir_key = source_dir_key
        self.target_dir_key = target_dir_key

    def __call__(self, options):
        source_filename = options[self.source_filename_key]
        target_filename = options[self.target_filename_key]

        if self.source_dir_key:
            source_dir = options[self.source_dir_key]
        else:
            source_dir = '.'

        if self.target_dir_key:
            target_dir = options[self.target_dir_key]
        else:
            target_dir = '.'
            
        operation = self.engine.get_operation(
            options, source_filename, target_filename,
            source_dir, target_dir)

        self.boilerplate(
            options, [operation], [source_filename],
            target_name=target_filename)


class RunProgram(ParallelFunctor):
    def __init__(self, command_line_arguments_key,
                 prerequisite_filenames_key=None, target_name_key=None,
                 working_dir_key=None, error_filename_key=None):
        self.command_line_arguments_key = command_line_arguments_key
        self.prerequisite_filenames_key = prerequisite_filenames_key
        self.target_name_key = target_name_key
        self.working_dir_key = working_dir_key
        self.error_filename_key = error_filename_key
    
    def __call__(self, options):
        subp_args = options[self.command_line_arguments_key]
        if self.prerequisite_filenames_key:
            prerequisite_filenames = options[self.prerequisite_filenames_key]
        else:
            prerequisite_filenames = []
            
        if self.target_name_key:
            target_name = options[self.target_name_key]
        else:
            target_name = ' '.join(subp_args)
            
        if self.error_filename_key:
            error_filename = options[self.error_filename_key]
        elif self.target_name_key:
            error_filename = target_name + '.err'
        else:
            error_filename = None

        # WARNING: working_dir doesn't seem to be respected.  To be
        # investigated.
        if self.working_dir_key:
            working_dir = options[self.working_dir_key]
        else:
            working_dir = '.'

        with ChDir(working_dir):
            def operation():
                if error_filename:
                    try:
                        with open(error_filename, 'w') as err_file:
                            subprocess.check_output(subp_args, stderr=err_file)
                    except subprocess.CalledProcessError as e:
                        raise Failure('FAILURE: see ' + error_filename)
                    os.remove(error_filename)
                else:
                    subprocess.check_output(subp_args)
        
            self.boilerplate(
                options, [operation], prerequisite_filenames,
                target_name=target_name)
        
