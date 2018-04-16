# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

import dialogflow_v2.proto.session_entity_type_pb2 as google_dot_cloud_dot_dialogflow__v2_dot_proto_dot_session__entity__type__pb2
import google.protobuf.empty_pb2 as google_dot_protobuf_dot_empty__pb2


class SessionEntityTypesStub(object):
  """Manages session entity types.

  Session entity types can be redefined on a session level, allowing for
  specific concepts, like a user's playlists.

  #
  """

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.ListSessionEntityTypes = channel.unary_unary(
        '/google.cloud.dialogflow.v2.SessionEntityTypes/ListSessionEntityTypes',
        request_serializer=google_dot_cloud_dot_dialogflow__v2_dot_proto_dot_session__entity__type__pb2.ListSessionEntityTypesRequest.SerializeToString,
        response_deserializer=google_dot_cloud_dot_dialogflow__v2_dot_proto_dot_session__entity__type__pb2.ListSessionEntityTypesResponse.FromString,
        )
    self.GetSessionEntityType = channel.unary_unary(
        '/google.cloud.dialogflow.v2.SessionEntityTypes/GetSessionEntityType',
        request_serializer=google_dot_cloud_dot_dialogflow__v2_dot_proto_dot_session__entity__type__pb2.GetSessionEntityTypeRequest.SerializeToString,
        response_deserializer=google_dot_cloud_dot_dialogflow__v2_dot_proto_dot_session__entity__type__pb2.SessionEntityType.FromString,
        )
    self.CreateSessionEntityType = channel.unary_unary(
        '/google.cloud.dialogflow.v2.SessionEntityTypes/CreateSessionEntityType',
        request_serializer=google_dot_cloud_dot_dialogflow__v2_dot_proto_dot_session__entity__type__pb2.CreateSessionEntityTypeRequest.SerializeToString,
        response_deserializer=google_dot_cloud_dot_dialogflow__v2_dot_proto_dot_session__entity__type__pb2.SessionEntityType.FromString,
        )
    self.UpdateSessionEntityType = channel.unary_unary(
        '/google.cloud.dialogflow.v2.SessionEntityTypes/UpdateSessionEntityType',
        request_serializer=google_dot_cloud_dot_dialogflow__v2_dot_proto_dot_session__entity__type__pb2.UpdateSessionEntityTypeRequest.SerializeToString,
        response_deserializer=google_dot_cloud_dot_dialogflow__v2_dot_proto_dot_session__entity__type__pb2.SessionEntityType.FromString,
        )
    self.DeleteSessionEntityType = channel.unary_unary(
        '/google.cloud.dialogflow.v2.SessionEntityTypes/DeleteSessionEntityType',
        request_serializer=google_dot_cloud_dot_dialogflow__v2_dot_proto_dot_session__entity__type__pb2.DeleteSessionEntityTypeRequest.SerializeToString,
        response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
        )


class SessionEntityTypesServicer(object):
  """Manages session entity types.

  Session entity types can be redefined on a session level, allowing for
  specific concepts, like a user's playlists.

  #
  """

  def ListSessionEntityTypes(self, request, context):
    """Returns the list of all session entity types in the specified session.
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def GetSessionEntityType(self, request, context):
    """Retrieves the specified session entity type.
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def CreateSessionEntityType(self, request, context):
    """Creates a session entity type.
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def UpdateSessionEntityType(self, request, context):
    """Updates the specified session entity type.
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def DeleteSessionEntityType(self, request, context):
    """Deletes the specified session entity type.
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_SessionEntityTypesServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'ListSessionEntityTypes': grpc.unary_unary_rpc_method_handler(
          servicer.ListSessionEntityTypes,
          request_deserializer=google_dot_cloud_dot_dialogflow__v2_dot_proto_dot_session__entity__type__pb2.ListSessionEntityTypesRequest.FromString,
          response_serializer=google_dot_cloud_dot_dialogflow__v2_dot_proto_dot_session__entity__type__pb2.ListSessionEntityTypesResponse.SerializeToString,
      ),
      'GetSessionEntityType': grpc.unary_unary_rpc_method_handler(
          servicer.GetSessionEntityType,
          request_deserializer=google_dot_cloud_dot_dialogflow__v2_dot_proto_dot_session__entity__type__pb2.GetSessionEntityTypeRequest.FromString,
          response_serializer=google_dot_cloud_dot_dialogflow__v2_dot_proto_dot_session__entity__type__pb2.SessionEntityType.SerializeToString,
      ),
      'CreateSessionEntityType': grpc.unary_unary_rpc_method_handler(
          servicer.CreateSessionEntityType,
          request_deserializer=google_dot_cloud_dot_dialogflow__v2_dot_proto_dot_session__entity__type__pb2.CreateSessionEntityTypeRequest.FromString,
          response_serializer=google_dot_cloud_dot_dialogflow__v2_dot_proto_dot_session__entity__type__pb2.SessionEntityType.SerializeToString,
      ),
      'UpdateSessionEntityType': grpc.unary_unary_rpc_method_handler(
          servicer.UpdateSessionEntityType,
          request_deserializer=google_dot_cloud_dot_dialogflow__v2_dot_proto_dot_session__entity__type__pb2.UpdateSessionEntityTypeRequest.FromString,
          response_serializer=google_dot_cloud_dot_dialogflow__v2_dot_proto_dot_session__entity__type__pb2.SessionEntityType.SerializeToString,
      ),
      'DeleteSessionEntityType': grpc.unary_unary_rpc_method_handler(
          servicer.DeleteSessionEntityType,
          request_deserializer=google_dot_cloud_dot_dialogflow__v2_dot_proto_dot_session__entity__type__pb2.DeleteSessionEntityTypeRequest.FromString,
          response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'google.cloud.dialogflow.v2.SessionEntityTypes', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))
