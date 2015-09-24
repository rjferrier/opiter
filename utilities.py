"""
Note: the functions and classes in this module are *not* supported
by tests.  Consider them recipes rather than part of the source code.
"""

import os
import multiprocessing
import subprocess
import sys
import numpy
import glob

from options_iteration import OptionsArray, OptionsNode

try:
    import jinja2
    HAVE_JINJA2 = True
except:
    HAVE_JINJA2 = False



## DIAGNOSTIC FUNCTIONS

def check_entries(options_tree):
    """
    Evaluates each entry in each options dictionary in options_tree.
    Errors will be thrown for missing or invalid dependencies.
    """
    for od in options_tree.collapse():
        for key in od.keys():
            od[key]
            
def pretty_print(options_tree):
    """
    Prints options_tree in tree form.
    """
    for od in options_tree.collapse():
        print od.str(formatter='tree')


## PROCESSING FUNCTIONS

def smap(functor, options_tree, message=None):
    "Serial processing"
    functor.check_processing(False)
    options_dicts = options_tree.collapse()
    functor.preamble(options_dicts[0])
    if message:
        print '\n' + message
    else:
        print
    map(functor, options_dicts)
    functor.postamble(options_dicts[-1])
    

def pmap(functor, options_tree, message=None, nprocs_max=None,
         in_reverse=False):
    "Parallel processing"
    functor.check_processing(True)
    options_dicts = options_tree.collapse()
    nprocs = get_nprocs(len(options_dicts), nprocs_max)
    for opt in options_dicts:
        opt.freeze()
    if in_reverse:
        options_dicts.reverse()
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
            branch = options.str(formatter='tree')
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

class SimpleRendering:
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

            
class Jinja2Rendering:
    def __init__(self, configuration={}, filters={}, globals={}, tests={}):
        if not HAVE_JINJA2:
            raise Exception('jinja2 not installed; needed by this functor')
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
            self.render(source_filename, target_filename, 
                        source_dir, target_dir, opt=options)
        return operation
    

## FUNCTOR CLASSES FOR PUBLIC USE

class ExpandTemplate(SerialFunctor):
    def __init__(self, source_filename_key, target_filename_key,
                 rendering_strategy=SimpleRendering(),
                 source_dir_key=None, target_dir_key=None):
        self.source_filename_key = source_filename_key
        self.target_filename_key = target_filename_key
        self.rendering_strategy = rendering_strategy
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
            
        operation = self.rendering_strategy.get_operation(
            options, source_filename, target_filename,
            source_dir, target_dir)

        self.boilerplate(
            options, [operation], [source_filename],
            target_name=target_filename)


class RunProgram(ParallelFunctor):
    def __init__(self, command_line_arguments_key,
                 prerequisite_filenames_key, target_name_key=None,
                 working_dir_key=None, error_filename_key=None):
        self.command_line_arguments_key = command_line_arguments_key
        self.prerequisite_filenames_key = prerequisite_filenames_key
        self.target_name_key = target_name_key
        self.working_dir_key = working_dir_key
        self.error_filename_key = error_filename_key
    
    def __call__(self, options):
        subp_args = options[self.command_line_arguments_key]
        prerequisite_filenames = options[self.prerequisite_filenames_key]
        
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
            working_dir = None

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
        

            
## ALTERNATIVE CONSTRUCTORS

class OptionsArrayFactory:
    """
    Provides an OptionsArray constructor with an alternative system
    for naming the nodes.  For example, where

       OptionsArray('array1', [class1, class2])
       OptionsArray('array2', range(3))

    produces nodes named ['class1', 'class2'] and ['0', '1', '2'],

       factory = OptionsArrayFactory()
       factory('array1', [class1, class2])
       factory('array2', range(3))

    produces nodes named ['A00', 'A01'] and ['B00', 'B01', 'B02'].
    """
    def __init__(self, array_index_formatter=None, node_index_formatter=None):
        self.array_index = 0
        if not array_index_formatter:
            self.array_index_formatter = self.default_array_index_formatter
        if not node_index_formatter:
            self.node_index_formatter = self.default_node_index_formatter

    @staticmethod
    def default_array_index_formatter(i):
        "Converts 0, 1, 2,... to A, B, C,... "
        return 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'[i]

    @staticmethod
    def default_node_index_formatter(i):
        "Converts 0, 1, 2,... to 00, 01, 02,... "
        return '{:02d}'.format(i)
        
    def __call__(self, array_name, elements):
        nodes = []
        for node_index, el in enumerate(elements):
            node_name = self.array_index_formatter(self.array_index) +\
                        self.node_index_formatter(node_index)
            nodes.append(
                OptionsNode(node_name, el, array_name=array_name))

        # bump the array counter for next time
        self.array_index += 1
        return OptionsArray(array_name, nodes)


