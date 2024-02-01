# -*- coding: utf-8 -*-
# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os

# try/except added for compatibility with python < 3.8
try:
    from unittest import mock
    from unittest.mock import AsyncMock  # pragma: NO COVER
except ImportError:  # pragma: NO COVER
    import mock

from collections.abc import Iterable
import json
import math

from google.api_core import (
    future,
    gapic_v1,
    grpc_helpers,
    grpc_helpers_async,
    operation,
    operations_v1,
    path_template,
)
from google.api_core import api_core_version, client_options
from google.api_core import exceptions as core_exceptions
from google.api_core import operation_async  # type: ignore
import google.auth
from google.auth import credentials as ga_credentials
from google.auth.exceptions import MutualTLSChannelError
from google.cloud.location import locations_pb2
from google.longrunning import operations_pb2  # type: ignore
from google.oauth2 import service_account
from google.protobuf import empty_pb2  # type: ignore
from google.protobuf import field_mask_pb2  # type: ignore
from google.protobuf import json_format
from google.protobuf import struct_pb2  # type: ignore
import grpc
from grpc.experimental import aio
from proto.marshal.rules import wrappers
from proto.marshal.rules.dates import DurationRule, TimestampRule
import pytest
from requests import PreparedRequest, Request, Response
from requests.sessions import Session

from google.cloud.dialogflow_v2.services.agents import (
    AgentsAsyncClient,
    AgentsClient,
    pagers,
    transports,
)
from google.cloud.dialogflow_v2.types import agent
from google.cloud.dialogflow_v2.types import agent as gcd_agent
from google.cloud.dialogflow_v2.types import validation_result


def client_cert_source_callback():
    return b"cert bytes", b"key bytes"


# If default endpoint is localhost, then default mtls endpoint will be the same.
# This method modifies the default endpoint so the client can produce a different
# mtls endpoint for endpoint testing purposes.
def modify_default_endpoint(client):
    return (
        "foo.googleapis.com"
        if ("localhost" in client.DEFAULT_ENDPOINT)
        else client.DEFAULT_ENDPOINT
    )


# If default endpoint template is localhost, then default mtls endpoint will be the same.
# This method modifies the default endpoint template so the client can produce a different
# mtls endpoint for endpoint testing purposes.
def modify_default_endpoint_template(client):
    return (
        "test.{UNIVERSE_DOMAIN}"
        if ("localhost" in client._DEFAULT_ENDPOINT_TEMPLATE)
        else client._DEFAULT_ENDPOINT_TEMPLATE
    )


# Anonymous Credentials with universe domain property. If no universe domain is provided, then
# the default universe domain is "googleapis.com".
class _AnonymousCredentialsWithUniverseDomain(ga_credentials.AnonymousCredentials):
    def __init__(self, universe_domain="googleapis.com"):
        super(_AnonymousCredentialsWithUniverseDomain, self).__init__()
        self._universe_domain = universe_domain

    @property
    def universe_domain(self):
        return self._universe_domain


def test__get_default_mtls_endpoint():
    api_endpoint = "example.googleapis.com"
    api_mtls_endpoint = "example.mtls.googleapis.com"
    sandbox_endpoint = "example.sandbox.googleapis.com"
    sandbox_mtls_endpoint = "example.mtls.sandbox.googleapis.com"
    non_googleapi = "api.example.com"

    assert AgentsClient._get_default_mtls_endpoint(None) is None
    assert AgentsClient._get_default_mtls_endpoint(api_endpoint) == api_mtls_endpoint
    assert (
        AgentsClient._get_default_mtls_endpoint(api_mtls_endpoint) == api_mtls_endpoint
    )
    assert (
        AgentsClient._get_default_mtls_endpoint(sandbox_endpoint)
        == sandbox_mtls_endpoint
    )
    assert (
        AgentsClient._get_default_mtls_endpoint(sandbox_mtls_endpoint)
        == sandbox_mtls_endpoint
    )
    assert AgentsClient._get_default_mtls_endpoint(non_googleapi) == non_googleapi


def test__read_environment_variables():
    assert AgentsClient._read_environment_variables() == (False, "auto", None)

    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": "true"}):
        assert AgentsClient._read_environment_variables() == (True, "auto", None)

    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": "false"}):
        assert AgentsClient._read_environment_variables() == (False, "auto", None)

    with mock.patch.dict(
        os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": "Unsupported"}
    ):
        with pytest.raises(ValueError) as excinfo:
            AgentsClient._read_environment_variables()
    assert (
        str(excinfo.value)
        == "Environment variable `GOOGLE_API_USE_CLIENT_CERTIFICATE` must be either `true` or `false`"
    )

    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "never"}):
        assert AgentsClient._read_environment_variables() == (False, "never", None)

    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "always"}):
        assert AgentsClient._read_environment_variables() == (False, "always", None)

    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "auto"}):
        assert AgentsClient._read_environment_variables() == (False, "auto", None)

    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "Unsupported"}):
        with pytest.raises(MutualTLSChannelError) as excinfo:
            AgentsClient._read_environment_variables()
    assert (
        str(excinfo.value)
        == "Environment variable `GOOGLE_API_USE_MTLS_ENDPOINT` must be `never`, `auto` or `always`"
    )

    with mock.patch.dict(os.environ, {"GOOGLE_CLOUD_UNIVERSE_DOMAIN": "foo.com"}):
        assert AgentsClient._read_environment_variables() == (False, "auto", "foo.com")


def test__get_client_cert_source():
    mock_provided_cert_source = mock.Mock()
    mock_default_cert_source = mock.Mock()

    assert AgentsClient._get_client_cert_source(None, False) is None
    assert (
        AgentsClient._get_client_cert_source(mock_provided_cert_source, False) is None
    )
    assert (
        AgentsClient._get_client_cert_source(mock_provided_cert_source, True)
        == mock_provided_cert_source
    )

    with mock.patch(
        "google.auth.transport.mtls.has_default_client_cert_source", return_value=True
    ):
        with mock.patch(
            "google.auth.transport.mtls.default_client_cert_source",
            return_value=mock_default_cert_source,
        ):
            assert (
                AgentsClient._get_client_cert_source(None, True)
                is mock_default_cert_source
            )
            assert (
                AgentsClient._get_client_cert_source(mock_provided_cert_source, "true")
                is mock_provided_cert_source
            )


@mock.patch.object(
    AgentsClient,
    "_DEFAULT_ENDPOINT_TEMPLATE",
    modify_default_endpoint_template(AgentsClient),
)
@mock.patch.object(
    AgentsAsyncClient,
    "_DEFAULT_ENDPOINT_TEMPLATE",
    modify_default_endpoint_template(AgentsAsyncClient),
)
def test__get_api_endpoint():
    api_override = "foo.com"
    mock_client_cert_source = mock.Mock()
    default_universe = AgentsClient._DEFAULT_UNIVERSE
    default_endpoint = AgentsClient._DEFAULT_ENDPOINT_TEMPLATE.format(
        UNIVERSE_DOMAIN=default_universe
    )
    mock_universe = "bar.com"
    mock_endpoint = AgentsClient._DEFAULT_ENDPOINT_TEMPLATE.format(
        UNIVERSE_DOMAIN=mock_universe
    )

    assert (
        AgentsClient._get_api_endpoint(
            api_override, mock_client_cert_source, default_universe, "always"
        )
        == api_override
    )
    assert (
        AgentsClient._get_api_endpoint(
            None, mock_client_cert_source, default_universe, "auto"
        )
        == AgentsClient.DEFAULT_MTLS_ENDPOINT
    )
    assert (
        AgentsClient._get_api_endpoint(None, None, default_universe, "auto")
        == default_endpoint
    )
    assert (
        AgentsClient._get_api_endpoint(None, None, default_universe, "always")
        == AgentsClient.DEFAULT_MTLS_ENDPOINT
    )
    assert (
        AgentsClient._get_api_endpoint(
            None, mock_client_cert_source, default_universe, "always"
        )
        == AgentsClient.DEFAULT_MTLS_ENDPOINT
    )
    assert (
        AgentsClient._get_api_endpoint(None, None, mock_universe, "never")
        == mock_endpoint
    )
    assert (
        AgentsClient._get_api_endpoint(None, None, default_universe, "never")
        == default_endpoint
    )

    with pytest.raises(MutualTLSChannelError) as excinfo:
        AgentsClient._get_api_endpoint(
            None, mock_client_cert_source, mock_universe, "auto"
        )
    assert (
        str(excinfo.value)
        == "mTLS is not supported in any universe other than googleapis.com."
    )


def test__get_universe_domain():
    client_universe_domain = "foo.com"
    universe_domain_env = "bar.com"

    assert (
        AgentsClient._get_universe_domain(client_universe_domain, universe_domain_env)
        == client_universe_domain
    )
    assert (
        AgentsClient._get_universe_domain(None, universe_domain_env)
        == universe_domain_env
    )
    assert (
        AgentsClient._get_universe_domain(None, None) == AgentsClient._DEFAULT_UNIVERSE
    )

    with pytest.raises(ValueError) as excinfo:
        AgentsClient._get_universe_domain("", None)
    assert str(excinfo.value) == "Universe Domain cannot be an empty string."


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name",
    [
        (AgentsClient, transports.AgentsGrpcTransport, "grpc"),
        (AgentsClient, transports.AgentsRestTransport, "rest"),
    ],
)
def test__validate_universe_domain(client_class, transport_class, transport_name):
    client = client_class(
        transport=transport_class(credentials=_AnonymousCredentialsWithUniverseDomain())
    )
    assert client._validate_universe_domain() == True

    # Test the case when universe is already validated.
    assert client._validate_universe_domain() == True

    if transport_name == "grpc":
        # Test the case where credentials are provided by the
        # `local_channel_credentials`. The default universes in both match.
        channel = grpc.secure_channel(
            "http://localhost/", grpc.local_channel_credentials()
        )
        client = client_class(transport=transport_class(channel=channel))
        assert client._validate_universe_domain() == True

        # Test the case where credentials do not exist: e.g. a transport is provided
        # with no credentials. Validation should still succeed because there is no
        # mismatch with non-existent credentials.
        channel = grpc.secure_channel(
            "http://localhost/", grpc.local_channel_credentials()
        )
        transport = transport_class(channel=channel)
        transport._credentials = None
        client = client_class(transport=transport)
        assert client._validate_universe_domain() == True

    # Test the case when there is a universe mismatch from the credentials.
    client = client_class(
        transport=transport_class(
            credentials=_AnonymousCredentialsWithUniverseDomain(
                universe_domain="foo.com"
            )
        )
    )
    with pytest.raises(ValueError) as excinfo:
        client._validate_universe_domain()
    assert (
        str(excinfo.value)
        == "The configured universe domain (googleapis.com) does not match the universe domain found in the credentials (foo.com). If you haven't configured the universe domain explicitly, `googleapis.com` is the default."
    )

    # Test the case when there is a universe mismatch from the client.
    #
    # TODO: Make this test unconditional once the minimum supported version of
    # google-api-core becomes 2.15.0 or higher.
    api_core_major, api_core_minor, _ = [
        int(part) for part in api_core_version.__version__.split(".")
    ]
    if api_core_major > 2 or (api_core_major == 2 and api_core_minor >= 15):
        client = client_class(
            client_options={"universe_domain": "bar.com"},
            transport=transport_class(
                credentials=_AnonymousCredentialsWithUniverseDomain(),
            ),
        )
        with pytest.raises(ValueError) as excinfo:
            client._validate_universe_domain()
        assert (
            str(excinfo.value)
            == "The configured universe domain (bar.com) does not match the universe domain found in the credentials (googleapis.com). If you haven't configured the universe domain explicitly, `googleapis.com` is the default."
        )


@pytest.mark.parametrize(
    "client_class,transport_name",
    [
        (AgentsClient, "grpc"),
        (AgentsAsyncClient, "grpc_asyncio"),
        (AgentsClient, "rest"),
    ],
)
def test_agents_client_from_service_account_info(client_class, transport_name):
    creds = _AnonymousCredentialsWithUniverseDomain()
    with mock.patch.object(
        service_account.Credentials, "from_service_account_info"
    ) as factory:
        factory.return_value = creds
        info = {"valid": True}
        client = client_class.from_service_account_info(info, transport=transport_name)
        assert client.transport._credentials == creds
        assert isinstance(client, client_class)

        assert client.transport._host == (
            "dialogflow.googleapis.com:443"
            if transport_name in ["grpc", "grpc_asyncio"]
            else "https://dialogflow.googleapis.com"
        )


@pytest.mark.parametrize(
    "transport_class,transport_name",
    [
        (transports.AgentsGrpcTransport, "grpc"),
        (transports.AgentsGrpcAsyncIOTransport, "grpc_asyncio"),
        (transports.AgentsRestTransport, "rest"),
    ],
)
def test_agents_client_service_account_always_use_jwt(transport_class, transport_name):
    with mock.patch.object(
        service_account.Credentials, "with_always_use_jwt_access", create=True
    ) as use_jwt:
        creds = service_account.Credentials(None, None, None)
        transport = transport_class(credentials=creds, always_use_jwt_access=True)
        use_jwt.assert_called_once_with(True)

    with mock.patch.object(
        service_account.Credentials, "with_always_use_jwt_access", create=True
    ) as use_jwt:
        creds = service_account.Credentials(None, None, None)
        transport = transport_class(credentials=creds, always_use_jwt_access=False)
        use_jwt.assert_not_called()


@pytest.mark.parametrize(
    "client_class,transport_name",
    [
        (AgentsClient, "grpc"),
        (AgentsAsyncClient, "grpc_asyncio"),
        (AgentsClient, "rest"),
    ],
)
def test_agents_client_from_service_account_file(client_class, transport_name):
    creds = _AnonymousCredentialsWithUniverseDomain()
    with mock.patch.object(
        service_account.Credentials, "from_service_account_file"
    ) as factory:
        factory.return_value = creds
        client = client_class.from_service_account_file(
            "dummy/file/path.json", transport=transport_name
        )
        assert client.transport._credentials == creds
        assert isinstance(client, client_class)

        client = client_class.from_service_account_json(
            "dummy/file/path.json", transport=transport_name
        )
        assert client.transport._credentials == creds
        assert isinstance(client, client_class)

        assert client.transport._host == (
            "dialogflow.googleapis.com:443"
            if transport_name in ["grpc", "grpc_asyncio"]
            else "https://dialogflow.googleapis.com"
        )


