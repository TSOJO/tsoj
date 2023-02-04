# from __future__ import annotations

# from enum import Enum

# class Language(Enum):
# 	# https://stackoverflow.com/questions/12680080/python-enums-with-attributes
# 	def __new__(cls, *args, **kwds):
# 		value = len(cls.__members__) + 1
# 		obj = object.__new__(cls)
# 		obj._value_ = value
# 		return obj
# 	def __init__(self, file_extension, ace_mode):
# 		self.file_extension = file_extension
# 		self.ace_mode = ace_mode
	
# 	CPLUSPLUS = ('cpp', 'c_cpp')
# 	PYTHON = ('py', 'python')

# 	def cast_to_document(self) -> str:
# 		return self.name
	
# 	@classmethod
# 	def cast_from_document(cls, document: str) -> Language:
# 		return Language[document]

	