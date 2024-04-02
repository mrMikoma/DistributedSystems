# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import chat_pb2 as chat__pb2


class ChatServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.SendPrivateMessage = channel.unary_unary(
                '/chat.ChatService/SendPrivateMessage',
                request_serializer=chat__pb2.PrivateMessage.SerializeToString,
                response_deserializer=chat__pb2.Status.FromString,
                )
        self.GetPrivateMessages = channel.unary_stream(
                '/chat.ChatService/GetPrivateMessages',
                request_serializer=chat__pb2.PrivateMessageRequest.SerializeToString,
                response_deserializer=chat__pb2.Message.FromString,
                )


class ChatServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def SendPrivateMessage(self, request, context):
        """RPC for sending a private message to a user
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetPrivateMessages(self, request, context):
        """RPC for getting all private messages between two users
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ChatServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'SendPrivateMessage': grpc.unary_unary_rpc_method_handler(
                    servicer.SendPrivateMessage,
                    request_deserializer=chat__pb2.PrivateMessage.FromString,
                    response_serializer=chat__pb2.Status.SerializeToString,
            ),
            'GetPrivateMessages': grpc.unary_stream_rpc_method_handler(
                    servicer.GetPrivateMessages,
                    request_deserializer=chat__pb2.PrivateMessageRequest.FromString,
                    response_serializer=chat__pb2.Message.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'chat.ChatService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class ChatService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def SendPrivateMessage(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/chat.ChatService/SendPrivateMessage',
            chat__pb2.PrivateMessage.SerializeToString,
            chat__pb2.Status.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetPrivateMessages(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/chat.ChatService/GetPrivateMessages',
            chat__pb2.PrivateMessageRequest.SerializeToString,
            chat__pb2.Message.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
