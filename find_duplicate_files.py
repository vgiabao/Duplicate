#!/bin/python3
from argparse import ArgumentParser
from hashlib import md5
from json import dumps
from os import walk, stat
from os.path import join, expanduser, islink


def handle_parser():
    '''
    handle the command line interface
    '''
    parser = ArgumentParser()
    parser.add_argument('-p', '--path', help='whatever-directory',
                        metavar='filename', required=True)
    return parser.parse_args()


def handle_tilde(path_name):
    '''
    execute file if have '~'
    :param path_name: initial path
    :return: handled paths
    '''

    file_name = expanduser(path_name)
    return path_name


def scan_file_module(path_name):
    '''
    scan all files in given path
    :param path_name: given path
    :return: list of all files
    '''
    path_name = handle_tilde(path_name)
    current_list = []
    # check the type of given path, give blank result if not string
    if not isinstance(path_name, str):
        return []
    # check all file in the given path, append to list result
    for root, _, files in walk(path_name):
        for name in files:
            if not islink(join(root, name)):
                current_list.append(join(root, name))
    return current_list


def group_file_by_size(file_path_name):
    '''
    given the files bear close volume in size
    :param file_path_name: list of paths
    :return: list path have similar size
    '''
    dir = {}
    current_list = []
    # read the size of all provided files
    for abs_path in file_path_name:
        size_group = str(stat(abs_path).st_size)
        if size_group is not '0':
            if size_group not in dir:
                dir[size_group] = [abs_path]
            else:
                dir[size_group] += [abs_path]
    # append list of duplicate file to result list
    for item in dir:
        if len(dir[item]) >= 2:
            current_list.append(dir[item])
    return current_list


def get_check_sum(path):
    '''
    check the  md5 hash array of a file
    :param path: path of file
    :return: md5 hash
    '''
    m = md5()
    try:
        m.update(open(path, 'rb').read())
    except (OSError, PermissionError):
        pass
    return m.hexdigest()


def group_file_by_checksum(file_path_name):
    '''
    group the file which have same md5 hash in a result list
    :param file_path_name: list of paths
    :return: group of files has similar md5 hash
    '''
    dic = {}
    current_list = []
    # check path in given list and add them in dic with md5 hash = key and
    # path name is value.
    for path in file_path_name:
        seri = str(get_check_sum(path))
        if seri:
            if seri not in dic:
                dic[seri] = [path]
            else:
                dic[seri] += [path]
    # append group of file which is similar in md5 hash in a list
    for item in dic:
        if len(dic[item]) >= 2:
            current_list.append(dic[item])
    return current_list


def find_duplicate_files(file_path_name):
    '''
    find duplicate file depend on their size and md5 hash
    :param file_path_name: list of file
    :return: the list containing duplicate files
    '''
    list_size = group_file_by_size(file_path_name)
    list_seri = group_file_by_checksum(file_path_name)
    optimized_list = []
    # take the union
    for element in list_size:
        if element in list_seri:
            optimized_list.append(element)
    return optimized_list


def main():
    rootdir = handle_parser().path
    print(dumps(find_duplicate_files(scan_file_module(rootdir)),
                separators=('\n','')))


if __name__ == '__main__':
    main()
