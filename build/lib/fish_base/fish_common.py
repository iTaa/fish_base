# 2016.4.1 create fish_common.py by david.yi
# 2016.4.3 edit FishCache class, and edit get_cf_cache
# 2016.4.7 v1.0.6, v1.0.7  add get_long_filename_with_sub_dir()
# 2016.10.4 v1.0.9 add #19001 check_sub_path_create()
# 2017.1.8 v1.0.9 #19003, remove file related functions to fish_file.py
import sys
import uuid
import configparser
import re
import hashlib
import os


# 2017.2.13 #19006
# 通过调用os.platform来获得当前操作系统名称
def check_platform():
    if sys.platform == 'win32':
        return 'win32'
    elif sys.platform == 'darwin':
        return 'macos'
    elif sys.platform == 'linux':
        return 'linux'
    else:
        return sys.platform


# md5 函数
# 2015.5.27 create by david.yi
# 2015.6.6 edit, 转移到这里，作为基本工具函数
# 2018.6.8 edit by chunying.jia, 添加文件、大文件MD5的获取功能
# 输入: s: str 字符串
# 输出: 经过md5计算的值
def get_md5(string, mode='S'):
    """
    获取MD5方法
    :param string: 待hash的字符串，或者是文件的路径，
                如果是文件路径的时候需要设置mode='F'
    :param mode: 模式，'S', 获取字符串的MD5
                'F', 传入的str需要是文件的路径
                'B', 大文件的MD5,传入的str需要是文件的路径
    :return: 32位小写MD5值
    """
    if mode.upper() == 'S':
        return _get_str_md5(string)
    if mode.upper() == 'F':
        return _get_file_md5(string)
    if mode.upper() == 'B':
        return _get_big_file_md5(string)


def _get_str_md5(string):
    """
    获取一个字符串的MD5值
    :param string 待hash的字符串
    :return: 32位小写MD5值
    """
    m0 = hashlib.md5()
    m0.update(string.encode('utf-8'))
    result = m0.hexdigest()
    return result


def _get_file_md5(file_path):
    """
    获取一个文件的MD5值
    :param file_path 待hash的文件路径
    :return: 32位小写MD5值
    """
    with open(file_path, 'rb') as f:
        md5obj = hashlib.md5()
        md5obj.update(f.read())
        hash_o = md5obj.hexdigest()
        return hash_o


def _get_big_file_md5(file_name):
    """
    获取一个较大文件的MD5值
    :param file_name 待hash的文件路径
    :return: 32位小写MD5值
    """
    if not os.path.isfile(file_name):
        return
    hash_o = hashlib.md5()
    f = open(file_name, 'rb')
    while True:
        b = f.read(8096)
        if not b:
            break
        hash_o.update(b)
    f.close()
    return hash_o.hexdigest()


# 对象序列化
# 2015.6.14  edit by david.yi
# 输入: info: 要显示的字段解释，field_default：默认的字段名称
# 输出: 字段名称
def serialize_instance(obj):
    d = {'__classname__': type(obj).__name__}
    d.update(vars(obj))
    return d


# 功能：获取带时间戳的流水号
# 2017.2.22, create by David.Yi, #19006,
# 输入参数：无
# 输出参数：流水号（string)
def get_time_uuid():
    # Generate a UUID from a host ID, sequence number, and the current time.
    # If node is not given, getnode() is used to obtain the hardware address.
    # If clock_seq is given, it is used as the sequence number; otherwise a random 14-bit sequence number is chosen.
    return str(uuid.uuid1())


# 功能：判断参数列表是否存在不合法的参数，如果存在None或空字符串或空格字符串，则返回True, 否则返回False
# 2017.2.22 edit by David.Yi, #19007
# 输入参数：source 是参数列表或元组
# 输出参数：True : 有元素为 None，或空； False：没有元素为 None 或空
def if_any_elements_is_space(source):
    for i in source:
        if not (i and str(i).strip()):
            return True
    return False


# 2017.2.23 create by David.Yi, #19008
# 读入配置文件，返回根据配置文件内容生成的字典类型变量
# 输入： conf 文件长文件名
def conf_as_dict(conf_filename):

    cf = configparser.ConfigParser()

    cf.read(conf_filename)

    d = dict(cf._sections)
    for k in d:
        d[k] = dict(cf._defaults, **d[k])
        d[k].pop('__name__', None)

    return d


# r2c1 v1.0.1 #12089
# 2016.4.3 edit class and function name
# 通过conf文件。eg ini，读取值，通过字典缓存来提高读取速度
class FishCache:
    __cache = {}

    def get_cf_cache(self, cf, section, key):
        # 生成 key，用于 dict
        temp_key = section + '_' + key

        if not (temp_key in self.__cache):
            self.__cache[temp_key] = cf[section][key]

        return self.__cache[temp_key]


# 2017.3.30 create by Leo #11001
# 功能：监测list或者元素是否含有特殊字符
# 输入：source 是参数列表或元组
# 输出：True：不包含特殊字符；False：包含特殊字符
def if_any_elements_is_special(source):

    if not re.match('^[a-zA-Z0-9_,-.|]+$', "".join(source)):
            return False

    return True


# 2017.3.30 create by Leo #11003
# 功能：监测list或者元素是否只包含数字
# 输入：source 是参数列表或元组
# 输出：True：只包含数字；False：不只包含数字
def if_any_elements_is_number(source):

    for i in source:

        if not i.isdigit():
            return False

    return True


# 2017.3.30 create by Leo #11004
# 功能：监测list或者元素是否只包含英文
# 输入：source 是参数列表或元组
# 输出：True：只包含英文；False：不只包含英文
def if_any_elements_is_letter(source):

    for i in source:

        if not i.isalpha():
            return False

    return True