def test_agents_client_get_transport_class():
    transport = AgentsClient.get_transport_class()
    available_transports = [
        transports.AgentsGrpcTransport,
        transports.AgentsRestTransport,
    ]
    assert transport in available_transports

    transport = AgentsClient.get_transport_class("grpc")
    assert transport == transports.AgentsGrpcTransport


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name",
    [
        (AgentsClient, transports.AgentsGrpcTransport, "grpc"),
        (AgentsAsyncClient, transports.AgentsGrpcAsyncIOTransport, "grpc_asyncio"),
        (AgentsClient, transports.AgentsRestTransport, "rest"),
    ],
)
@mock.patch.object(
    AgentsClient,
    "_DEFAULT_ENDPOINT_TEMPLATE",
    modify_default_endpoint_template(AgentsClient),
)
@mock.patch.object(
    AgentsAsyncClient,
    "_DEFAULT_ENDPOINT_TEMPLATE",
    modify_default_endpoint_template(AgentsAsyncClient),
)
def test_agents_client_client_options(client_class, transport_class, transport_name):
    # Check that if channel is provided we won't create a new one.
    with mock.patch.object(AgentsClient, "get_transport_class") as gtc:
        transport = transport_class(
            credentials=_AnonymousCredentialsWithUniverseDomain()
        )
        client = client_class(transport=transport)
        gtc.assert_not_called()

    # Check that if channel is provided via str we will create a new one.
    with mock.patch.object(AgentsClient, "get_transport_class") as gtc:
        client = client_class(transport=transport_name)
        gtc.assert_called()

    # Check the case api_endpoint is provided.
    options = client_options.ClientOptions(api_endpoint="squid.clam.whelk")
    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(transport=transport_name, client_options=options)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host="squid.clam.whelk",
            scopes=None,
            client_cert_source_for_mtls=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
            always_use_jwt_access=True,
            api_audience=None,
        )

    # Check the case api_endpoint is not provided and GOOGLE_API_USE_MTLS_ENDPOINT is
    # "never".
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "never"}):
        with mock.patch.object(transport_class, "__init__") as patched:
            patched.return_value = None
            client = client_class(transport=transport_name)
            patched.assert_called_once_with(
                credentials=None,
                credentials_file=None,
                host=client._DEFAULT_ENDPOINT_TEMPLATE.format(
                    UNIVERSE_DOMAIN=client._DEFAULT_UNIVERSE
                ),
                scopes=None,
                client_cert_source_for_mtls=None,
                quota_project_id=None,
                client_info=transports.base.DEFAULT_CLIENT_INFO,
                always_use_jwt_access=True,
                api_audience=None,
            )

    # Check the case api_endpoint is not provided and GOOGLE_API_USE_MTLS_ENDPOINT is
    # "always".
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "always"}):
        with mock.patch.object(transport_class, "__init__") as patched:
            patched.return_value = None
            client = client_class(transport=transport_name)
            patched.assert_called_once_with(
                credentials=None,
                credentials_file=None,
                host=client.DEFAULT_MTLS_ENDPOINT,
                scopes=None,
                client_cert_source_for_mtls=None,
                quota_project_id=None,
                client_info=transports.base.DEFAULT_CLIENT_INFO,
                always_use_jwt_access=True,
                api_audience=None,
            )

    # Check the case api_endpoint is not provided and GOOGLE_API_USE_MTLS_ENDPOINT has
    # unsupported value.
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "Unsupported"}):
        with pytest.raises(MutualTLSChannelError) as excinfo:
            client = client_class(transport=transport_name)
    assert (
        str(excinfo.value)
        == "Environment variable `GOOGLE_API_USE_MTLS_ENDPOINT` must be `never`, `auto` or `always`"
    )

    # Check the case GOOGLE_API_USE_CLIENT_CERTIFICATE has unsupported value.
    with mock.patch.dict(
        os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": "Unsupported"}
    ):
        with pytest.raises(ValueError) as excinfo:
            client = client_class(transport=transport_name)
    assert (
        str(excinfo.value)
        == "Environment variable `GOOGLE_API_USE_CLIENT_CERTIFICATE` must be either `true` or `false`"
    )

    # Check the case quota_project_id is provided
    options = client_options.ClientOptions(quota_project_id="octopus")
    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(client_options=options, transport=transport_name)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host=client._DEFAULT_ENDPOINT_TEMPLATE.format(
                UNIVERSE_DOMAIN=client._DEFAULT_UNIVERSE
            ),
            scopes=None,
            client_cert_source_for_mtls=None,
            quota_project_id="octopus",
            client_info=transports.base.DEFAULT_CLIENT_INFO,
            always_use_jwt_access=True,
            api_audience=None,
        )
    # Check the case api_endpoint is provided
    options = client_options.ClientOptions(
        api_audience="https://language.googleapis.com"
    )
    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(client_options=options, transport=transport_name)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host=client._DEFAULT_ENDPOINT_TEMPLATE.format(
                UNIVERSE_DOMAIN=client._DEFAULT_UNIVERSE
            ),
            scopes=None,
            client_cert_source_for_mtls=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
            always_use_jwt_access=True,
            api_audience="https://language.googleapis.com",
        )


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name,use_client_cert_env",
    [
        (AgentsClient, transports.AgentsGrpcTransport, "grpc", "true"),
        (
            AgentsAsyncClient,
            transports.AgentsGrpcAsyncIOTransport,
            "grpc_asyncio",
            "true",
        ),
        (AgentsClient, transports.AgentsGrpcTransport, "grpc", "false"),
        (
            AgentsAsyncClient,
            transports.AgentsGrpcAsyncIOTransport,
            "grpc_asyncio",
            "false",
        ),
        (AgentsClient, transports.AgentsRestTransport, "rest", "true"),
        (AgentsClient, transports.AgentsRestTransport, "rest", "false"),
    ],
)
@mock.patch.object(
    AgentsClient,
    "_DEFAULT_ENDPOINT_TEMPLATE",
    modify_default_endpoint_template(AgentsClient),
)
@mock.patch.object(
    AgentsAsyncClient,
    "_DEFAULT_ENDPOINT_TEMPLATE",
    modify_default_endpoint_template(AgentsAsyncClient),
)
@mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "auto"})
def test_agents_client_mtls_env_auto(
    client_class, transport_class, transport_name, use_client_cert_env
):
    # This tests the endpoint autoswitch behavior. Endpoint is autoswitched to the default
    # mtls endpoint, if GOOGLE_API_USE_CLIENT_CERTIFICATE is "true" and client cert exists.

    # Check the case client_cert_source is provided. Whether client cert is used depends on
    # GOOGLE_API_USE_CLIENT_CERTIFICATE value.
    with mock.patch.dict(
        os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": use_client_cert_env}
    ):
        options = client_options.ClientOptions(
            client_cert_source=client_cert_source_callback
        )
        with mock.patch.object(transport_class, "__init__") as patched:
            patched.return_value = None
            client = client_class(client_options=options, transport=transport_name)

            if use_client_cert_env == "false":
                expected_client_cert_source = None
                expected_host = client._DEFAULT_ENDPOINT_TEMPLATE.format(
                    UNIVERSE_DOMAIN=client._DEFAULT_UNIVERSE
                )
            else:
                expected_client_cert_source = client_cert_source_callback
                expected_host = client.DEFAULT_MTLS_ENDPOINT

            patched.assert_called_once_with(
                credentials=None,
                credentials_file=None,
                host=expected_host,
                scopes=None,
                client_cert_source_for_mtls=expected_client_cert_source,
                quota_project_id=None,
                client_info=transports.base.DEFAULT_CLIENT_INFO,
                always_use_jwt_access=True,
                api_audience=None,
            )

    # Check the case ADC client cert is provided. Whether client cert is used depends on
    # GOOGLE_API_USE_CLIENT_CERTIFICATE value.
    with mock.patch.dict(
        os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": use_client_cert_env}
    ):
        with mock.patch.object(transport_class, "__init__") as patched:
            with mock.patch(
                "google.auth.transport.mtls.has_default_client_cert_source",
                return_value=True,
            ):
                with mock.patch(
                    "google.auth.transport.mtls.default_client_cert_source",
                    return_value=client_cert_source_callback,
                ):
                    if use_client_cert_env == "false":
                        expected_host = client._DEFAULT_ENDPOINT_TEMPLATE.format(
                            UNIVERSE_DOMAIN=client._DEFAULT_UNIVERSE
                        )
                        expected_client_cert_source = None
                    else:
                        expected_host = client.DEFAULT_MTLS_ENDPOINT
                        expected_client_cert_source = client_cert_source_callback

                    patched.return_value = None
                    client = client_class(transport=transport_name)
                    patched.assert_called_once_with(
                        credentials=None,
                        credentials_file=None,
                        host=expected_host,
                        scopes=None,
                        client_cert_source_for_mtls=expected_client_cert_source,
                        quota_project_id=None,
                        client_info=transports.base.DEFAULT_CLIENT_INFO,
                        always_use_jwt_access=True,
                        api_audience=None,
                    )

    # Check the case client_cert_source and ADC client cert are not provided.
    with mock.patch.dict(
        os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": use_client_cert_env}
    ):
        with mock.patch.object(transport_class, "__init__") as patched:
            with mock.patch(
                "google.auth.transport.mtls.has_default_client_cert_source",
                return_value=False,
            ):
                patched.return_value = None
                client = client_class(transport=transport_name)
                patched.assert_called_once_with(
                    credentials=None,
                    credentials_file=None,
                    host=client._DEFAULT_ENDPOINT_TEMPLATE.format(
                        UNIVERSE_DOMAIN=client._DEFAULT_UNIVERSE
                    ),
                    scopes=None,
                    client_cert_source_for_mtls=None,
                    quota_project_id=None,
                    client_info=transports.base.DEFAULT_CLIENT_INFO,
                    always_use_jwt_access=True,
                    api_audience=None,
                )


@pytest.mark.parametrize("client_class", [AgentsClient, AgentsAsyncClient])
@mock.patch.object(
    AgentsClient, "DEFAULT_ENDPOINT", modify_default_endpoint(AgentsClient)
)
@mock.patch.object(
    AgentsAsyncClient, "DEFAULT_ENDPOINT", modify_default_endpoint(AgentsAsyncClient)
)
def test_agents_client_get_mtls_endpoint_and_cert_source(client_class):
    mock_client_cert_source = mock.Mock()

    # Test the case GOOGLE_API_USE_CLIENT_CERTIFICATE is "true".
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": "true"}):
        mock_api_endpoint = "foo"
        options = client_options.ClientOptions(
            client_cert_source=mock_client_cert_source, api_endpoint=mock_api_endpoint
        )
        api_endpoint, cert_source = client_class.get_mtls_endpoint_and_cert_source(
            options
        )
        assert api_endpoint == mock_api_endpoint
        assert cert_source == mock_client_cert_source

    # Test the case GOOGLE_API_USE_CLIENT_CERTIFICATE is "false".
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": "false"}):
        mock_client_cert_source = mock.Mock()
        mock_api_endpoint = "foo"
        options = client_options.ClientOptions(
            client_cert_source=mock_client_cert_source, api_endpoint=mock_api_endpoint
        )
        api_endpoint, cert_source = client_class.get_mtls_endpoint_and_cert_source(
            options
        )
        assert api_endpoint == mock_api_endpoint
        assert cert_source is None

    # Test the case GOOGLE_API_USE_MTLS_ENDPOINT is "never".
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "never"}):
        api_endpoint, cert_source = client_class.get_mtls_endpoint_and_cert_source()
        assert api_endpoint == client_class.DEFAULT_ENDPOINT
        assert cert_source is None

    # Test the case GOOGLE_API_USE_MTLS_ENDPOINT is "always".
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "always"}):
        api_endpoint, cert_source = client_class.get_mtls_endpoint_and_cert_source()
        assert api_endpoint == client_class.DEFAULT_MTLS_ENDPOINT
        assert cert_source is None

    # Test the case GOOGLE_API_USE_MTLS_ENDPOINT is "auto" and default cert doesn't exist.
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": "true"}):
        with mock.patch(
            "google.auth.transport.mtls.has_default_client_cert_source",
            return_value=False,
        ):
            api_endpoint, cert_source = client_class.get_mtls_endpoint_and_cert_source()
            assert api_endpoint == client_class.DEFAULT_ENDPOINT
            assert cert_source is None

    # Test the case GOOGLE_API_USE_MTLS_ENDPOINT is "auto" and default cert exists.
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": "true"}):
        with mock.patch(
            "google.auth.transport.mtls.has_default_client_cert_source",
            return_value=True,
        ):
            with mock.patch(
                "google.auth.transport.mtls.default_client_cert_source",
                return_value=mock_client_cert_source,
            ):
                (
                    api_endpoint,
                    cert_source,
                ) = client_class.get_mtls_endpoint_and_cert_source()
                assert api_endpoint == client_class.DEFAULT_MTLS_ENDPOINT
                assert cert_source == mock_client_cert_source

    # Check the case api_endpoint is not provided and GOOGLE_API_USE_MTLS_ENDPOINT has
    # unsupported value.
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "Unsupported"}):
        with pytest.raises(MutualTLSChannelError) as excinfo:
            client_class.get_mtls_endpoint_and_cert_source()

        assert (
            str(excinfo.value)
            == "Environment variable `GOOGLE_API_USE_MTLS_ENDPOINT` must be `never`, `auto` or `always`"
        )

    # Check the case GOOGLE_API_USE_CLIENT_CERTIFICATE has unsupported value.
    with mock.patch.dict(
        os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": "Unsupported"}
    ):
        with pytest.raises(ValueError) as excinfo:
            client_class.get_mtls_endpoint_and_cert_source()

        assert (
            str(excinfo.value)
            == "Environment variable `GOOGLE_API_USE_CLIENT_CERTIFICATE` must be either `true` or `false`"
        )


@pytest.mark.parametrize("client_class", [AgentsClient, AgentsAsyncClient])
@mock.patch.object(
    AgentsClient,
    "_DEFAULT_ENDPOINT_TEMPLATE",
    modify_default_endpoint_template(AgentsClient),
)
@mock.patch.object(
    AgentsAsyncClient,
    "_DEFAULT_ENDPOINT_TEMPLATE",
    modify_default_endpoint_template(AgentsAsyncClient),
)
def test_agents_client_client_api_endpoint(client_class):
    mock_client_cert_source = client_cert_source_callback
    api_override = "foo.com"
    default_universe = AgentsClient._DEFAULT_UNIVERSE
    default_endpoint = AgentsClient._DEFAULT_ENDPOINT_TEMPLATE.format(
        UNIVERSE_DOMAIN=default_universe
    )
    mock_universe = "bar.com"
    mock_endpoint = AgentsClient._DEFAULT_ENDPOINT_TEMPLATE.format(
        UNIVERSE_DOMAIN=mock_universe
    )

    # If ClientOptions.api_endpoint is set and GOOGLE_API_USE_CLIENT_CERTIFICATE="true",
    # use ClientOptions.api_endpoint as the api endpoint regardless.
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": "true"}):
        with mock.patch(
            "google.auth.transport.requests.AuthorizedSession.configure_mtls_channel"
        ):
            options = client_options.ClientOptions(
                client_cert_source=mock_client_cert_source, api_endpoint=api_override
            )
            client = client_class(
                client_options=options,
                credentials=_AnonymousCredentialsWithUniverseDomain(),
            )
            assert client.api_endpoint == api_override

    # If ClientOptions.api_endpoint is not set and GOOGLE_API_USE_MTLS_ENDPOINT="never",
    # use the _DEFAULT_ENDPOINT_TEMPLATE populated with GDU as the api endpoint.
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "never"}):
        client = client_class(credentials=_AnonymousCredentialsWithUniverseDomain())
        assert client.api_endpoint == default_endpoint

    # If ClientOptions.api_endpoint is not set and GOOGLE_API_USE_MTLS_ENDPOINT="always",
    # use the DEFAULT_MTLS_ENDPOINT as the api endpoint.
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "always"}):
        client = client_class(credentials=_AnonymousCredentialsWithUniverseDomain())
        assert client.api_endpoint == client_class.DEFAULT_MTLS_ENDPOINT

    # If ClientOptions.api_endpoint is not set, GOOGLE_API_USE_MTLS_ENDPOINT="auto" (default),
    # GOOGLE_API_USE_CLIENT_CERTIFICATE="false" (default), default cert source doesn't exist,
    # and ClientOptions.universe_domain="bar.com",
    # use the _DEFAULT_ENDPOINT_TEMPLATE populated with universe domain as the api endpoint.
    options = client_options.ClientOptions()
    universe_exists = hasattr(options, "universe_domain")
    if universe_exists:
        options = client_options.ClientOptions(universe_domain=mock_universe)
        client = client_class(
            client_options=options,
            credentials=_AnonymousCredentialsWithUniverseDomain(),
        )
    else:
        client = client_class(
            client_options=options,
            credentials=_AnonymousCredentialsWithUniverseDomain(),
        )
    assert client.api_endpoint == (
        mock_endpoint if universe_exists else default_endpoint
    )
    assert client.universe_domain == (
        mock_universe if universe_exists else default_universe
    )

    # If ClientOptions does not have a universe domain attribute and GOOGLE_API_USE_MTLS_ENDPOINT="never",
    # use the _DEFAULT_ENDPOINT_TEMPLATE populated with GDU as the api endpoint.
    options = client_options.ClientOptions()
    if hasattr(options, "universe_domain"):
        delattr(options, "universe_domain")
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "never"}):
        client = client_class(
            client_options=options,
            credentials=_AnonymousCredentialsWithUniverseDomain(),
        )
        assert client.api_endpoint == default_endpoint


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name",
    [
        (AgentsClient, transports.AgentsGrpcTransport, "grpc"),
        (AgentsAsyncClient, transports.AgentsGrpcAsyncIOTransport, "grpc_asyncio"),
        (AgentsClient, transports.AgentsRestTransport, "rest"),
    ],
)
def test_agents_client_client_options_scopes(
    client_class, transport_class, transport_name
):
    # Check the case scopes are provided.
    options = client_options.ClientOptions(
        scopes=["1", "2"],
    )
    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(client_options=options, transport=transport_name)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host=client._DEFAULT_ENDPOINT_TEMPLATE.format(
                UNIVERSE_DOMAIN=client._DEFAULT_UNIVERSE
            ),
            scopes=["1", "2"],
            client_cert_source_for_mtls=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
            always_use_jwt_access=True,
            api_audience=None,
        )


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name,grpc_helpers",
    [
        (AgentsClient, transports.AgentsGrpcTransport, "grpc", grpc_helpers),
        (
            AgentsAsyncClient,
            transports.AgentsGrpcAsyncIOTransport,
            "grpc_asyncio",
            grpc_helpers_async,
        ),
        (AgentsClient, transports.AgentsRestTransport, "rest", None),
    ],
)
def test_agents_client_client_options_credentials_file(
    client_class, transport_class, transport_name, grpc_helpers
):
    # Check the case credentials file is provided.
    options = client_options.ClientOptions(credentials_file="credentials.json")

    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(client_options=options, transport=transport_name)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file="credentials.json",
            host=client._DEFAULT_ENDPOINT_TEMPLATE.format(
                UNIVERSE_DOMAIN=client._DEFAULT_UNIVERSE
            ),
            scopes=None,
            client_cert_source_for_mtls=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
            always_use_jwt_access=True,
            api_audience=None,
        )


