#!/usr/bin/env python2.5

#Appengine Installer - Extracts the Python AppEngine SDK to a sensible folder structure
#    Copyright (C) 2011 Luke Benstead

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#    

from optparse import OptionParser
import sys
import os
import urllib2
import tempfile
import zipfile
import shutil

LIBRARY_LOCATIONS = {
    'google' : ('google_appengine/google', 'google'),
    'antlr3' : ('google_appengine/lib/antlr3/antlr3', 'antlr3'),
    'django_0_96' : ('google_appengine/lib/django_0_96', 'django_0_96'),
    'django_1_2' : ('google_appengine/lib/django_1_2', 'django_1_2'),
    'fancy_urllib' : ('google_appengine/lib/fancy_urllib/fancy_urllib', 'fancy_urllib'),
    'graphy' : ('google_appengine/lib/graphy/graphy', 'graphy'),
    'ipaddr' : ('google_appengine/lib/ipaddr/ipaddr', 'ipaddr'),
    'protorpc' : ('google_appengine/lib/protorpc/protorpc', 'protorpc'),
    'simplejson' : ('google_appengine/lib/simplejson/simplejson', 'simplejson'), 
    'whoosh' : ('google_appengine/lib/whoosh/whoosh', 'whoosh'),
    'webob' : ('google_appengine/lib/webob/webob', 'webob'),
    'yaml' : ('google_appengine/lib/yaml/lib/yaml', 'yaml'),
    'VERSION' : ('google_appengine/VERSION', 'VERSION'),
    'cacerts' : ('google_appengine/lib/cacerts', 'lib/cacerts')
}

def get_url(url, filename):
    resp = urllib2.urlopen(url)
    open(filename, "w").write(resp.read())

def print_warning(dest_folder):
    existing_folders = []
    
    for k in LIBRARY_LOCATIONS:
        lib_dest = os.path.join(dest_folder, LIBRARY_LOCATIONS[k][1])
        if os.path.exists(lib_dest):
            existing_folders.append(lib_dest)
            
    if existing_folders:
        print("""WARNING: The following library folders will be replaced, this may screw up your packaging system
or kill kittens. Only continue if you are sure that's what you want.

%s

Continue? Y/N""" % '\n'.join(existing_folders))
        ans = raw_input()
        if ans != 'Y':
            print("Fine. Exiting.")
            sys.exit(0)

def _download_sdk(options):
    sdk_url = "http://googleappengine.googlecode.com/files/google_appengine_%(version)s.zip"
    sdk_url = sdk_url % { 'version' : options.version }
    
    temp_dir = tempfile.gettempdir()
    dest_file = os.path.join(temp_dir, "google_appengine_%s.zip" % options.version)
    try:
        print("Downloading the SDK...")
        get_url(sdk_url, dest_file)
    except urllib2.HTTPError:
        print("Invalid SDK version")
        sys.exit(1)
        
    print("SDK downloaded.")
    return dest_file

def _unzip(zipfile, path):
    """
        Python 2.5 doesn't have extractall()
    """
    isdir = os.path.isdir
    join = os.path.join
    norm = os.path.normpath
    split = os.path.split

    for each in zipfile.namelist():
        if not each.endswith('/'):
            root, name = split(each)
            directory = norm(join(path, root))
            if not isdir(directory):
                os.makedirs(directory)
            file(join(directory, name), 'wb').write(zipfile.read(each))

def _extract_sdk(zip_filename):
    print("Extracting SDK...")
    z = zipfile.ZipFile(zip_filename, 'r')
    dest = os.path.dirname(zip_filename)
    _unzip(z, dest)
    
    if not os.path.isdir(os.path.join(dest, "google_appengine")):
        print("Zip file doesn't have the expected structure, the format may have changed.")
        sys.exit(2)

def _install_folders(source_dir, options):
    for k in LIBRARY_LOCATIONS:
        lib_source = os.path.join(source_dir, LIBRARY_LOCATIONS[k][0])
        lib_dest = os.path.join(options.dest_dir, LIBRARY_LOCATIONS[k][1])
        assert os.path.exists(lib_source), "Couldn't find library in zip %s" % lib_source

        if os.path.isdir(lib_source):
            if os.path.exists(lib_dest):
                shutil.rmtree(lib_dest)

            print("Installing %s to %s" % (k, lib_dest))
            shutil.copytree(lib_source, lib_dest)
        else:
            shutil.copyfile(lib_source, lib_dest)

def _check_path(dest):
    if not dest in sys.path:
        print("""Install complete. 

The installation path (%s) does not exist on your PATH. You'll need to add this manually.
""" % dest)

def run(options, args):
    assert options.version, "You must specify a version of the SDK to download"
    assert options.dest_dir, "No destination directory - not even a default.. WTF?"
    
    zip_file = _download_sdk(options)
    _extract_sdk(zip_file)
    _install_folders(os.path.dirname(zip_file), options)
    
    _check_path(options.dest_dir)
    return 0


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-v", "--version", dest="version")
    parser.add_option("-d", "--destination_dir", dest="dest_dir", default="/usr/local/lib/python2.5/site-packages")
    
    options, args = parser.parse_args()
    
    print_warning(options.dest_dir)
    
    sys.exit(run(options, args))
    

