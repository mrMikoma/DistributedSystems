# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: chat.proto
# Protobuf Python Version: 4.25.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\nchat.proto\x12\x04\x63hat\"J\n\x0ePrivateMessage\x12\x11\n\tsender_id\x18\x01 \x01(\t\x12\x14\n\x0crecipient_id\x18\x02 \x01(\t\x12\x0f\n\x07\x63ontent\x18\x03 \x01(\t\"@\n\x15PrivateMessageRequest\x12\x11\n\tsender_id\x18\x01 \x01(\t\x12\x14\n\x0crecipient_id\x18\x02 \x01(\t\">\n\x07Message\x12\x0f\n\x07user_id\x18\x01 \x01(\t\x12\x0f\n\x07\x63ontent\x18\x02 \x01(\t\x12\x11\n\ttimestamp\x18\x03 \x01(\x03\"*\n\x06Status\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x0f\n\x07message\x18\x02 \x01(\t2\x8f\x01\n\x0b\x43hatService\x12:\n\x12SendPrivateMessage\x12\x14.chat.PrivateMessage\x1a\x0c.chat.Status\"\x00\x12\x44\n\x12GetPrivateMessages\x12\x1b.chat.PrivateMessageRequest\x1a\r.chat.Message\"\x00\x30\x01\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'chat_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_PRIVATEMESSAGE']._serialized_start=20
  _globals['_PRIVATEMESSAGE']._serialized_end=94
  _globals['_PRIVATEMESSAGEREQUEST']._serialized_start=96
  _globals['_PRIVATEMESSAGEREQUEST']._serialized_end=160
  _globals['_MESSAGE']._serialized_start=162
  _globals['_MESSAGE']._serialized_end=224
  _globals['_STATUS']._serialized_start=226
  _globals['_STATUS']._serialized_end=268
  _globals['_CHATSERVICE']._serialized_start=271
  _globals['_CHATSERVICE']._serialized_end=414
# @@protoc_insertion_point(module_scope)