def test_agents_client_client_options_from_dict():
    with mock.patch(
        "google.cloud.dialogflow_v2.services.agents.transports.AgentsGrpcTransport.__init__"
    ) as grpc_transport:
        grpc_transport.return_value = None
        client = AgentsClient(client_options={"api_endpoint": "squid.clam.whelk"})
        grpc_transport.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host="squid.clam.whelk",
            scopes=None,
            client_cert_source_for_mtls=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
            always_use_jwt_access=True,
            api_audience=None,
        )


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name,grpc_helpers",
    [
        (AgentsClient, transports.AgentsGrpcTransport, "grpc", grpc_helpers),
        (
            AgentsAsyncClient,
            transports.AgentsGrpcAsyncIOTransport,
            "grpc_asyncio",
            grpc_helpers_async,
        ),
    ],
)
def test_agents_client_create_channel_credentials_file(
    client_class, transport_class, transport_name, grpc_helpers
):
    # Check the case credentials file is provided.
    options = client_options.ClientOptions(credentials_file="credentials.json")

    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(client_options=options, transport=transport_name)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file="credentials.json",
            host=client._DEFAULT_ENDPOINT_TEMPLATE.format(
                UNIVERSE_DOMAIN=client._DEFAULT_UNIVERSE
            ),
            scopes=None,
            client_cert_source_for_mtls=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
            always_use_jwt_access=True,
            api_audience=None,
        )

    # test that the credentials from file are saved and used as the credentials.
    with mock.patch.object(
        google.auth, "load_credentials_from_file", autospec=True
    ) as load_creds, mock.patch.object(
        google.auth, "default", autospec=True
    ) as adc, mock.patch.object(
        grpc_helpers, "create_channel"
    ) as create_channel:
        creds = _AnonymousCredentialsWithUniverseDomain()
        file_creds = _AnonymousCredentialsWithUniverseDomain()
        load_creds.return_value = (file_creds, None)
        adc.return_value = (creds, None)
        client = client_class(client_options=options, transport=transport_name)
        create_channel.assert_called_with(
            "dialogflow.googleapis.com:443",
            credentials=file_creds,
            credentials_file=None,
            quota_project_id=None,
            default_scopes=(
                "https://www.googleapis.com/auth/cloud-platform",
                "https://www.googleapis.com/auth/dialogflow",
            ),
            scopes=None,
            default_host="dialogflow.googleapis.com",
            ssl_credentials=None,
            options=[
                ("grpc.max_send_message_length", -1),
                ("grpc.max_receive_message_length", -1),
            ],
        )


@pytest.mark.parametrize(
    "request_type",
    [
        agent.GetAgentRequest,
        dict,
    ],
)
def test_get_agent(request_type, transport: str = "grpc"):
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_agent), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = agent.Agent(
            parent="parent_value",
            display_name="display_name_value",
            default_language_code="default_language_code_value",
            supported_language_codes=["supported_language_codes_value"],
            time_zone="time_zone_value",
            description="description_value",
            avatar_uri="avatar_uri_value",
            enable_logging=True,
            match_mode=agent.Agent.MatchMode.MATCH_MODE_HYBRID,
            classification_threshold=0.25520000000000004,
            api_version=agent.Agent.ApiVersion.API_VERSION_V1,
            tier=agent.Agent.Tier.TIER_STANDARD,
        )
        response = client.get_agent(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == agent.GetAgentRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, agent.Agent)
    assert response.parent == "parent_value"
    assert response.display_name == "display_name_value"
    assert response.default_language_code == "default_language_code_value"
    assert response.supported_language_codes == ["supported_language_codes_value"]
    assert response.time_zone == "time_zone_value"
    assert response.description == "description_value"
    assert response.avatar_uri == "avatar_uri_value"
    assert response.enable_logging is True
    assert response.match_mode == agent.Agent.MatchMode.MATCH_MODE_HYBRID
    assert math.isclose(
        response.classification_threshold, 0.25520000000000004, rel_tol=1e-6
    )
    assert response.api_version == agent.Agent.ApiVersion.API_VERSION_V1
    assert response.tier == agent.Agent.Tier.TIER_STANDARD


def test_get_agent_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_agent), "__call__") as call:
        client.get_agent()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == agent.GetAgentRequest()


@pytest.mark.asyncio
async def test_get_agent_async(
    transport: str = "grpc_asyncio", request_type=agent.GetAgentRequest
):
    client = AgentsAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_agent), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            agent.Agent(
                parent="parent_value",
                display_name="display_name_value",
                default_language_code="default_language_code_value",
                supported_language_codes=["supported_language_codes_value"],
                time_zone="time_zone_value",
                description="description_value",
                avatar_uri="avatar_uri_value",
                enable_logging=True,
                match_mode=agent.Agent.MatchMode.MATCH_MODE_HYBRID,
                classification_threshold=0.25520000000000004,
                api_version=agent.Agent.ApiVersion.API_VERSION_V1,
                tier=agent.Agent.Tier.TIER_STANDARD,
            )
        )
        response = await client.get_agent(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == agent.GetAgentRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, agent.Agent)
    assert response.parent == "parent_value"
    assert response.display_name == "display_name_value"
    assert response.default_language_code == "default_language_code_value"
    assert response.supported_language_codes == ["supported_language_codes_value"]
    assert response.time_zone == "time_zone_value"
    assert response.description == "description_value"
    assert response.avatar_uri == "avatar_uri_value"
    assert response.enable_logging is True
    assert response.match_mode == agent.Agent.MatchMode.MATCH_MODE_HYBRID
    assert math.isclose(
        response.classification_threshold, 0.25520000000000004, rel_tol=1e-6
    )
    assert response.api_version == agent.Agent.ApiVersion.API_VERSION_V1
    assert response.tier == agent.Agent.Tier.TIER_STANDARD


@pytest.mark.asyncio
async def test_get_agent_async_from_dict():
    await test_get_agent_async(request_type=dict)


def test_get_agent_field_headers():
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = agent.GetAgentRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_agent), "__call__") as call:
        call.return_value = agent.Agent()
        client.get_agent(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "parent=parent_value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_get_agent_field_headers_async():
    client = AgentsAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = agent.GetAgentRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_agent), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(agent.Agent())
        await client.get_agent(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "parent=parent_value",
    ) in kw["metadata"]


def test_get_agent_flattened():
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_agent), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = agent.Agent()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.get_agent(
            parent="parent_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val


def test_get_agent_flattened_error():
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_agent(
            agent.GetAgentRequest(),
            parent="parent_value",
        )


@pytest.mark.asyncio
async def test_get_agent_flattened_async():
    client = AgentsAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_agent), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = agent.Agent()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(agent.Agent())
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.get_agent(
            parent="parent_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val


@pytest.mark.asyncio
async def test_get_agent_flattened_error_async():
    client = AgentsAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.get_agent(
            agent.GetAgentRequest(),
            parent="parent_value",
        )


@pytest.mark.parametrize(
    "request_type",
    [
        gcd_agent.SetAgentRequest,
        dict,
    ],
)
def test_set_agent(request_type, transport: str = "grpc"):
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.set_agent), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = gcd_agent.Agent(
            parent="parent_value",
            display_name="display_name_value",
            default_language_code="default_language_code_value",
            supported_language_codes=["supported_language_codes_value"],
            time_zone="time_zone_value",
            description="description_value",
            avatar_uri="avatar_uri_value",
            enable_logging=True,
            match_mode=gcd_agent.Agent.MatchMode.MATCH_MODE_HYBRID,
            classification_threshold=0.25520000000000004,
            api_version=gcd_agent.Agent.ApiVersion.API_VERSION_V1,
            tier=gcd_agent.Agent.Tier.TIER_STANDARD,
        )
        response = client.set_agent(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == gcd_agent.SetAgentRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, gcd_agent.Agent)
    assert response.parent == "parent_value"
    assert response.display_name == "display_name_value"
    assert response.default_language_code == "default_language_code_value"
    assert response.supported_language_codes == ["supported_language_codes_value"]
    assert response.time_zone == "time_zone_value"
    assert response.description == "description_value"
    assert response.avatar_uri == "avatar_uri_value"
    assert response.enable_logging is True
    assert response.match_mode == gcd_agent.Agent.MatchMode.MATCH_MODE_HYBRID
    assert math.isclose(
        response.classification_threshold, 0.25520000000000004, rel_tol=1e-6
    )
    assert response.api_version == gcd_agent.Agent.ApiVersion.API_VERSION_V1
    assert response.tier == gcd_agent.Agent.Tier.TIER_STANDARD


def test_set_agent_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.set_agent), "__call__") as call:
        client.set_agent()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == gcd_agent.SetAgentRequest()


@pytest.mark.asyncio
async def test_set_agent_async(
    transport: str = "grpc_asyncio", request_type=gcd_agent.SetAgentRequest
):
    client = AgentsAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.set_agent), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            gcd_agent.Agent(
                parent="parent_value",
                display_name="display_name_value",
                default_language_code="default_language_code_value",
                supported_language_codes=["supported_language_codes_value"],
                time_zone="time_zone_value",
                description="description_value",
                avatar_uri="avatar_uri_value",
                enable_logging=True,
                match_mode=gcd_agent.Agent.MatchMode.MATCH_MODE_HYBRID,
                classification_threshold=0.25520000000000004,
                api_version=gcd_agent.Agent.ApiVersion.API_VERSION_V1,
                tier=gcd_agent.Agent.Tier.TIER_STANDARD,
            )
        )
        response = await client.set_agent(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == gcd_agent.SetAgentRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, gcd_agent.Agent)
    assert response.parent == "parent_value"
    assert response.display_name == "display_name_value"
    assert response.default_language_code == "default_language_code_value"
    assert response.supported_language_codes == ["supported_language_codes_value"]
    assert response.time_zone == "time_zone_value"
    assert response.description == "description_value"
    assert response.avatar_uri == "avatar_uri_value"
    assert response.enable_logging is True
    assert response.match_mode == gcd_agent.Agent.MatchMode.MATCH_MODE_HYBRID
    assert math.isclose(
        response.classification_threshold, 0.25520000000000004, rel_tol=1e-6
    )
    assert response.api_version == gcd_agent.Agent.ApiVersion.API_VERSION_V1
    assert response.tier == gcd_agent.Agent.Tier.TIER_STANDARD


@pytest.mark.asyncio
async def test_set_agent_async_from_dict():
    await test_set_agent_async(request_type=dict)


def test_set_agent_field_headers():
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = gcd_agent.SetAgentRequest()

    request.agent.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.set_agent), "__call__") as call:
        call.return_value = gcd_agent.Agent()
        client.set_agent(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "agent.parent=parent_value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_set_agent_field_headers_async():
    client = AgentsAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = gcd_agent.SetAgentRequest()

    request.agent.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.set_agent), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(gcd_agent.Agent())
        await client.set_agent(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "agent.parent=parent_value",
    ) in kw["metadata"]


def test_set_agent_flattened():
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.set_agent), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = gcd_agent.Agent()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.set_agent(
            agent=gcd_agent.Agent(parent="parent_value"),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].agent
        mock_val = gcd_agent.Agent(parent="parent_value")
        assert arg == mock_val


def test_set_agent_flattened_error():
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.set_agent(
            gcd_agent.SetAgentRequest(),
            agent=gcd_agent.Agent(parent="parent_value"),
        )


@pytest.mark.asyncio
async def test_set_agent_flattened_async():
    client = AgentsAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.set_agent), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = gcd_agent.Agent()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(gcd_agent.Agent())
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.set_agent(
            agent=gcd_agent.Agent(parent="parent_value"),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].agent
        mock_val = gcd_agent.Agent(parent="parent_value")
        assert arg == mock_val


@pytest.mark.asyncio
async def test_set_agent_flattened_error_async():
    client = AgentsAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.set_agent(
            gcd_agent.SetAgentRequest(),
            agent=gcd_agent.Agent(parent="parent_value"),
        )


@pytest.mark.parametrize(
    "request_type",
    [
        agent.DeleteAgentRequest,
        dict,
    ],
)
def test_delete_agent(request_type, transport: str = "grpc"):
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_agent), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = None
        response = client.delete_agent(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == agent.DeleteAgentRequest()

    # Establish that the response is the type that we expect.
    assert response is None


def test_delete_agent_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_agent), "__call__") as call:
        client.delete_agent()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == agent.DeleteAgentRequest()


@pytest.mark.asyncio
async def test_delete_agent_async(
    transport: str = "grpc_asyncio", request_type=agent.DeleteAgentRequest
):
    client = AgentsAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_agent), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        response = await client.delete_agent(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == agent.DeleteAgentRequest()

    # Establish that the response is the type that we expect.
    assert response is None


@pytest.mark.asyncio
async def test_delete_agent_async_from_dict():
    await test_delete_agent_async(request_type=dict)


def test_delete_agent_field_headers():
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = agent.DeleteAgentRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_agent), "__call__") as call:
        call.return_value = None
        client.delete_agent(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "parent=parent_value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_delete_agent_field_headers_async():
    client = AgentsAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = agent.DeleteAgentRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_agent), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        await client.delete_agent(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "parent=parent_value",
    ) in kw["metadata"]


def test_delete_agent_flattened():
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_agent), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = None
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.delete_agent(
            parent="parent_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val


def test_delete_agent_flattened_error():
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_agent(
            agent.DeleteAgentRequest(),
            parent="parent_value",
        )


@pytest.mark.asyncio
async def test_delete_agent_flattened_async():
    client = AgentsAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.delete_agent), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.delete_agent(
            parent="parent_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val


@pytest.mark.asyncio
async def test_delete_agent_flattened_error_async():
    client = AgentsAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.delete_agent(
            agent.DeleteAgentRequest(),
            parent="parent_value",
        )


@pytest.mark.parametrize(
    "request_type",
    [
        agent.SearchAgentsRequest,
        dict,
    ],
)
def test_search_agents(request_type, transport: str = "grpc"):
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.search_agents), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = agent.SearchAgentsResponse(
            next_page_token="next_page_token_value",
        )
        response = client.search_agents(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == agent.SearchAgentsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.SearchAgentsPager)
    assert response.next_page_token == "next_page_token_value"


def test_search_agents_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.search_agents), "__call__") as call:
        client.search_agents()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == agent.SearchAgentsRequest()


@pytest.mark.asyncio
async def test_search_agents_async(
    transport: str = "grpc_asyncio", request_type=agent.SearchAgentsRequest
):
    client = AgentsAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.search_agents), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            agent.SearchAgentsResponse(
                next_page_token="next_page_token_value",
            )
        )
        response = await client.search_agents(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == agent.SearchAgentsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.SearchAgentsAsyncPager)
    assert response.next_page_token == "next_page_token_value"


@pytest.mark.asyncio
async def test_search_agents_async_from_dict():
    await test_search_agents_async(request_type=dict)


def test_search_agents_field_headers():
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = agent.SearchAgentsRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.search_agents), "__call__") as call:
        call.return_value = agent.SearchAgentsResponse()
        client.search_agents(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "parent=parent_value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_search_agents_field_headers_async():
    client = AgentsAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = agent.SearchAgentsRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.search_agents), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            agent.SearchAgentsResponse()
        )
        await client.search_agents(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "parent=parent_value",
    ) in kw["metadata"]


