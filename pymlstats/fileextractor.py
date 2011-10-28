# Copyright (C) 2007-2010 GSyC/LibreSoft Group
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# Authors : GSyC/LibreSoft Group <libresoft-tools-devel@lists.morfeo-project.org>
#

"""
File Extractor Module

@author:       GSyC/LibreSoft Group
@organization: GSyC/LibreSoft Group, Universidad Rey Juan Carlos
@copyright:    GSyC/LibreSoft Group
@license:      GNU GPL version 2 or any later version
@contact:      libresoft-tools-devel@lists.morfeo-project.org
"""

import os
import sys

# Extraction modules
import tarfile
import zipfile
import gzip
import bz2

class FileExtractorError(Exception):
    """
    Raised if an error occurs during the extraction process
    """
    
    def __init__(self, message):
        self.message = message



class FileExtractor:
    """
    The intention of this class is to provide an easy way to extract, decompress and access
    to the files stored in any kind of containers such as zips, tars and so on.
    """

    def gzExtraction(self, filename):
        """
        Extracts the contents of a gz file
           
        @param filename: path to gz file to be extracted
        @return: the path to the file that has been extracted
        """
        gzipfile = gzip.GzipFile(filename,mode='r')
        outputfilename, ext = os.path.splitext(filename)
        # If the extension is different than gz,
        # add this to avoid using the same output
        # filename than the original file
        if '.gz' != ext.lower():
            outputfilename = filename + '.extracted'

        outputfileobj = open(outputfilename,'w')
        outputfileobj.write(gzipfile.read())
        gzipfile.close()
        outputfileobj.close()

        return outputfilename

    def bz2Extraction(self, filename):
        """
        Extracts the contents of a bz2 file
           
        @param filename: path to bz2 file to be extracted
        @return: the path to the file that has been extracted
        """
        bz2file = bz2.BZ2File(filename,mode='r')
        outputfilename, ext = os.path.splitext(filename)
        # If the extension is different than bz2,
        # add this to avoid using the same output
        # filename than the original file
        if '.bz2' != ext.lower():
            outputfilename = filename + '.extracted'

        outputfileobj = open(outputfilename,'w')
        outputfileobj.write(bz2file.read())
        bz2file.close()
        outputfileobj.close()

        return outputfilename
        
    
    def tarExtraction (self, filename):
        """
        Extracts the contents of a tar file
           
        @param filename: path to tar file to be extracted
        @return: list with the paths of the files or directories extracted
        """   
        
        extracted_list = []
        path = os.path.dirname(filename)
        
        try:
            tar = tarfile.open(filename, "r")
        except tarfile.TarError:
            raise FileExtractorError("FileExtractor Error: Opening tarfile %s" % filename)
        
        for tarinfo in tar:
            try:
                tar.extract(tarinfo, path)
                extracted_list.append(os.path.join(path, tarinfo.name))
            except tarfile.TarError:
                tar.close()
                raise FileExtractorError("FileExtractor Error: Extracting tarfile %s" % filename)          
            
        tar.close()
        
        return extracted_list
    

    def zipExtraction (self, filename):
        """
        Extracts the contents of a zip file
        
        @param filename: path to zip file to be extracted
        @return: list with the paths of the files or directories extracted
        """
        
        extracted_list = [] 
        path = os.path.dirname(filename)
        
        try:
            zipped = zipfile.ZipFile(filename, "r")
        except zipfile.BadZipfile:
            raise FileExtractorError("FileExtractor Error: Opening zipfile %s" % filename)
            
        for name in zipped.namelist():
            try:
                bytes_in = zipped.read(name)
                filepath = os.path.join(path, name)
                # Check that subdirectories exist
                # If subdirectories do not exist, the creation of the file will fail
                subdirectory = os.path.dirname(filepath)
                if not os.path.exists(subdirectory):
                    os.makedirs(subdirectory)
                    
                f = open(filepath, 'w')
                
                try:
                    f.write(bytes_in)
                finally:
                    f.close()         
                            
            except zipfile.BadZipfile:
                zipped.close()
                raise FileExtractorError('FileExtractor Error: Reading %s zipfile' % filename)
            except IOError:
                zipped.close()
                raise FileExtractorError('FileExtractor Error: Write error while extracting %s zipfile' % filename)
        
            extracted_list.append(filepath)
        
        zipped.close()
                
        return extracted_list
        
            
    def extract (self, path_list):
        """
        Extract all the files included into a file container. If the container
        includes container files, these will be extracted too. If the container
        is a directory, the algorithm will search in its contents for other
        container files to perform the extraction.
        
        The algorithm is the next:
        
            Input:  path list of directories and files to extract
            Output: extracted files
            
            Steps:
            
                - Generate a LIFO list that will contains the path to files or directories containers.
                  Add the list of paths to the LIFO list.
                
                - Do until the list isn't be empty:
                
                  1) Take the last element and delete it from the list
                  
                  2) Check if the path belongs to a file or a directory
                  
                     a) If the element is a directory:
                        a.1) Add the elements than contains the directory at the end of the list
                             
                     b) If the element is a file:
                        b.1) Check if the file is a supported container (i.e tar, zip, deb, rpm, and so on)
                        b.2) If it's supported:
                             b.2.1) extract
                             b.2.2) for each extracted element, add its path to the end of the list
                             
                  3) Goto loop's start
        
        @param path_list: list with paths of files or directories to be extracted
        @return: list with directories or files extracted        
        """
        
        extracted_list = []
        container_list = []
        container_list.extend(path_list)
        
        while len(container_list) > 0:
            container = container_list.pop()
            extracted_list.append(container)
            
            if os.path.exists(container):
                if os.path.isdir(container):
                    file_list = os.listdir(container)
                    
                    for filename in file_list:
                        filename = os.path.join(container, filename)
                        container_list.append(filename)
                              
                else:
                    if tarfile.is_tarfile(container):
                        try:
                            ext_list = self.tarExtraction(container)
                        except:
                            raise
                        else:
                            container_list.extend(ext_list)
                            
                    elif zipfile.is_zipfile(container):
                        try:
                            ext_list = self.zipExtraction(container)
                        except:
                            raise
                        else:
                            container_list.extend(ext_list)
                            
                    else:
                        print "FileExtractor: %s extraction ignored" % container
                
            else:
                raise FileExtractorError("FileExtractor Error: %s not found" % container)

        return extracted_list


if __name__ == "__main__":
    
    container_list = ["/tmp/test"]
    fe = FileExtractor()
    
    try:
        extracted_list = fe.extract(container_list)
        print str(extracted_list)
    except FileExtractorError, e:
        print >>sys.stderr, e.message
    else:
        print "Extraction completed"

