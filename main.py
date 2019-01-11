'''
This file is part of cats_client.

cats_client is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

cats_client is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with cats_client.  If not, see <https://www.gnu.org/licenses/>.
'''

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import socket

#path is type of observer that makes path entry and filechooser button have same value
class Path:
	def __init__(self):
		self.__value=''
	def add_observable(self,widgets):
		self.__widgets=widgets
	def set_path(self,path):
		self.__value=path
		for w in self.__widgets:
			w.set_path(self.__value)
	def get_path(self):
		return self.__value

#three wrappers over Gtk widgets
class PathButton:
    def __init__(self,button,path):
        self.__widget=button
        self.__path=path
        self.__widget.connect('file-set',self.__onValueChange)
    def __onValueChange(self,widget):
        self.__path.set_path(self.__widget.get_filename())
    def set_path(self,path):
        self.__widget.set_filename(path)

class PathEntry:
    def __init__(self,entry,path):
        self.__widget=entry
        self.__path=path
        self.__widget.connect('activate',self.__onValueChange)
    def __onValueChange(self,widget):
        self.__path.set_path(self.__widget.get_text())
    def set_path(self,path):
        self.__widget.set_text(path)

class SendButton:
    def __init__(self,widget,path,connection_details,response_label):
        self.__widget=widget
        self.__widget.connect('clicked',self.__clicked)
        self.__path=path
        self.__connection_details=connection_details
        self.__response_label=response_label
    def __clicked(self,widget):
        with open(self.__path.get_path(),'rb') as image_file:
            with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as connection_socket:
                connection_socket.connect(self.__connection_details)
                chunk=image_file.read(1024)
                while(chunk):
                    connection_socket.send(chunk)
                    chunk=image_file.read(1024)
                connection_socket.shutdown(socket.SHUT_WR)
                chunk=connection_socket.recv(1024)
                response=''
                while(chunk):
                    response+=chunk.decode('ascii')
                    chunk=connection_socket.recv(1024)
                self.__response_label.set_text(response)
class MainApp:
    def __init__(self):
        self.__server_address='192.168.122.201'
        self.__port=9500

        builder=Gtk.Builder()
        builder.add_from_file("GUI.glade")

        self.__path=Path()

        self.__window=builder.get_object("main_window")
                
        self.__response_label=builder.get_object('response')
        self.__send_button=SendButton(builder.get_object('send'),self.__path,(self.__server_address,self.__port),self.__response_label)

        self.__path_entry=PathEntry(builder.get_object("search_path"),self.__path)
        self.__file_chooser_button=PathButton(builder.get_object("file_chooser"),self.__path)
		
        self.__path.add_observable([self.__path_entry,self.__file_chooser_button])
		
    def show_all(self):
         self.__window.show_all()
MA=MainApp()
MA.show_all()
Gtk.main()