def test_search_agents_flattened():
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.search_agents), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = agent.SearchAgentsResponse()
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.search_agents(
            parent="parent_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val


def test_search_agents_flattened_error():
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.search_agents(
            agent.SearchAgentsRequest(),
            parent="parent_value",
        )


@pytest.mark.asyncio
async def test_search_agents_flattened_async():
    client = AgentsAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.search_agents), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = agent.SearchAgentsResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            agent.SearchAgentsResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.search_agents(
            parent="parent_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val


@pytest.mark.asyncio
async def test_search_agents_flattened_error_async():
    client = AgentsAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.search_agents(
            agent.SearchAgentsRequest(),
            parent="parent_value",
        )


def test_search_agents_pager(transport_name: str = "grpc"):
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport_name,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.search_agents), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            agent.SearchAgentsResponse(
                agents=[
                    agent.Agent(),
                    agent.Agent(),
                    agent.Agent(),
                ],
                next_page_token="abc",
            ),
            agent.SearchAgentsResponse(
                agents=[],
                next_page_token="def",
            ),
            agent.SearchAgentsResponse(
                agents=[
                    agent.Agent(),
                ],
                next_page_token="ghi",
            ),
            agent.SearchAgentsResponse(
                agents=[
                    agent.Agent(),
                    agent.Agent(),
                ],
            ),
            RuntimeError,
        )

        metadata = ()
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("parent", ""),)),
        )
        pager = client.search_agents(request={})

        assert pager._metadata == metadata

        results = list(pager)
        assert len(results) == 6
        assert all(isinstance(i, agent.Agent) for i in results)


def test_search_agents_pages(transport_name: str = "grpc"):
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport_name,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.search_agents), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            agent.SearchAgentsResponse(
                agents=[
                    agent.Agent(),
                    agent.Agent(),
                    agent.Agent(),
                ],
                next_page_token="abc",
            ),
            agent.SearchAgentsResponse(
                agents=[],
                next_page_token="def",
            ),
            agent.SearchAgentsResponse(
                agents=[
                    agent.Agent(),
                ],
                next_page_token="ghi",
            ),
            agent.SearchAgentsResponse(
                agents=[
                    agent.Agent(),
                    agent.Agent(),
                ],
            ),
            RuntimeError,
        )
        pages = list(client.search_agents(request={}).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_search_agents_async_pager():
    client = AgentsAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.search_agents), "__call__", new_callable=mock.AsyncMock
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            agent.SearchAgentsResponse(
                agents=[
                    agent.Agent(),
                    agent.Agent(),
                    agent.Agent(),
                ],
                next_page_token="abc",
            ),
            agent.SearchAgentsResponse(
                agents=[],
                next_page_token="def",
            ),
            agent.SearchAgentsResponse(
                agents=[
                    agent.Agent(),
                ],
                next_page_token="ghi",
            ),
            agent.SearchAgentsResponse(
                agents=[
                    agent.Agent(),
                    agent.Agent(),
                ],
            ),
            RuntimeError,
        )
        async_pager = await client.search_agents(
            request={},
        )
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:  # pragma: no branch
            responses.append(response)

        assert len(responses) == 6
        assert all(isinstance(i, agent.Agent) for i in responses)


@pytest.mark.asyncio
async def test_search_agents_async_pages():
    client = AgentsAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.search_agents), "__call__", new_callable=mock.AsyncMock
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            agent.SearchAgentsResponse(
                agents=[
                    agent.Agent(),
                    agent.Agent(),
                    agent.Agent(),
                ],
                next_page_token="abc",
            ),
            agent.SearchAgentsResponse(
                agents=[],
                next_page_token="def",
            ),
            agent.SearchAgentsResponse(
                agents=[
                    agent.Agent(),
                ],
                next_page_token="ghi",
            ),
            agent.SearchAgentsResponse(
                agents=[
                    agent.Agent(),
                    agent.Agent(),
                ],
            ),
            RuntimeError,
        )
        pages = []
        # Workaround issue in python 3.9 related to code coverage by adding `# pragma: no branch`
        # See https://github.com/googleapis/gapic-generator-python/pull/1174#issuecomment-1025132372
        async for page_ in (  # pragma: no branch
            await client.search_agents(request={})
        ).pages:
            pages.append(page_)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.parametrize(
    "request_type",
    [
        agent.TrainAgentRequest,
        dict,
    ],
)
def test_train_agent(request_type, transport: str = "grpc"):
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.train_agent), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")
        response = client.train_agent(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == agent.TrainAgentRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_train_agent_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.train_agent), "__call__") as call:
        client.train_agent()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == agent.TrainAgentRequest()


@pytest.mark.asyncio
async def test_train_agent_async(
    transport: str = "grpc_asyncio", request_type=agent.TrainAgentRequest
):
    client = AgentsAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.train_agent), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        response = await client.train_agent(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == agent.TrainAgentRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_train_agent_async_from_dict():
    await test_train_agent_async(request_type=dict)


def test_train_agent_field_headers():
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = agent.TrainAgentRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.train_agent), "__call__") as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.train_agent(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "parent=parent_value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_train_agent_field_headers_async():
    client = AgentsAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = agent.TrainAgentRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.train_agent), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )
        await client.train_agent(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "parent=parent_value",
    ) in kw["metadata"]


def test_train_agent_flattened():
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.train_agent), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.train_agent(
            parent="parent_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val


def test_train_agent_flattened_error():
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.train_agent(
            agent.TrainAgentRequest(),
            parent="parent_value",
        )


@pytest.mark.asyncio
async def test_train_agent_flattened_async():
    client = AgentsAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.train_agent), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.train_agent(
            parent="parent_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val


@pytest.mark.asyncio
async def test_train_agent_flattened_error_async():
    client = AgentsAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.train_agent(
            agent.TrainAgentRequest(),
            parent="parent_value",
        )


@pytest.mark.parametrize(
    "request_type",
    [
        agent.ExportAgentRequest,
        dict,
    ],
)
def test_export_agent(request_type, transport: str = "grpc"):
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.export_agent), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")
        response = client.export_agent(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == agent.ExportAgentRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_export_agent_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.export_agent), "__call__") as call:
        client.export_agent()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == agent.ExportAgentRequest()


@pytest.mark.asyncio
async def test_export_agent_async(
    transport: str = "grpc_asyncio", request_type=agent.ExportAgentRequest
):
    client = AgentsAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.export_agent), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        response = await client.export_agent(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == agent.ExportAgentRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_export_agent_async_from_dict():
    await test_export_agent_async(request_type=dict)


def test_export_agent_field_headers():
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = agent.ExportAgentRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.export_agent), "__call__") as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.export_agent(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "parent=parent_value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_export_agent_field_headers_async():
    client = AgentsAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = agent.ExportAgentRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.export_agent), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )
        await client.export_agent(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "parent=parent_value",
    ) in kw["metadata"]


def test_export_agent_flattened():
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.export_agent), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.export_agent(
            parent="parent_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val


def test_export_agent_flattened_error():
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.export_agent(
            agent.ExportAgentRequest(),
            parent="parent_value",
        )


@pytest.mark.asyncio
async def test_export_agent_flattened_async():
    client = AgentsAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.export_agent), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.export_agent(
            parent="parent_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        arg = args[0].parent
        mock_val = "parent_value"
        assert arg == mock_val


@pytest.mark.asyncio
async def test_export_agent_flattened_error_async():
    client = AgentsAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.export_agent(
            agent.ExportAgentRequest(),
            parent="parent_value",
        )


@pytest.mark.parametrize(
    "request_type",
    [
        agent.ImportAgentRequest,
        dict,
    ],
)
def test_import_agent(request_type, transport: str = "grpc"):
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.import_agent), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")
        response = client.import_agent(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == agent.ImportAgentRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_import_agent_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.import_agent), "__call__") as call:
        client.import_agent()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == agent.ImportAgentRequest()


@pytest.mark.asyncio
async def test_import_agent_async(
    transport: str = "grpc_asyncio", request_type=agent.ImportAgentRequest
):
    client = AgentsAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.import_agent), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        response = await client.import_agent(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == agent.ImportAgentRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_import_agent_async_from_dict():
    await test_import_agent_async(request_type=dict)


def test_import_agent_field_headers():
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = agent.ImportAgentRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.import_agent), "__call__") as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.import_agent(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "parent=parent_value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_import_agent_field_headers_async():
    client = AgentsAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = agent.ImportAgentRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.import_agent), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )
        await client.import_agent(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "parent=parent_value",
    ) in kw["metadata"]


@pytest.mark.parametrize(
    "request_type",
    [
        agent.RestoreAgentRequest,
        dict,
    ],
)
def test_restore_agent(request_type, transport: str = "grpc"):
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.restore_agent), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")
        response = client.restore_agent(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == agent.RestoreAgentRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_restore_agent_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.restore_agent), "__call__") as call:
        client.restore_agent()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == agent.RestoreAgentRequest()


@pytest.mark.asyncio
async def test_restore_agent_async(
    transport: str = "grpc_asyncio", request_type=agent.RestoreAgentRequest
):
    client = AgentsAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.restore_agent), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/spam")
        )
        response = await client.restore_agent(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == agent.RestoreAgentRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


@pytest.mark.asyncio
async def test_restore_agent_async_from_dict():
    await test_restore_agent_async(request_type=dict)


def test_restore_agent_field_headers():
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = agent.RestoreAgentRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.restore_agent), "__call__") as call:
        call.return_value = operations_pb2.Operation(name="operations/op")
        client.restore_agent(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "parent=parent_value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_restore_agent_field_headers_async():
    client = AgentsAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = agent.RestoreAgentRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.restore_agent), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation(name="operations/op")
        )
        await client.restore_agent(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "parent=parent_value",
    ) in kw["metadata"]


@pytest.mark.parametrize(
    "request_type",
    [
        agent.GetValidationResultRequest,
        dict,
    ],
)
def test_get_validation_result(request_type, transport: str = "grpc"):
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_validation_result), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = validation_result.ValidationResult()
        response = client.get_validation_result(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == agent.GetValidationResultRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, validation_result.ValidationResult)


def test_get_validation_result_empty_call():
    # This test is a coverage failsafe to make sure that totally empty calls,
    # i.e. request == None and no flattened fields passed, work.
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport="grpc",
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_validation_result), "__call__"
    ) as call:
        client.get_validation_result()
        call.assert_called()
        _, args, _ = call.mock_calls[0]
        assert args[0] == agent.GetValidationResultRequest()


@pytest.mark.asyncio
async def test_get_validation_result_async(
    transport: str = "grpc_asyncio", request_type=agent.GetValidationResultRequest
):
    client = AgentsAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_validation_result), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            validation_result.ValidationResult()
        )
        response = await client.get_validation_result(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == agent.GetValidationResultRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, validation_result.ValidationResult)


@pytest.mark.asyncio
async def test_get_validation_result_async_from_dict():
    await test_get_validation_result_async(request_type=dict)


def test_get_validation_result_field_headers():
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = agent.GetValidationResultRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_validation_result), "__call__"
    ) as call:
        call.return_value = validation_result.ValidationResult()
        client.get_validation_result(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "parent=parent_value",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_get_validation_result_field_headers_async():
    client = AgentsAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = agent.GetValidationResultRequest()

    request.parent = "parent_value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_validation_result), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            validation_result.ValidationResult()
        )
        await client.get_validation_result(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "parent=parent_value",
    ) in kw["metadata"]


@pytest.mark.parametrize(
    "request_type",
    [
        agent.GetAgentRequest,
        dict,
    ],
)
def test_get_agent_rest(request_type):
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = agent.Agent(
            parent="parent_value",
            display_name="display_name_value",
            default_language_code="default_language_code_value",
            supported_language_codes=["supported_language_codes_value"],
            time_zone="time_zone_value",
            description="description_value",
            avatar_uri="avatar_uri_value",
            enable_logging=True,
            match_mode=agent.Agent.MatchMode.MATCH_MODE_HYBRID,
            classification_threshold=0.25520000000000004,
            api_version=agent.Agent.ApiVersion.API_VERSION_V1,
            tier=agent.Agent.Tier.TIER_STANDARD,
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        # Convert return value to protobuf type
        return_value = agent.Agent.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.get_agent(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, agent.Agent)
    assert response.parent == "parent_value"
    assert response.display_name == "display_name_value"
    assert response.default_language_code == "default_language_code_value"
    assert response.supported_language_codes == ["supported_language_codes_value"]
    assert response.time_zone == "time_zone_value"
    assert response.description == "description_value"
    assert response.avatar_uri == "avatar_uri_value"
    assert response.enable_logging is True
    assert response.match_mode == agent.Agent.MatchMode.MATCH_MODE_HYBRID
    assert math.isclose(
        response.classification_threshold, 0.25520000000000004, rel_tol=1e-6
    )
    assert response.api_version == agent.Agent.ApiVersion.API_VERSION_V1
    assert response.tier == agent.Agent.Tier.TIER_STANDARD


def test_get_agent_rest_required_fields(request_type=agent.GetAgentRequest):
    transport_class = transports.AgentsRestTransport

    request_init = {}
    request_init["parent"] = ""
    request = request_type(**request_init)
    pb_request = request_type.pb(request)
    jsonified_request = json.loads(
        json_format.MessageToJson(
            pb_request,
            including_default_value_fields=False,
            use_integers_for_enums=False,
        )
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=_AnonymousCredentialsWithUniverseDomain()
    ).get_agent._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["parent"] = "parent_value"

    unset_fields = transport_class(
        credentials=_AnonymousCredentialsWithUniverseDomain()
    ).get_agent._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "parent" in jsonified_request
    assert jsonified_request["parent"] == "parent_value"

    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = agent.Agent()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            pb_request = request_type.pb(request)
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "get",
                "query_params": pb_request,
            }
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200

            # Convert return value to protobuf type
            return_value = agent.Agent.pb(return_value)
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.get_agent(request)

            expected_params = [("$alt", "json;enum-encoding=int")]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_get_agent_rest_unset_required_fields():
    transport = transports.AgentsRestTransport(
        credentials=_AnonymousCredentialsWithUniverseDomain
    )

    unset_fields = transport.get_agent._get_unset_required_fields({})
    assert set(unset_fields) == (set(()) & set(("parent",)))


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_get_agent_rest_interceptors(null_interceptor):
    transport = transports.AgentsRestTransport(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        interceptor=None if null_interceptor else transports.AgentsRestInterceptor(),
    )
    client = AgentsClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.AgentsRestInterceptor, "post_get_agent"
    ) as post, mock.patch.object(
        transports.AgentsRestInterceptor, "pre_get_agent"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        pb_message = agent.GetAgentRequest.pb(agent.GetAgentRequest())
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = agent.Agent.to_json(agent.Agent())

        request = agent.GetAgentRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = agent.Agent()

        client.get_agent(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_get_agent_rest_bad_request(
    transport: str = "rest", request_type=agent.GetAgentRequest
):
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.get_agent(request)


def test_get_agent_rest_flattened():
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = agent.Agent()

        # get arguments that satisfy an http rule for this method
        sample_request = {"parent": "projects/sample1"}

        # get truthy value for each flattened field
        mock_args = dict(
            parent="parent_value",
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        # Convert return value to protobuf type
        return_value = agent.Agent.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.get_agent(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v2/{parent=projects/*}/agent" % client.transport._host, args[1]
        )


def test_get_agent_rest_flattened_error(transport: str = "rest"):
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_agent(
            agent.GetAgentRequest(),
            parent="parent_value",
        )


def test_get_agent_rest_error():
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(), transport="rest"
    )


@pytest.mark.parametrize(
    "request_type",
    [
        gcd_agent.SetAgentRequest,
        dict,
    ],
)
def test_set_agent_rest(request_type):
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"agent": {"parent": "projects/sample1"}}
    request_init["agent"] = {
        "parent": "projects/sample1",
        "display_name": "display_name_value",
        "default_language_code": "default_language_code_value",
        "supported_language_codes": [
            "supported_language_codes_value1",
            "supported_language_codes_value2",
        ],
        "time_zone": "time_zone_value",
        "description": "description_value",
        "avatar_uri": "avatar_uri_value",
        "enable_logging": True,
        "match_mode": 1,
        "classification_threshold": 0.25520000000000004,
        "api_version": 1,
        "tier": 1,
    }
    # The version of a generated dependency at test runtime may differ from the version used during generation.
    # Delete any fields which are not present in the current runtime dependency
    # See https://github.com/googleapis/gapic-generator-python/issues/1748

    # Determine if the message type is proto-plus or protobuf
    test_field = gcd_agent.SetAgentRequest.meta.fields["agent"]

    def get_message_fields(field):
        # Given a field which is a message (composite type), return a list with
        # all the fields of the message.
        # If the field is not a composite type, return an empty list.
        message_fields = []

        if hasattr(field, "message") and field.message:
            is_field_type_proto_plus_type = not hasattr(field.message, "DESCRIPTOR")

            if is_field_type_proto_plus_type:
                message_fields = field.message.meta.fields.values()
            # Add `# pragma: NO COVER` because there may not be any `*_pb2` field types
            else:  # pragma: NO COVER
                message_fields = field.message.DESCRIPTOR.fields
        return message_fields

    runtime_nested_fields = [
        (field.name, nested_field.name)
        for field in get_message_fields(test_field)
        for nested_field in get_message_fields(field)
    ]

    subfields_not_in_runtime = []

    # For each item in the sample request, create a list of sub fields which are not present at runtime
    # Add `# pragma: NO COVER` because this test code will not run if all subfields are present at runtime
    for field, value in request_init["agent"].items():  # pragma: NO COVER
        result = None
        is_repeated = False
        # For repeated fields
        if isinstance(value, list) and len(value):
            is_repeated = True
            result = value[0]
        # For fields where the type is another message
        if isinstance(value, dict):
            result = value

        if result and hasattr(result, "keys"):
            for subfield in result.keys():
                if (field, subfield) not in runtime_nested_fields:
                    subfields_not_in_runtime.append(
                        {
                            "field": field,
                            "subfield": subfield,
                            "is_repeated": is_repeated,
                        }
                    )

    # Remove fields from the sample request which are not present in the runtime version of the dependency
    # Add `# pragma: NO COVER` because this test code will not run if all subfields are present at runtime
    for subfield_to_delete in subfields_not_in_runtime:  # pragma: NO COVER
        field = subfield_to_delete.get("field")
        field_repeated = subfield_to_delete.get("is_repeated")
        subfield = subfield_to_delete.get("subfield")
        if subfield:
            if field_repeated:
                for i in range(0, len(request_init["agent"][field])):
                    del request_init["agent"][field][i][subfield]
            else:
                del request_init["agent"][field][subfield]
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = gcd_agent.Agent(
            parent="parent_value",
            display_name="display_name_value",
            default_language_code="default_language_code_value",
            supported_language_codes=["supported_language_codes_value"],
            time_zone="time_zone_value",
            description="description_value",
            avatar_uri="avatar_uri_value",
            enable_logging=True,
            match_mode=gcd_agent.Agent.MatchMode.MATCH_MODE_HYBRID,
            classification_threshold=0.25520000000000004,
            api_version=gcd_agent.Agent.ApiVersion.API_VERSION_V1,
            tier=gcd_agent.Agent.Tier.TIER_STANDARD,
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        # Convert return value to protobuf type
        return_value = gcd_agent.Agent.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.set_agent(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, gcd_agent.Agent)
    assert response.parent == "parent_value"
    assert response.display_name == "display_name_value"
    assert response.default_language_code == "default_language_code_value"
    assert response.supported_language_codes == ["supported_language_codes_value"]
    assert response.time_zone == "time_zone_value"
    assert response.description == "description_value"
    assert response.avatar_uri == "avatar_uri_value"
    assert response.enable_logging is True
    assert response.match_mode == gcd_agent.Agent.MatchMode.MATCH_MODE_HYBRID
    assert math.isclose(
        response.classification_threshold, 0.25520000000000004, rel_tol=1e-6
    )
    assert response.api_version == gcd_agent.Agent.ApiVersion.API_VERSION_V1
    assert response.tier == gcd_agent.Agent.Tier.TIER_STANDARD


def test_set_agent_rest_required_fields(request_type=gcd_agent.SetAgentRequest):
    transport_class = transports.AgentsRestTransport

    request_init = {}
    request = request_type(**request_init)
    pb_request = request_type.pb(request)
    jsonified_request = json.loads(
        json_format.MessageToJson(
            pb_request,
            including_default_value_fields=False,
            use_integers_for_enums=False,
        )
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=_AnonymousCredentialsWithUniverseDomain()
    ).set_agent._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    unset_fields = transport_class(
        credentials=_AnonymousCredentialsWithUniverseDomain()
    ).set_agent._get_unset_required_fields(jsonified_request)
    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(("update_mask",))
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone

    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = gcd_agent.Agent()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            pb_request = request_type.pb(request)
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "post",
                "query_params": pb_request,
            }
            transcode_result["body"] = pb_request
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200

            # Convert return value to protobuf type
            return_value = gcd_agent.Agent.pb(return_value)
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.set_agent(request)

            expected_params = [("$alt", "json;enum-encoding=int")]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_set_agent_rest_unset_required_fields():
    transport = transports.AgentsRestTransport(
        credentials=_AnonymousCredentialsWithUniverseDomain
    )

    unset_fields = transport.set_agent._get_unset_required_fields({})
    assert set(unset_fields) == (set(("updateMask",)) & set(("agent",)))


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_set_agent_rest_interceptors(null_interceptor):
    transport = transports.AgentsRestTransport(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        interceptor=None if null_interceptor else transports.AgentsRestInterceptor(),
    )
    client = AgentsClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.AgentsRestInterceptor, "post_set_agent"
    ) as post, mock.patch.object(
        transports.AgentsRestInterceptor, "pre_set_agent"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        pb_message = gcd_agent.SetAgentRequest.pb(gcd_agent.SetAgentRequest())
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = gcd_agent.Agent.to_json(gcd_agent.Agent())

        request = gcd_agent.SetAgentRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = gcd_agent.Agent()

        client.set_agent(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_set_agent_rest_bad_request(
    transport: str = "rest", request_type=gcd_agent.SetAgentRequest
):
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"agent": {"parent": "projects/sample1"}}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.set_agent(request)


def test_set_agent_rest_flattened():
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = gcd_agent.Agent()

        # get arguments that satisfy an http rule for this method
        sample_request = {"agent": {"parent": "projects/sample1"}}

        # get truthy value for each flattened field
        mock_args = dict(
            agent=gcd_agent.Agent(parent="parent_value"),
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        # Convert return value to protobuf type
        return_value = gcd_agent.Agent.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.set_agent(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v2/{agent.parent=projects/*}/agent" % client.transport._host, args[1]
        )


def test_set_agent_rest_flattened_error(transport: str = "rest"):
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.set_agent(
            gcd_agent.SetAgentRequest(),
            agent=gcd_agent.Agent(parent="parent_value"),
        )


def test_set_agent_rest_error():
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(), transport="rest"
    )


@pytest.mark.parametrize(
    "request_type",
    [
        agent.DeleteAgentRequest,
        dict,
    ],
)
def test_delete_agent_rest(request_type):
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = None

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = ""

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.delete_agent(request)

    # Establish that the response is the type that we expect.
    assert response is None


def test_delete_agent_rest_required_fields(request_type=agent.DeleteAgentRequest):
    transport_class = transports.AgentsRestTransport

    request_init = {}
    request_init["parent"] = ""
    request = request_type(**request_init)
    pb_request = request_type.pb(request)
    jsonified_request = json.loads(
        json_format.MessageToJson(
            pb_request,
            including_default_value_fields=False,
            use_integers_for_enums=False,
        )
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=_AnonymousCredentialsWithUniverseDomain()
    ).delete_agent._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["parent"] = "parent_value"

    unset_fields = transport_class(
        credentials=_AnonymousCredentialsWithUniverseDomain()
    ).delete_agent._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "parent" in jsonified_request
    assert jsonified_request["parent"] == "parent_value"

    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = None
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            pb_request = request_type.pb(request)
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "delete",
                "query_params": pb_request,
            }
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = ""

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.delete_agent(request)

            expected_params = [("$alt", "json;enum-encoding=int")]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_delete_agent_rest_unset_required_fields():
    transport = transports.AgentsRestTransport(
        credentials=_AnonymousCredentialsWithUniverseDomain
    )

    unset_fields = transport.delete_agent._get_unset_required_fields({})
    assert set(unset_fields) == (set(()) & set(("parent",)))


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_delete_agent_rest_interceptors(null_interceptor):
    transport = transports.AgentsRestTransport(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        interceptor=None if null_interceptor else transports.AgentsRestInterceptor(),
    )
    client = AgentsClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.AgentsRestInterceptor, "pre_delete_agent"
    ) as pre:
        pre.assert_not_called()
        pb_message = agent.DeleteAgentRequest.pb(agent.DeleteAgentRequest())
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()

        request = agent.DeleteAgentRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata

        client.delete_agent(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()


def test_delete_agent_rest_bad_request(
    transport: str = "rest", request_type=agent.DeleteAgentRequest
):
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.delete_agent(request)


def test_delete_agent_rest_flattened():
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = None

        # get arguments that satisfy an http rule for this method
        sample_request = {"parent": "projects/sample1"}

        # get truthy value for each flattened field
        mock_args = dict(
            parent="parent_value",
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = ""
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.delete_agent(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v2/{parent=projects/*}/agent" % client.transport._host, args[1]
        )


def test_delete_agent_rest_flattened_error(transport: str = "rest"):
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_agent(
            agent.DeleteAgentRequest(),
            parent="parent_value",
        )


def test_delete_agent_rest_error():
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(), transport="rest"
    )


@pytest.mark.parametrize(
    "request_type",
    [
        agent.SearchAgentsRequest,
        dict,
    ],
)
def test_search_agents_rest(request_type):
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = agent.SearchAgentsResponse(
            next_page_token="next_page_token_value",
        )

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        # Convert return value to protobuf type
        return_value = agent.SearchAgentsResponse.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.search_agents(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.SearchAgentsPager)
    assert response.next_page_token == "next_page_token_value"


def test_search_agents_rest_required_fields(request_type=agent.SearchAgentsRequest):
    transport_class = transports.AgentsRestTransport

    request_init = {}
    request_init["parent"] = ""
    request = request_type(**request_init)
    pb_request = request_type.pb(request)
    jsonified_request = json.loads(
        json_format.MessageToJson(
            pb_request,
            including_default_value_fields=False,
            use_integers_for_enums=False,
        )
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=_AnonymousCredentialsWithUniverseDomain()
    ).search_agents._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["parent"] = "parent_value"

    unset_fields = transport_class(
        credentials=_AnonymousCredentialsWithUniverseDomain()
    ).search_agents._get_unset_required_fields(jsonified_request)
    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(
        (
            "page_size",
            "page_token",
        )
    )
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "parent" in jsonified_request
    assert jsonified_request["parent"] == "parent_value"

    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = agent.SearchAgentsResponse()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            pb_request = request_type.pb(request)
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "get",
                "query_params": pb_request,
            }
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200

            # Convert return value to protobuf type
            return_value = agent.SearchAgentsResponse.pb(return_value)
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.search_agents(request)

            expected_params = [("$alt", "json;enum-encoding=int")]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_search_agents_rest_unset_required_fields():
    transport = transports.AgentsRestTransport(
        credentials=_AnonymousCredentialsWithUniverseDomain
    )

    unset_fields = transport.search_agents._get_unset_required_fields({})
    assert set(unset_fields) == (
        set(
            (
                "pageSize",
                "pageToken",
            )
        )
        & set(("parent",))
    )


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_search_agents_rest_interceptors(null_interceptor):
    transport = transports.AgentsRestTransport(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        interceptor=None if null_interceptor else transports.AgentsRestInterceptor(),
    )
    client = AgentsClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.AgentsRestInterceptor, "post_search_agents"
    ) as post, mock.patch.object(
        transports.AgentsRestInterceptor, "pre_search_agents"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        pb_message = agent.SearchAgentsRequest.pb(agent.SearchAgentsRequest())
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = agent.SearchAgentsResponse.to_json(
            agent.SearchAgentsResponse()
        )

        request = agent.SearchAgentsRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = agent.SearchAgentsResponse()

        client.search_agents(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_search_agents_rest_bad_request(
    transport: str = "rest", request_type=agent.SearchAgentsRequest
):
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.search_agents(request)


def test_search_agents_rest_flattened():
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = agent.SearchAgentsResponse()

        # get arguments that satisfy an http rule for this method
        sample_request = {"parent": "projects/sample1"}

        # get truthy value for each flattened field
        mock_args = dict(
            parent="parent_value",
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        # Convert return value to protobuf type
        return_value = agent.SearchAgentsResponse.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.search_agents(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v2/{parent=projects/*}/agent:search" % client.transport._host, args[1]
        )


def test_search_agents_rest_flattened_error(transport: str = "rest"):
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.search_agents(
            agent.SearchAgentsRequest(),
            parent="parent_value",
        )


def test_search_agents_rest_pager(transport: str = "rest"):
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # TODO(kbandes): remove this mock unless there's a good reason for it.
        # with mock.patch.object(path_template, 'transcode') as transcode:
        # Set the response as a series of pages
        response = (
            agent.SearchAgentsResponse(
                agents=[
                    agent.Agent(),
                    agent.Agent(),
                    agent.Agent(),
                ],
                next_page_token="abc",
            ),
            agent.SearchAgentsResponse(
                agents=[],
                next_page_token="def",
            ),
            agent.SearchAgentsResponse(
                agents=[
                    agent.Agent(),
                ],
                next_page_token="ghi",
            ),
            agent.SearchAgentsResponse(
                agents=[
                    agent.Agent(),
                    agent.Agent(),
                ],
            ),
        )
        # Two responses for two calls
        response = response + response

        # Wrap the values into proper Response objs
        response = tuple(agent.SearchAgentsResponse.to_json(x) for x in response)
        return_values = tuple(Response() for i in response)
        for return_val, response_val in zip(return_values, response):
            return_val._content = response_val.encode("UTF-8")
            return_val.status_code = 200
        req.side_effect = return_values

        sample_request = {"parent": "projects/sample1"}

        pager = client.search_agents(request=sample_request)

        results = list(pager)
        assert len(results) == 6
        assert all(isinstance(i, agent.Agent) for i in results)

        pages = list(client.search_agents(request=sample_request).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.parametrize(
    "request_type",
    [
        agent.TrainAgentRequest,
        dict,
    ],
)
def test_train_agent_rest(request_type):
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation(name="operations/spam")

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.train_agent(request)

    # Establish that the response is the type that we expect.
    assert response.operation.name == "operations/spam"


def test_train_agent_rest_required_fields(request_type=agent.TrainAgentRequest):
    transport_class = transports.AgentsRestTransport

    request_init = {}
    request_init["parent"] = ""
    request = request_type(**request_init)
    pb_request = request_type.pb(request)
    jsonified_request = json.loads(
        json_format.MessageToJson(
            pb_request,
            including_default_value_fields=False,
            use_integers_for_enums=False,
        )
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=_AnonymousCredentialsWithUniverseDomain()
    ).train_agent._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["parent"] = "parent_value"

    unset_fields = transport_class(
        credentials=_AnonymousCredentialsWithUniverseDomain()
    ).train_agent._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "parent" in jsonified_request
    assert jsonified_request["parent"] == "parent_value"

    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = operations_pb2.Operation(name="operations/spam")
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            pb_request = request_type.pb(request)
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "post",
                "query_params": pb_request,
            }
            transcode_result["body"] = pb_request
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.train_agent(request)

            expected_params = [("$alt", "json;enum-encoding=int")]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_train_agent_rest_unset_required_fields():
    transport = transports.AgentsRestTransport(
        credentials=_AnonymousCredentialsWithUniverseDomain
    )

    unset_fields = transport.train_agent._get_unset_required_fields({})
    assert set(unset_fields) == (set(()) & set(("parent",)))


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_train_agent_rest_interceptors(null_interceptor):
    transport = transports.AgentsRestTransport(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        interceptor=None if null_interceptor else transports.AgentsRestInterceptor(),
    )
    client = AgentsClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        operation.Operation, "_set_result_from_operation"
    ), mock.patch.object(
        transports.AgentsRestInterceptor, "post_train_agent"
    ) as post, mock.patch.object(
        transports.AgentsRestInterceptor, "pre_train_agent"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        pb_message = agent.TrainAgentRequest.pb(agent.TrainAgentRequest())
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = json_format.MessageToJson(
            operations_pb2.Operation()
        )

        request = agent.TrainAgentRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = operations_pb2.Operation()

        client.train_agent(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_train_agent_rest_bad_request(
    transport: str = "rest", request_type=agent.TrainAgentRequest
):
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.train_agent(request)


def test_train_agent_rest_flattened():
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation(name="operations/spam")

        # get arguments that satisfy an http rule for this method
        sample_request = {"parent": "projects/sample1"}

        # get truthy value for each flattened field
        mock_args = dict(
            parent="parent_value",
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.train_agent(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v2/{parent=projects/*}/agent:train" % client.transport._host, args[1]
        )


def test_train_agent_rest_flattened_error(transport: str = "rest"):
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.train_agent(
            agent.TrainAgentRequest(),
            parent="parent_value",
        )


def test_train_agent_rest_error():
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(), transport="rest"
    )


@pytest.mark.parametrize(
    "request_type",
    [
        agent.ExportAgentRequest,
        dict,
    ],
)
def test_export_agent_rest(request_type):
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation(name="operations/spam")

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.export_agent(request)

    # Establish that the response is the type that we expect.
    assert response.operation.name == "operations/spam"


def test_export_agent_rest_required_fields(request_type=agent.ExportAgentRequest):
    transport_class = transports.AgentsRestTransport

    request_init = {}
    request_init["parent"] = ""
    request_init["agent_uri"] = ""
    request = request_type(**request_init)
    pb_request = request_type.pb(request)
    jsonified_request = json.loads(
        json_format.MessageToJson(
            pb_request,
            including_default_value_fields=False,
            use_integers_for_enums=False,
        )
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=_AnonymousCredentialsWithUniverseDomain()
    ).export_agent._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["parent"] = "parent_value"
    jsonified_request["agentUri"] = "agent_uri_value"

    unset_fields = transport_class(
        credentials=_AnonymousCredentialsWithUniverseDomain()
    ).export_agent._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "parent" in jsonified_request
    assert jsonified_request["parent"] == "parent_value"
    assert "agentUri" in jsonified_request
    assert jsonified_request["agentUri"] == "agent_uri_value"

    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = operations_pb2.Operation(name="operations/spam")
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            pb_request = request_type.pb(request)
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "post",
                "query_params": pb_request,
            }
            transcode_result["body"] = pb_request
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.export_agent(request)

            expected_params = [("$alt", "json;enum-encoding=int")]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_export_agent_rest_unset_required_fields():
    transport = transports.AgentsRestTransport(
        credentials=_AnonymousCredentialsWithUniverseDomain
    )

    unset_fields = transport.export_agent._get_unset_required_fields({})
    assert set(unset_fields) == (
        set(())
        & set(
            (
                "parent",
                "agentUri",
            )
        )
    )


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_export_agent_rest_interceptors(null_interceptor):
    transport = transports.AgentsRestTransport(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        interceptor=None if null_interceptor else transports.AgentsRestInterceptor(),
    )
    client = AgentsClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        operation.Operation, "_set_result_from_operation"
    ), mock.patch.object(
        transports.AgentsRestInterceptor, "post_export_agent"
    ) as post, mock.patch.object(
        transports.AgentsRestInterceptor, "pre_export_agent"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        pb_message = agent.ExportAgentRequest.pb(agent.ExportAgentRequest())
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = json_format.MessageToJson(
            operations_pb2.Operation()
        )

        request = agent.ExportAgentRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = operations_pb2.Operation()

        client.export_agent(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_export_agent_rest_bad_request(
    transport: str = "rest", request_type=agent.ExportAgentRequest
):
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.export_agent(request)


def test_export_agent_rest_flattened():
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport="rest",
    )

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation(name="operations/spam")

        # get arguments that satisfy an http rule for this method
        sample_request = {"parent": "projects/sample1"}

        # get truthy value for each flattened field
        mock_args = dict(
            parent="parent_value",
        )
        mock_args.update(sample_request)

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)
        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        client.export_agent(**mock_args)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(req.mock_calls) == 1
        _, args, _ = req.mock_calls[0]
        assert path_template.validate(
            "%s/v2/{parent=projects/*}/agent:export" % client.transport._host, args[1]
        )


def test_export_agent_rest_flattened_error(transport: str = "rest"):
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.export_agent(
            agent.ExportAgentRequest(),
            parent="parent_value",
        )


def test_export_agent_rest_error():
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(), transport="rest"
    )


@pytest.mark.parametrize(
    "request_type",
    [
        agent.ImportAgentRequest,
        dict,
    ],
)
def test_import_agent_rest(request_type):
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation(name="operations/spam")

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.import_agent(request)

    # Establish that the response is the type that we expect.
    assert response.operation.name == "operations/spam"


def test_import_agent_rest_required_fields(request_type=agent.ImportAgentRequest):
    transport_class = transports.AgentsRestTransport

    request_init = {}
    request_init["parent"] = ""
    request = request_type(**request_init)
    pb_request = request_type.pb(request)
    jsonified_request = json.loads(
        json_format.MessageToJson(
            pb_request,
            including_default_value_fields=False,
            use_integers_for_enums=False,
        )
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=_AnonymousCredentialsWithUniverseDomain()
    ).import_agent._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["parent"] = "parent_value"

    unset_fields = transport_class(
        credentials=_AnonymousCredentialsWithUniverseDomain()
    ).import_agent._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "parent" in jsonified_request
    assert jsonified_request["parent"] == "parent_value"

    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = operations_pb2.Operation(name="operations/spam")
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            pb_request = request_type.pb(request)
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "post",
                "query_params": pb_request,
            }
            transcode_result["body"] = pb_request
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.import_agent(request)

            expected_params = [("$alt", "json;enum-encoding=int")]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_import_agent_rest_unset_required_fields():
    transport = transports.AgentsRestTransport(
        credentials=_AnonymousCredentialsWithUniverseDomain
    )

    unset_fields = transport.import_agent._get_unset_required_fields({})
    assert set(unset_fields) == (set(()) & set(("parent",)))


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_import_agent_rest_interceptors(null_interceptor):
    transport = transports.AgentsRestTransport(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        interceptor=None if null_interceptor else transports.AgentsRestInterceptor(),
    )
    client = AgentsClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        operation.Operation, "_set_result_from_operation"
    ), mock.patch.object(
        transports.AgentsRestInterceptor, "post_import_agent"
    ) as post, mock.patch.object(
        transports.AgentsRestInterceptor, "pre_import_agent"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        pb_message = agent.ImportAgentRequest.pb(agent.ImportAgentRequest())
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = json_format.MessageToJson(
            operations_pb2.Operation()
        )

        request = agent.ImportAgentRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = operations_pb2.Operation()

        client.import_agent(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_import_agent_rest_bad_request(
    transport: str = "rest", request_type=agent.ImportAgentRequest
):
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.import_agent(request)


def test_import_agent_rest_error():
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(), transport="rest"
    )


@pytest.mark.parametrize(
    "request_type",
    [
        agent.RestoreAgentRequest,
        dict,
    ],
)
def test_restore_agent_rest(request_type):
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation(name="operations/spam")

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.restore_agent(request)

    # Establish that the response is the type that we expect.
    assert response.operation.name == "operations/spam"


def test_restore_agent_rest_required_fields(request_type=agent.RestoreAgentRequest):
    transport_class = transports.AgentsRestTransport

    request_init = {}
    request_init["parent"] = ""
    request = request_type(**request_init)
    pb_request = request_type.pb(request)
    jsonified_request = json.loads(
        json_format.MessageToJson(
            pb_request,
            including_default_value_fields=False,
            use_integers_for_enums=False,
        )
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=_AnonymousCredentialsWithUniverseDomain()
    ).restore_agent._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["parent"] = "parent_value"

    unset_fields = transport_class(
        credentials=_AnonymousCredentialsWithUniverseDomain()
    ).restore_agent._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "parent" in jsonified_request
    assert jsonified_request["parent"] == "parent_value"

    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = operations_pb2.Operation(name="operations/spam")
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            pb_request = request_type.pb(request)
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "post",
                "query_params": pb_request,
            }
            transcode_result["body"] = pb_request
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.restore_agent(request)

            expected_params = [("$alt", "json;enum-encoding=int")]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_restore_agent_rest_unset_required_fields():
    transport = transports.AgentsRestTransport(
        credentials=_AnonymousCredentialsWithUniverseDomain
    )

    unset_fields = transport.restore_agent._get_unset_required_fields({})
    assert set(unset_fields) == (set(()) & set(("parent",)))


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_restore_agent_rest_interceptors(null_interceptor):
    transport = transports.AgentsRestTransport(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        interceptor=None if null_interceptor else transports.AgentsRestInterceptor(),
    )
    client = AgentsClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        operation.Operation, "_set_result_from_operation"
    ), mock.patch.object(
        transports.AgentsRestInterceptor, "post_restore_agent"
    ) as post, mock.patch.object(
        transports.AgentsRestInterceptor, "pre_restore_agent"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        pb_message = agent.RestoreAgentRequest.pb(agent.RestoreAgentRequest())
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = json_format.MessageToJson(
            operations_pb2.Operation()
        )

        request = agent.RestoreAgentRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = operations_pb2.Operation()

        client.restore_agent(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_restore_agent_rest_bad_request(
    transport: str = "rest", request_type=agent.RestoreAgentRequest
):
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.restore_agent(request)


def test_restore_agent_rest_error():
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(), transport="rest"
    )


@pytest.mark.parametrize(
    "request_type",
    [
        agent.GetValidationResultRequest,
        dict,
    ],
)
def test_get_validation_result_rest(request_type):
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport="rest",
    )

    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = validation_result.ValidationResult()

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        # Convert return value to protobuf type
        return_value = validation_result.ValidationResult.pb(return_value)
        json_return_value = json_format.MessageToJson(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value
        response = client.get_validation_result(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, validation_result.ValidationResult)


def test_get_validation_result_rest_required_fields(
    request_type=agent.GetValidationResultRequest,
):
    transport_class = transports.AgentsRestTransport

    request_init = {}
    request_init["parent"] = ""
    request = request_type(**request_init)
    pb_request = request_type.pb(request)
    jsonified_request = json.loads(
        json_format.MessageToJson(
            pb_request,
            including_default_value_fields=False,
            use_integers_for_enums=False,
        )
    )

    # verify fields with default values are dropped

    unset_fields = transport_class(
        credentials=_AnonymousCredentialsWithUniverseDomain()
    ).get_validation_result._get_unset_required_fields(jsonified_request)
    jsonified_request.update(unset_fields)

    # verify required fields with default values are now present

    jsonified_request["parent"] = "parent_value"

    unset_fields = transport_class(
        credentials=_AnonymousCredentialsWithUniverseDomain()
    ).get_validation_result._get_unset_required_fields(jsonified_request)
    # Check that path parameters and body parameters are not mixing in.
    assert not set(unset_fields) - set(("language_code",))
    jsonified_request.update(unset_fields)

    # verify required fields with non-default values are left alone
    assert "parent" in jsonified_request
    assert jsonified_request["parent"] == "parent_value"

    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport="rest",
    )
    request = request_type(**request_init)

    # Designate an appropriate value for the returned response.
    return_value = validation_result.ValidationResult()
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(Session, "request") as req:
        # We need to mock transcode() because providing default values
        # for required fields will fail the real version if the http_options
        # expect actual values for those fields.
        with mock.patch.object(path_template, "transcode") as transcode:
            # A uri without fields and an empty body will force all the
            # request fields to show up in the query_params.
            pb_request = request_type.pb(request)
            transcode_result = {
                "uri": "v1/sample_method",
                "method": "get",
                "query_params": pb_request,
            }
            transcode.return_value = transcode_result

            response_value = Response()
            response_value.status_code = 200

            # Convert return value to protobuf type
            return_value = validation_result.ValidationResult.pb(return_value)
            json_return_value = json_format.MessageToJson(return_value)

            response_value._content = json_return_value.encode("UTF-8")
            req.return_value = response_value

            response = client.get_validation_result(request)

            expected_params = [("$alt", "json;enum-encoding=int")]
            actual_params = req.call_args.kwargs["params"]
            assert expected_params == actual_params


def test_get_validation_result_rest_unset_required_fields():
    transport = transports.AgentsRestTransport(
        credentials=_AnonymousCredentialsWithUniverseDomain
    )

    unset_fields = transport.get_validation_result._get_unset_required_fields({})
    assert set(unset_fields) == (set(("languageCode",)) & set(("parent",)))


@pytest.mark.parametrize("null_interceptor", [True, False])
def test_get_validation_result_rest_interceptors(null_interceptor):
    transport = transports.AgentsRestTransport(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        interceptor=None if null_interceptor else transports.AgentsRestInterceptor(),
    )
    client = AgentsClient(transport=transport)
    with mock.patch.object(
        type(client.transport._session), "request"
    ) as req, mock.patch.object(
        path_template, "transcode"
    ) as transcode, mock.patch.object(
        transports.AgentsRestInterceptor, "post_get_validation_result"
    ) as post, mock.patch.object(
        transports.AgentsRestInterceptor, "pre_get_validation_result"
    ) as pre:
        pre.assert_not_called()
        post.assert_not_called()
        pb_message = agent.GetValidationResultRequest.pb(
            agent.GetValidationResultRequest()
        )
        transcode.return_value = {
            "method": "post",
            "uri": "my_uri",
            "body": pb_message,
            "query_params": pb_message,
        }

        req.return_value = Response()
        req.return_value.status_code = 200
        req.return_value.request = PreparedRequest()
        req.return_value._content = validation_result.ValidationResult.to_json(
            validation_result.ValidationResult()
        )

        request = agent.GetValidationResultRequest()
        metadata = [
            ("key", "val"),
            ("cephalopod", "squid"),
        ]
        pre.return_value = request, metadata
        post.return_value = validation_result.ValidationResult()

        client.get_validation_result(
            request,
            metadata=[
                ("key", "val"),
                ("cephalopod", "squid"),
            ],
        )

        pre.assert_called_once()
        post.assert_called_once()


def test_get_validation_result_rest_bad_request(
    transport: str = "rest", request_type=agent.GetValidationResultRequest
):
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # send a request that will satisfy transcoding
    request_init = {"parent": "projects/sample1"}
    request = request_type(**request_init)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.get_validation_result(request)


def test_get_validation_result_rest_error():
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(), transport="rest"
    )


def test_credentials_transport_error():
    # It is an error to provide credentials and a transport instance.
    transport = transports.AgentsGrpcTransport(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )
    with pytest.raises(ValueError):
        client = AgentsClient(
            credentials=_AnonymousCredentialsWithUniverseDomain(),
            transport=transport,
        )

    # It is an error to provide a credentials file and a transport instance.
    transport = transports.AgentsGrpcTransport(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )
    with pytest.raises(ValueError):
        client = AgentsClient(
            client_options={"credentials_file": "credentials.json"},
            transport=transport,
        )

    # It is an error to provide an api_key and a transport instance.
    transport = transports.AgentsGrpcTransport(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )
    options = client_options.ClientOptions()
    options.api_key = "api_key"
    with pytest.raises(ValueError):
        client = AgentsClient(
            client_options=options,
            transport=transport,
        )

    # It is an error to provide an api_key and a credential.
    options = client_options.ClientOptions()
    options.api_key = "api_key"
    with pytest.raises(ValueError):
        client = AgentsClient(
            client_options=options,
            credentials=_AnonymousCredentialsWithUniverseDomain(),
        )

    # It is an error to provide scopes and a transport instance.
    transport = transports.AgentsGrpcTransport(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )
    with pytest.raises(ValueError):
        client = AgentsClient(
            client_options={"scopes": ["1", "2"]},
            transport=transport,
        )


def test_transport_instance():
    # A client may be instantiated with a custom transport instance.
    transport = transports.AgentsGrpcTransport(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )
    client = AgentsClient(transport=transport)
    assert client.transport is transport


def test_transport_get_channel():
    # A client may be instantiated with a custom transport instance.
    transport = transports.AgentsGrpcTransport(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )
    channel = transport.grpc_channel
    assert channel

    transport = transports.AgentsGrpcAsyncIOTransport(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )
    channel = transport.grpc_channel
    assert channel


@pytest.mark.parametrize(
    "transport_class",
    [
        transports.AgentsGrpcTransport,
        transports.AgentsGrpcAsyncIOTransport,
        transports.AgentsRestTransport,
    ],
)
def test_transport_adc(transport_class):
    # Test default credentials are used if not provided.
    with mock.patch.object(google.auth, "default") as adc:
        adc.return_value = (_AnonymousCredentialsWithUniverseDomain(), None)
        transport_class()
        adc.assert_called_once()


@pytest.mark.parametrize(
    "transport_name",
    [
        "grpc",
        "rest",
    ],
)
def test_transport_kind(transport_name):
    transport = AgentsClient.get_transport_class(transport_name)(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )
    assert transport.kind == transport_name


def test_transport_grpc_default():
    # A client should use the gRPC transport by default.
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )
    assert isinstance(
        client.transport,
        transports.AgentsGrpcTransport,
    )


def test_agents_base_transport_error():
    # Passing both a credentials object and credentials_file should raise an error
    with pytest.raises(core_exceptions.DuplicateCredentialArgs):
        transport = transports.AgentsTransport(
            credentials=_AnonymousCredentialsWithUniverseDomain(),
            credentials_file="credentials.json",
        )


def test_agents_base_transport():
    # Instantiate the base transport.
    with mock.patch(
        "google.cloud.dialogflow_v2.services.agents.transports.AgentsTransport.__init__"
    ) as Transport:
        Transport.return_value = None
        transport = transports.AgentsTransport(
            credentials=_AnonymousCredentialsWithUniverseDomain(),
        )

    # Every method on the transport should just blindly
    # raise NotImplementedError.
    methods = (
        "get_agent",
        "set_agent",
        "delete_agent",
        "search_agents",
        "train_agent",
        "export_agent",
        "import_agent",
        "restore_agent",
        "get_validation_result",
        "get_location",
        "list_locations",
        "get_operation",
        "cancel_operation",
        "list_operations",
    )
    for method in methods:
        with pytest.raises(NotImplementedError):
            getattr(transport, method)(request=object())

    with pytest.raises(NotImplementedError):
        transport.close()

    # Additionally, the LRO client (a property) should
    # also raise NotImplementedError
    with pytest.raises(NotImplementedError):
        transport.operations_client

    # Catch all for all remaining methods and properties
    remainder = [
        "kind",
    ]
    for r in remainder:
        with pytest.raises(NotImplementedError):
            getattr(transport, r)()


def test_agents_base_transport_with_credentials_file():
    # Instantiate the base transport with a credentials file
    with mock.patch.object(
        google.auth, "load_credentials_from_file", autospec=True
    ) as load_creds, mock.patch(
        "google.cloud.dialogflow_v2.services.agents.transports.AgentsTransport._prep_wrapped_messages"
    ) as Transport:
        Transport.return_value = None
        load_creds.return_value = (_AnonymousCredentialsWithUniverseDomain(), None)
        transport = transports.AgentsTransport(
            credentials_file="credentials.json",
            quota_project_id="octopus",
        )
        load_creds.assert_called_once_with(
            "credentials.json",
            scopes=None,
            default_scopes=(
                "https://www.googleapis.com/auth/cloud-platform",
                "https://www.googleapis.com/auth/dialogflow",
            ),
            quota_project_id="octopus",
        )


def test_agents_base_transport_with_adc():
    # Test the default credentials are used if credentials and credentials_file are None.
    with mock.patch.object(google.auth, "default", autospec=True) as adc, mock.patch(
        "google.cloud.dialogflow_v2.services.agents.transports.AgentsTransport._prep_wrapped_messages"
    ) as Transport:
        Transport.return_value = None
        adc.return_value = (_AnonymousCredentialsWithUniverseDomain(), None)
        transport = transports.AgentsTransport()
        adc.assert_called_once()


def test_agents_auth_adc():
    # If no credentials are provided, we should use ADC credentials.
    with mock.patch.object(google.auth, "default", autospec=True) as adc:
        adc.return_value = (_AnonymousCredentialsWithUniverseDomain(), None)
        AgentsClient()
        adc.assert_called_once_with(
            scopes=None,
            default_scopes=(
                "https://www.googleapis.com/auth/cloud-platform",
                "https://www.googleapis.com/auth/dialogflow",
            ),
            quota_project_id=None,
        )


@pytest.mark.parametrize(
    "transport_class",
    [
        transports.AgentsGrpcTransport,
        transports.AgentsGrpcAsyncIOTransport,
    ],
)
def test_agents_transport_auth_adc(transport_class):
    # If credentials and host are not provided, the transport class should use
    # ADC credentials.
    with mock.patch.object(google.auth, "default", autospec=True) as adc:
        adc.return_value = (_AnonymousCredentialsWithUniverseDomain(), None)
        transport_class(quota_project_id="octopus", scopes=["1", "2"])
        adc.assert_called_once_with(
            scopes=["1", "2"],
            default_scopes=(
                "https://www.googleapis.com/auth/cloud-platform",
                "https://www.googleapis.com/auth/dialogflow",
            ),
            quota_project_id="octopus",
        )


@pytest.mark.parametrize(
    "transport_class",
    [
        transports.AgentsGrpcTransport,
        transports.AgentsGrpcAsyncIOTransport,
        transports.AgentsRestTransport,
    ],
)
def test_agents_transport_auth_gdch_credentials(transport_class):
    host = "https://language.com"
    api_audience_tests = [None, "https://language2.com"]
    api_audience_expect = [host, "https://language2.com"]
    for t, e in zip(api_audience_tests, api_audience_expect):
        with mock.patch.object(google.auth, "default", autospec=True) as adc:
            gdch_mock = mock.MagicMock()
            type(gdch_mock).with_gdch_audience = mock.PropertyMock(
                return_value=gdch_mock
            )
            adc.return_value = (gdch_mock, None)
            transport_class(host=host, api_audience=t)
            gdch_mock.with_gdch_audience.assert_called_once_with(e)


@pytest.mark.parametrize(
    "transport_class,grpc_helpers",
    [
        (transports.AgentsGrpcTransport, grpc_helpers),
        (transports.AgentsGrpcAsyncIOTransport, grpc_helpers_async),
    ],
)
def test_agents_transport_create_channel(transport_class, grpc_helpers):
    # If credentials and host are not provided, the transport class should use
    # ADC credentials.
    with mock.patch.object(
        google.auth, "default", autospec=True
    ) as adc, mock.patch.object(
        grpc_helpers, "create_channel", autospec=True
    ) as create_channel:
        creds = _AnonymousCredentialsWithUniverseDomain()
        adc.return_value = (creds, None)
        transport_class(quota_project_id="octopus", scopes=["1", "2"])

        create_channel.assert_called_with(
            "dialogflow.googleapis.com:443",
            credentials=creds,
            credentials_file=None,
            quota_project_id="octopus",
            default_scopes=(
                "https://www.googleapis.com/auth/cloud-platform",
                "https://www.googleapis.com/auth/dialogflow",
            ),
            scopes=["1", "2"],
            default_host="dialogflow.googleapis.com",
            ssl_credentials=None,
            options=[
                ("grpc.max_send_message_length", -1),
                ("grpc.max_receive_message_length", -1),
            ],
        )


@pytest.mark.parametrize(
    "transport_class",
    [transports.AgentsGrpcTransport, transports.AgentsGrpcAsyncIOTransport],
)
def test_agents_grpc_transport_client_cert_source_for_mtls(transport_class):
    cred = _AnonymousCredentialsWithUniverseDomain()

    # Check ssl_channel_credentials is used if provided.
    with mock.patch.object(transport_class, "create_channel") as mock_create_channel:
        mock_ssl_channel_creds = mock.Mock()
        transport_class(
            host="squid.clam.whelk",
            credentials=cred,
            ssl_channel_credentials=mock_ssl_channel_creds,
        )
        mock_create_channel.assert_called_once_with(
            "squid.clam.whelk:443",
            credentials=cred,
            credentials_file=None,
            scopes=None,
            ssl_credentials=mock_ssl_channel_creds,
            quota_project_id=None,
            options=[
                ("grpc.max_send_message_length", -1),
                ("grpc.max_receive_message_length", -1),
            ],
        )

    # Check if ssl_channel_credentials is not provided, then client_cert_source_for_mtls
    # is used.
    with mock.patch.object(transport_class, "create_channel", return_value=mock.Mock()):
        with mock.patch("grpc.ssl_channel_credentials") as mock_ssl_cred:
            transport_class(
                credentials=cred,
                client_cert_source_for_mtls=client_cert_source_callback,
            )
            expected_cert, expected_key = client_cert_source_callback()
            mock_ssl_cred.assert_called_once_with(
                certificate_chain=expected_cert, private_key=expected_key
            )


def test_agents_http_transport_client_cert_source_for_mtls():
    cred = _AnonymousCredentialsWithUniverseDomain()
    with mock.patch(
        "google.auth.transport.requests.AuthorizedSession.configure_mtls_channel"
    ) as mock_configure_mtls_channel:
        transports.AgentsRestTransport(
            credentials=cred, client_cert_source_for_mtls=client_cert_source_callback
        )
        mock_configure_mtls_channel.assert_called_once_with(client_cert_source_callback)


def test_agents_rest_lro_client():
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport="rest",
    )
    transport = client.transport

    # Ensure that we have a api-core operations client.
    assert isinstance(
        transport.operations_client,
        operations_v1.AbstractOperationsClient,
    )

    # Ensure that subsequent calls to the property send the exact same object.
    assert transport.operations_client is transport.operations_client


@pytest.mark.parametrize(
    "transport_name",
    [
        "grpc",
        "grpc_asyncio",
        "rest",
    ],
)
def test_agents_host_no_port(transport_name):
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        client_options=client_options.ClientOptions(
            api_endpoint="dialogflow.googleapis.com"
        ),
        transport=transport_name,
    )
    assert client.transport._host == (
        "dialogflow.googleapis.com:443"
        if transport_name in ["grpc", "grpc_asyncio"]
        else "https://dialogflow.googleapis.com"
    )


@pytest.mark.parametrize(
    "transport_name",
    [
        "grpc",
        "grpc_asyncio",
        "rest",
    ],
)
def test_agents_host_with_port(transport_name):
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        client_options=client_options.ClientOptions(
            api_endpoint="dialogflow.googleapis.com:8000"
        ),
        transport=transport_name,
    )
    assert client.transport._host == (
        "dialogflow.googleapis.com:8000"
        if transport_name in ["grpc", "grpc_asyncio"]
        else "https://dialogflow.googleapis.com:8000"
    )


@pytest.mark.parametrize(
    "transport_name",
    [
        "rest",
    ],
)
def test_agents_client_transport_session_collision(transport_name):
    creds1 = _AnonymousCredentialsWithUniverseDomain()
    creds2 = _AnonymousCredentialsWithUniverseDomain()
    client1 = AgentsClient(
        credentials=creds1,
        transport=transport_name,
    )
    client2 = AgentsClient(
        credentials=creds2,
        transport=transport_name,
    )
    session1 = client1.transport.get_agent._session
    session2 = client2.transport.get_agent._session
    assert session1 != session2
    session1 = client1.transport.set_agent._session
    session2 = client2.transport.set_agent._session
    assert session1 != session2
    session1 = client1.transport.delete_agent._session
    session2 = client2.transport.delete_agent._session
    assert session1 != session2
    session1 = client1.transport.search_agents._session
    session2 = client2.transport.search_agents._session
    assert session1 != session2
    session1 = client1.transport.train_agent._session
    session2 = client2.transport.train_agent._session
    assert session1 != session2
    session1 = client1.transport.export_agent._session
    session2 = client2.transport.export_agent._session
    assert session1 != session2
    session1 = client1.transport.import_agent._session
    session2 = client2.transport.import_agent._session
    assert session1 != session2
    session1 = client1.transport.restore_agent._session
    session2 = client2.transport.restore_agent._session
    assert session1 != session2
    session1 = client1.transport.get_validation_result._session
    session2 = client2.transport.get_validation_result._session
    assert session1 != session2


def test_agents_grpc_transport_channel():
    channel = grpc.secure_channel("http://localhost/", grpc.local_channel_credentials())

    # Check that channel is used if provided.
    transport = transports.AgentsGrpcTransport(
        host="squid.clam.whelk",
        channel=channel,
    )
    assert transport.grpc_channel == channel
    assert transport._host == "squid.clam.whelk:443"
    assert transport._ssl_channel_credentials == None


def test_agents_grpc_asyncio_transport_channel():
    channel = aio.secure_channel("http://localhost/", grpc.local_channel_credentials())

    # Check that channel is used if provided.
    transport = transports.AgentsGrpcAsyncIOTransport(
        host="squid.clam.whelk",
        channel=channel,
    )
    assert transport.grpc_channel == channel
    assert transport._host == "squid.clam.whelk:443"
    assert transport._ssl_channel_credentials == None


# Remove this test when deprecated arguments (api_mtls_endpoint, client_cert_source) are
# removed from grpc/grpc_asyncio transport constructor.
@pytest.mark.parametrize(
    "transport_class",
    [transports.AgentsGrpcTransport, transports.AgentsGrpcAsyncIOTransport],
)
def test_agents_transport_channel_mtls_with_client_cert_source(transport_class):
    with mock.patch(
        "grpc.ssl_channel_credentials", autospec=True
    ) as grpc_ssl_channel_cred:
        with mock.patch.object(
            transport_class, "create_channel"
        ) as grpc_create_channel:
            mock_ssl_cred = mock.Mock()
            grpc_ssl_channel_cred.return_value = mock_ssl_cred

            mock_grpc_channel = mock.Mock()
            grpc_create_channel.return_value = mock_grpc_channel

            cred = _AnonymousCredentialsWithUniverseDomain()
            with pytest.warns(DeprecationWarning):
                with mock.patch.object(google.auth, "default") as adc:
                    adc.return_value = (cred, None)
                    transport = transport_class(
                        host="squid.clam.whelk",
                        api_mtls_endpoint="mtls.squid.clam.whelk",
                        client_cert_source=client_cert_source_callback,
                    )
                    adc.assert_called_once()

            grpc_ssl_channel_cred.assert_called_once_with(
                certificate_chain=b"cert bytes", private_key=b"key bytes"
            )
            grpc_create_channel.assert_called_once_with(
                "mtls.squid.clam.whelk:443",
                credentials=cred,
                credentials_file=None,
                scopes=None,
                ssl_credentials=mock_ssl_cred,
                quota_project_id=None,
                options=[
                    ("grpc.max_send_message_length", -1),
                    ("grpc.max_receive_message_length", -1),
                ],
            )
            assert transport.grpc_channel == mock_grpc_channel
            assert transport._ssl_channel_credentials == mock_ssl_cred


# Remove this test when deprecated arguments (api_mtls_endpoint, client_cert_source) are
# removed from grpc/grpc_asyncio transport constructor.
@pytest.mark.parametrize(
    "transport_class",
    [transports.AgentsGrpcTransport, transports.AgentsGrpcAsyncIOTransport],
)
def test_agents_transport_channel_mtls_with_adc(transport_class):
    mock_ssl_cred = mock.Mock()
    with mock.patch.multiple(
        "google.auth.transport.grpc.SslCredentials",
        __init__=mock.Mock(return_value=None),
        ssl_credentials=mock.PropertyMock(return_value=mock_ssl_cred),
    ):
        with mock.patch.object(
            transport_class, "create_channel"
        ) as grpc_create_channel:
            mock_grpc_channel = mock.Mock()
            grpc_create_channel.return_value = mock_grpc_channel
            mock_cred = mock.Mock()

            with pytest.warns(DeprecationWarning):
                transport = transport_class(
                    host="squid.clam.whelk",
                    credentials=mock_cred,
                    api_mtls_endpoint="mtls.squid.clam.whelk",
                    client_cert_source=None,
                )

            grpc_create_channel.assert_called_once_with(
                "mtls.squid.clam.whelk:443",
                credentials=mock_cred,
                credentials_file=None,
                scopes=None,
                ssl_credentials=mock_ssl_cred,
                quota_project_id=None,
                options=[
                    ("grpc.max_send_message_length", -1),
                    ("grpc.max_receive_message_length", -1),
                ],
            )
            assert transport.grpc_channel == mock_grpc_channel


def test_agents_grpc_lro_client():
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport="grpc",
    )
    transport = client.transport

    # Ensure that we have a api-core operations client.
    assert isinstance(
        transport.operations_client,
        operations_v1.OperationsClient,
    )

    # Ensure that subsequent calls to the property send the exact same object.
    assert transport.operations_client is transport.operations_client


def test_agents_grpc_lro_async_client():
    client = AgentsAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport="grpc_asyncio",
    )
    transport = client.transport

    # Ensure that we have a api-core operations client.
    assert isinstance(
        transport.operations_client,
        operations_v1.OperationsAsyncClient,
    )

    # Ensure that subsequent calls to the property send the exact same object.
    assert transport.operations_client is transport.operations_client


def test_agent_path():
    project = "squid"
    expected = "projects/{project}/agent".format(
        project=project,
    )
    actual = AgentsClient.agent_path(project)
    assert expected == actual


def test_parse_agent_path():
    expected = {
        "project": "clam",
    }
    path = AgentsClient.agent_path(**expected)

    # Check that the path construction is reversible.
    actual = AgentsClient.parse_agent_path(path)
    assert expected == actual


def test_common_billing_account_path():
    billing_account = "whelk"
    expected = "billingAccounts/{billing_account}".format(
        billing_account=billing_account,
    )
    actual = AgentsClient.common_billing_account_path(billing_account)
    assert expected == actual


def test_parse_common_billing_account_path():
    expected = {
        "billing_account": "octopus",
    }
    path = AgentsClient.common_billing_account_path(**expected)

    # Check that the path construction is reversible.
    actual = AgentsClient.parse_common_billing_account_path(path)
    assert expected == actual


def test_common_folder_path():
    folder = "oyster"
    expected = "folders/{folder}".format(
        folder=folder,
    )
    actual = AgentsClient.common_folder_path(folder)
    assert expected == actual


def test_parse_common_folder_path():
    expected = {
        "folder": "nudibranch",
    }
    path = AgentsClient.common_folder_path(**expected)

    # Check that the path construction is reversible.
    actual = AgentsClient.parse_common_folder_path(path)
    assert expected == actual


def test_common_organization_path():
    organization = "cuttlefish"
    expected = "organizations/{organization}".format(
        organization=organization,
    )
    actual = AgentsClient.common_organization_path(organization)
    assert expected == actual


def test_parse_common_organization_path():
    expected = {
        "organization": "mussel",
    }
    path = AgentsClient.common_organization_path(**expected)

    # Check that the path construction is reversible.
    actual = AgentsClient.parse_common_organization_path(path)
    assert expected == actual


def test_common_project_path():
    project = "winkle"
    expected = "projects/{project}".format(
        project=project,
    )
    actual = AgentsClient.common_project_path(project)
    assert expected == actual


def test_parse_common_project_path():
    expected = {
        "project": "nautilus",
    }
    path = AgentsClient.common_project_path(**expected)

    # Check that the path construction is reversible.
    actual = AgentsClient.parse_common_project_path(path)
    assert expected == actual


def test_common_location_path():
    project = "scallop"
    location = "abalone"
    expected = "projects/{project}/locations/{location}".format(
        project=project,
        location=location,
    )
    actual = AgentsClient.common_location_path(project, location)
    assert expected == actual


def test_parse_common_location_path():
    expected = {
        "project": "squid",
        "location": "clam",
    }
    path = AgentsClient.common_location_path(**expected)

    # Check that the path construction is reversible.
    actual = AgentsClient.parse_common_location_path(path)
    assert expected == actual


def test_client_with_default_client_info():
    client_info = gapic_v1.client_info.ClientInfo()

    with mock.patch.object(
        transports.AgentsTransport, "_prep_wrapped_messages"
    ) as prep:
        client = AgentsClient(
            credentials=_AnonymousCredentialsWithUniverseDomain(),
            client_info=client_info,
        )
        prep.assert_called_once_with(client_info)

    with mock.patch.object(
        transports.AgentsTransport, "_prep_wrapped_messages"
    ) as prep:
        transport_class = AgentsClient.get_transport_class()
        transport = transport_class(
            credentials=_AnonymousCredentialsWithUniverseDomain(),
            client_info=client_info,
        )
        prep.assert_called_once_with(client_info)


@pytest.mark.asyncio
async def test_transport_close_async():
    client = AgentsAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport="grpc_asyncio",
    )
    with mock.patch.object(
        type(getattr(client.transport, "grpc_channel")), "close"
    ) as close:
        async with client:
            close.assert_not_called()
        close.assert_called_once()


def test_get_location_rest_bad_request(
    transport: str = "rest", request_type=locations_pb2.GetLocationRequest
):
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    request = request_type()
    request = json_format.ParseDict(
        {"name": "projects/sample1/locations/sample2"}, request
    )

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.get_location(request)


@pytest.mark.parametrize(
    "request_type",
    [
        locations_pb2.GetLocationRequest,
        dict,
    ],
)
def test_get_location_rest(request_type):
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport="rest",
    )
    request_init = {"name": "projects/sample1/locations/sample2"}
    request = request_type(**request_init)
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = locations_pb2.Location()

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        response = client.get_location(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, locations_pb2.Location)


def test_list_locations_rest_bad_request(
    transport: str = "rest", request_type=locations_pb2.ListLocationsRequest
):
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    request = request_type()
    request = json_format.ParseDict({"name": "projects/sample1"}, request)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.list_locations(request)


@pytest.mark.parametrize(
    "request_type",
    [
        locations_pb2.ListLocationsRequest,
        dict,
    ],
)
def test_list_locations_rest(request_type):
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport="rest",
    )
    request_init = {"name": "projects/sample1"}
    request = request_type(**request_init)
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = locations_pb2.ListLocationsResponse()

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        response = client.list_locations(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, locations_pb2.ListLocationsResponse)


def test_cancel_operation_rest_bad_request(
    transport: str = "rest", request_type=operations_pb2.CancelOperationRequest
):
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    request = request_type()
    request = json_format.ParseDict(
        {"name": "projects/sample1/operations/sample2"}, request
    )

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.cancel_operation(request)


@pytest.mark.parametrize(
    "request_type",
    [
        operations_pb2.CancelOperationRequest,
        dict,
    ],
)
def test_cancel_operation_rest(request_type):
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport="rest",
    )
    request_init = {"name": "projects/sample1/operations/sample2"}
    request = request_type(**request_init)
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = None

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = "{}"

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        response = client.cancel_operation(request)

    # Establish that the response is the type that we expect.
    assert response is None


def test_get_operation_rest_bad_request(
    transport: str = "rest", request_type=operations_pb2.GetOperationRequest
):
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    request = request_type()
    request = json_format.ParseDict(
        {"name": "projects/sample1/operations/sample2"}, request
    )

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.get_operation(request)


@pytest.mark.parametrize(
    "request_type",
    [
        operations_pb2.GetOperationRequest,
        dict,
    ],
)
def test_get_operation_rest(request_type):
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport="rest",
    )
    request_init = {"name": "projects/sample1/operations/sample2"}
    request = request_type(**request_init)
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.Operation()

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        response = client.get_operation(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, operations_pb2.Operation)


def test_list_operations_rest_bad_request(
    transport: str = "rest", request_type=operations_pb2.ListOperationsRequest
):
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    request = request_type()
    request = json_format.ParseDict({"name": "projects/sample1"}, request)

    # Mock the http request call within the method and fake a BadRequest error.
    with mock.patch.object(Session, "request") as req, pytest.raises(
        core_exceptions.BadRequest
    ):
        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 400
        response_value.request = Request()
        req.return_value = response_value
        client.list_operations(request)


@pytest.mark.parametrize(
    "request_type",
    [
        operations_pb2.ListOperationsRequest,
        dict,
    ],
)
def test_list_operations_rest(request_type):
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport="rest",
    )
    request_init = {"name": "projects/sample1"}
    request = request_type(**request_init)
    # Mock the http request call within the method and fake a response.
    with mock.patch.object(type(client.transport._session), "request") as req:
        # Designate an appropriate value for the returned response.
        return_value = operations_pb2.ListOperationsResponse()

        # Wrap the value into a proper Response obj
        response_value = Response()
        response_value.status_code = 200
        json_return_value = json_format.MessageToJson(return_value)

        response_value._content = json_return_value.encode("UTF-8")
        req.return_value = response_value

        response = client.list_operations(request)

    # Establish that the response is the type that we expect.
    assert isinstance(response, operations_pb2.ListOperationsResponse)


def test_cancel_operation(transport: str = "grpc"):
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = operations_pb2.CancelOperationRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.cancel_operation), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = None
        response = client.cancel_operation(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert response is None


@pytest.mark.asyncio
async def test_cancel_operation_async(transport: str = "grpc_asyncio"):
    client = AgentsAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = operations_pb2.CancelOperationRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.cancel_operation), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        response = await client.cancel_operation(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert response is None


def test_cancel_operation_field_headers():
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = operations_pb2.CancelOperationRequest()
    request.name = "locations"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.cancel_operation), "__call__") as call:
        call.return_value = None

        client.cancel_operation(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "name=locations",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_cancel_operation_field_headers_async():
    client = AgentsAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = operations_pb2.CancelOperationRequest()
    request.name = "locations"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.cancel_operation), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        await client.cancel_operation(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "name=locations",
    ) in kw["metadata"]


def test_cancel_operation_from_dict():
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.cancel_operation), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        response = client.cancel_operation(
            request={
                "name": "locations",
            }
        )
        call.assert_called()


@pytest.mark.asyncio
async def test_cancel_operation_from_dict_async():
    client = AgentsAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.cancel_operation), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(None)
        response = await client.cancel_operation(
            request={
                "name": "locations",
            }
        )
        call.assert_called()


def test_get_operation(transport: str = "grpc"):
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = operations_pb2.GetOperationRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_operation), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation()
        response = client.get_operation(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, operations_pb2.Operation)


@pytest.mark.asyncio
async def test_get_operation_async(transport: str = "grpc_asyncio"):
    client = AgentsAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = operations_pb2.GetOperationRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_operation), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation()
        )
        response = await client.get_operation(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, operations_pb2.Operation)


def test_get_operation_field_headers():
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = operations_pb2.GetOperationRequest()
    request.name = "locations"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_operation), "__call__") as call:
        call.return_value = operations_pb2.Operation()

        client.get_operation(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "name=locations",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_get_operation_field_headers_async():
    client = AgentsAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = operations_pb2.GetOperationRequest()
    request.name = "locations"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_operation), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation()
        )
        await client.get_operation(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "name=locations",
    ) in kw["metadata"]


def test_get_operation_from_dict():
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_operation), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation()

        response = client.get_operation(
            request={
                "name": "locations",
            }
        )
        call.assert_called()


@pytest.mark.asyncio
async def test_get_operation_from_dict_async():
    client = AgentsAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_operation), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.Operation()
        )
        response = await client.get_operation(
            request={
                "name": "locations",
            }
        )
        call.assert_called()


def test_list_operations(transport: str = "grpc"):
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = operations_pb2.ListOperationsRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_operations), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.ListOperationsResponse()
        response = client.list_operations(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, operations_pb2.ListOperationsResponse)


@pytest.mark.asyncio
async def test_list_operations_async(transport: str = "grpc_asyncio"):
    client = AgentsAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = operations_pb2.ListOperationsRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_operations), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.ListOperationsResponse()
        )
        response = await client.list_operations(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, operations_pb2.ListOperationsResponse)


def test_list_operations_field_headers():
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = operations_pb2.ListOperationsRequest()
    request.name = "locations"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_operations), "__call__") as call:
        call.return_value = operations_pb2.ListOperationsResponse()

        client.list_operations(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "name=locations",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_list_operations_field_headers_async():
    client = AgentsAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = operations_pb2.ListOperationsRequest()
    request.name = "locations"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_operations), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.ListOperationsResponse()
        )
        await client.list_operations(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "name=locations",
    ) in kw["metadata"]


def test_list_operations_from_dict():
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_operations), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.ListOperationsResponse()

        response = client.list_operations(
            request={
                "name": "locations",
            }
        )
        call.assert_called()


@pytest.mark.asyncio
async def test_list_operations_from_dict_async():
    client = AgentsAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_operations), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            operations_pb2.ListOperationsResponse()
        )
        response = await client.list_operations(
            request={
                "name": "locations",
            }
        )
        call.assert_called()


def test_list_locations(transport: str = "grpc"):
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = locations_pb2.ListLocationsRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_locations), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = locations_pb2.ListLocationsResponse()
        response = client.list_locations(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, locations_pb2.ListLocationsResponse)


@pytest.mark.asyncio
async def test_list_locations_async(transport: str = "grpc_asyncio"):
    client = AgentsAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = locations_pb2.ListLocationsRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_locations), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            locations_pb2.ListLocationsResponse()
        )
        response = await client.list_locations(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, locations_pb2.ListLocationsResponse)


def test_list_locations_field_headers():
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = locations_pb2.ListLocationsRequest()
    request.name = "locations"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_locations), "__call__") as call:
        call.return_value = locations_pb2.ListLocationsResponse()

        client.list_locations(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "name=locations",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_list_locations_field_headers_async():
    client = AgentsAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = locations_pb2.ListLocationsRequest()
    request.name = "locations"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_locations), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            locations_pb2.ListLocationsResponse()
        )
        await client.list_locations(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "name=locations",
    ) in kw["metadata"]


def test_list_locations_from_dict():
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_locations), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = locations_pb2.ListLocationsResponse()

        response = client.list_locations(
            request={
                "name": "locations",
            }
        )
        call.assert_called()


@pytest.mark.asyncio
async def test_list_locations_from_dict_async():
    client = AgentsAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_locations), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            locations_pb2.ListLocationsResponse()
        )
        response = await client.list_locations(
            request={
                "name": "locations",
            }
        )
        call.assert_called()


def test_get_location(transport: str = "grpc"):
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = locations_pb2.GetLocationRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_location), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = locations_pb2.Location()
        response = client.get_location(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, locations_pb2.Location)


@pytest.mark.asyncio
async def test_get_location_async(transport: str = "grpc_asyncio"):
    client = AgentsAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = locations_pb2.GetLocationRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_location), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            locations_pb2.Location()
        )
        response = await client.get_location(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, locations_pb2.Location)


def test_get_location_field_headers():
    client = AgentsClient(credentials=_AnonymousCredentialsWithUniverseDomain())

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = locations_pb2.GetLocationRequest()
    request.name = "locations/abc"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_location), "__call__") as call:
        call.return_value = locations_pb2.Location()

        client.get_location(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "name=locations/abc",
    ) in kw["metadata"]


@pytest.mark.asyncio
async def test_get_location_field_headers_async():
    client = AgentsAsyncClient(credentials=_AnonymousCredentialsWithUniverseDomain())

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = locations_pb2.GetLocationRequest()
    request.name = "locations/abc"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_location), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            locations_pb2.Location()
        )
        await client.get_location(request)
        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        "x-goog-request-params",
        "name=locations/abc",
    ) in kw["metadata"]


def test_get_location_from_dict():
    client = AgentsClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_locations), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = locations_pb2.Location()

        response = client.get_location(
            request={
                "name": "locations/abc",
            }
        )
        call.assert_called()


@pytest.mark.asyncio
async def test_get_location_from_dict_async():
    client = AgentsAsyncClient(
        credentials=_AnonymousCredentialsWithUniverseDomain(),
    )
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.list_locations), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            locations_pb2.Location()
        )
        response = await client.get_location(
            request={
                "name": "locations",
            }
        )
        call.assert_called()


def test_transport_close():
    transports = {
        "rest": "_session",
        "grpc": "_grpc_channel",
    }

    for transport, close_name in transports.items():
        client = AgentsClient(
            credentials=_AnonymousCredentialsWithUniverseDomain(), transport=transport
        )
        with mock.patch.object(
            type(getattr(client.transport, close_name)), "close"
        ) as close:
            with client:
                close.assert_not_called()
            close.assert_called_once()


def test_client_ctx():
    transports = [
        "rest",
        "grpc",
    ]
    for transport in transports:
        client = AgentsClient(
            credentials=_AnonymousCredentialsWithUniverseDomain(), transport=transport
        )
        # Test client calls underlying transport.
        with mock.patch.object(type(client.transport), "close") as close:
            close.assert_not_called()
            with client:
                pass
            close.assert_called()


@pytest.mark.parametrize(
    "client_class,transport_class",
    [
        (AgentsClient, transports.AgentsGrpcTransport),
        (AgentsAsyncClient, transports.AgentsGrpcAsyncIOTransport),
    ],
)
def test_api_key_credentials(client_class, transport_class):
    with mock.patch.object(
        google.auth._default, "get_api_key_credentials", create=True
    ) as get_api_key_credentials:
        mock_cred = mock.Mock()
        get_api_key_credentials.return_value = mock_cred
        options = client_options.ClientOptions()
        options.api_key = "api_key"
        with mock.patch.object(transport_class, "__init__") as patched:
            patched.return_value = None
            client = client_class(client_options=options)
            patched.assert_called_once_with(
                credentials=mock_cred,
                credentials_file=None,
                host=client._DEFAULT_ENDPOINT_TEMPLATE.format(
                    UNIVERSE_DOMAIN=client._DEFAULT_UNIVERSE
                ),
                scopes=None,
                client_cert_source_for_mtls=None,
                quota_project_id=None,
                client_info=transports.base.DEFAULT_CLIENT_INFO,
                always_use_jwt_access=True,
                api_audience=None,
            )
