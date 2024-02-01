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
import abc
from typing import Awaitable, Callable, Dict, Optional, Sequence, Union

import google.api_core
from google.api_core import exceptions as core_exceptions
from google.api_core import gapic_v1, operations_v1
from google.api_core import retry as retries
import google.auth  # type: ignore
from google.auth import credentials as ga_credentials  # type: ignore
from google.longrunning import operations_pb2  # type: ignore
from google.oauth2 import service_account  # type: ignore
from google.protobuf import empty_pb2  # type: ignore

from google.cloud.translate_v3 import gapic_version as package_version
from google.cloud.translate_v3.types import adaptive_mt, translation_service

DEFAULT_CLIENT_INFO = gapic_v1.client_info.ClientInfo(
    gapic_version=package_version.__version__
)


class TranslationServiceTransport(abc.ABC):
    """Abstract transport class for TranslationService."""

    AUTH_SCOPES = (
        "https://www.googleapis.com/auth/cloud-platform",
        "https://www.googleapis.com/auth/cloud-translation",
    )

    DEFAULT_HOST: str = "translate.googleapis.com"

    def __init__(
        self,
        *,
        host: str = DEFAULT_HOST,
        credentials: Optional[ga_credentials.Credentials] = None,
        credentials_file: Optional[str] = None,
        scopes: Optional[Sequence[str]] = None,
        quota_project_id: Optional[str] = None,
        client_info: gapic_v1.client_info.ClientInfo = DEFAULT_CLIENT_INFO,
        always_use_jwt_access: Optional[bool] = False,
        api_audience: Optional[str] = None,
        **kwargs,
    ) -> None:
        """Instantiate the transport.

        Args:
            host (Optional[str]):
                 The hostname to connect to (default: 'translate.googleapis.com').
            credentials (Optional[google.auth.credentials.Credentials]): The
                authorization credentials to attach to requests. These
                credentials identify the application to the service; if none
                are specified, the client will attempt to ascertain the
                credentials from the environment.
            credentials_file (Optional[str]): A file with credentials that can
                be loaded with :func:`google.auth.load_credentials_from_file`.
                This argument is mutually exclusive with credentials.
            scopes (Optional[Sequence[str]]): A list of scopes.
            quota_project_id (Optional[str]): An optional project to use for billing
                and quota.
            client_info (google.api_core.gapic_v1.client_info.ClientInfo):
                The client info used to send a user-agent string along with
                API requests. If ``None``, then default info will be used.
                Generally, you only need to set this if you're developing
                your own client library.
            always_use_jwt_access (Optional[bool]): Whether self signed JWT should
                be used for service account credentials.
        """

        scopes_kwargs = {"scopes": scopes, "default_scopes": self.AUTH_SCOPES}

        # Save the scopes.
        self._scopes = scopes

        # If no credentials are provided, then determine the appropriate
        # defaults.
        if credentials and credentials_file:
            raise core_exceptions.DuplicateCredentialArgs(
                "'credentials_file' and 'credentials' are mutually exclusive"
            )

        if credentials_file is not None:
            credentials, _ = google.auth.load_credentials_from_file(
                credentials_file, **scopes_kwargs, quota_project_id=quota_project_id
            )
        elif credentials is None:
            credentials, _ = google.auth.default(
                **scopes_kwargs, quota_project_id=quota_project_id
            )
            # Don't apply audience if the credentials file passed from user.
            if hasattr(credentials, "with_gdch_audience"):
                credentials = credentials.with_gdch_audience(
                    api_audience if api_audience else host
                )

        # If the credentials are service account credentials, then always try to use self signed JWT.
        if (
            always_use_jwt_access
            and isinstance(credentials, service_account.Credentials)
            and hasattr(service_account.Credentials, "with_always_use_jwt_access")
        ):
            credentials = credentials.with_always_use_jwt_access(True)

        # Save the credentials.
        self._credentials = credentials

        # Save the hostname. Default to port 443 (HTTPS) if none is specified.
        if ":" not in host:
            host += ":443"
        self._host = host

    @property
    def host(self):
        return self._host

    def _prep_wrapped_messages(self, client_info):
        # Precompute the wrapped methods.
        self._wrapped_methods = {
            self.translate_text: gapic_v1.method.wrap_method(
                self.translate_text,
                default_timeout=600.0,
                client_info=client_info,
            ),
            self.detect_language: gapic_v1.method.wrap_method(
                self.detect_language,
                default_timeout=600.0,
                client_info=client_info,
            ),
            self.get_supported_languages: gapic_v1.method.wrap_method(
                self.get_supported_languages,
                default_retry=retries.Retry(
                    initial=0.1,
                    maximum=60.0,
                    multiplier=1.3,
                    predicate=retries.if_exception_type(
                        core_exceptions.DeadlineExceeded,
                        core_exceptions.ServiceUnavailable,
                    ),
                    deadline=600.0,
                ),
                default_timeout=600.0,
                client_info=client_info,
            ),
            self.translate_document: gapic_v1.method.wrap_method(
                self.translate_document,
                default_timeout=600.0,
                client_info=client_info,
            ),
            self.batch_translate_text: gapic_v1.method.wrap_method(
                self.batch_translate_text,
                default_timeout=600.0,
                client_info=client_info,
            ),
            self.batch_translate_document: gapic_v1.method.wrap_method(
                self.batch_translate_document,
                default_timeout=600.0,
                client_info=client_info,
            ),
            self.create_glossary: gapic_v1.method.wrap_method(
                self.create_glossary,
                default_timeout=600.0,
                client_info=client_info,
            ),
            self.list_glossaries: gapic_v1.method.wrap_method(
                self.list_glossaries,
                default_retry=retries.Retry(
                    initial=0.1,
                    maximum=60.0,
                    multiplier=1.3,
                    predicate=retries.if_exception_type(
                        core_exceptions.DeadlineExceeded,
                        core_exceptions.ServiceUnavailable,
                    ),
                    deadline=600.0,
                ),
                default_timeout=600.0,
                client_info=client_info,
            ),
            self.get_glossary: gapic_v1.method.wrap_method(
                self.get_glossary,
                default_retry=retries.Retry(
                    initial=0.1,
                    maximum=60.0,
                    multiplier=1.3,
                    predicate=retries.if_exception_type(
                        core_exceptions.DeadlineExceeded,
                        core_exceptions.ServiceUnavailable,
                    ),
                    deadline=600.0,
                ),
                default_timeout=600.0,
                client_info=client_info,
            ),
            self.delete_glossary: gapic_v1.method.wrap_method(
                self.delete_glossary,
                default_retry=retries.Retry(
                    initial=0.1,
                    maximum=60.0,
                    multiplier=1.3,
                    predicate=retries.if_exception_type(
                        core_exceptions.DeadlineExceeded,
                        core_exceptions.ServiceUnavailable,
                    ),
                    deadline=600.0,
                ),
                default_timeout=600.0,
                client_info=client_info,
            ),
            self.create_adaptive_mt_dataset: gapic_v1.method.wrap_method(
                self.create_adaptive_mt_dataset,
                default_timeout=None,
                client_info=client_info,
            ),
            self.delete_adaptive_mt_dataset: gapic_v1.method.wrap_method(
                self.delete_adaptive_mt_dataset,
                default_timeout=None,
                client_info=client_info,
            ),
            self.get_adaptive_mt_dataset: gapic_v1.method.wrap_method(
                self.get_adaptive_mt_dataset,
                default_timeout=None,
                client_info=client_info,
            ),
            self.list_adaptive_mt_datasets: gapic_v1.method.wrap_method(
                self.list_adaptive_mt_datasets,
                default_timeout=None,
                client_info=client_info,
            ),
            self.adaptive_mt_translate: gapic_v1.method.wrap_method(
                self.adaptive_mt_translate,
                default_timeout=None,
                client_info=client_info,
            ),
            self.get_adaptive_mt_file: gapic_v1.method.wrap_method(
                self.get_adaptive_mt_file,
                default_timeout=None,
                client_info=client_info,
            ),
            self.delete_adaptive_mt_file: gapic_v1.method.wrap_method(
                self.delete_adaptive_mt_file,
                default_timeout=None,
                client_info=client_info,
            ),
            self.import_adaptive_mt_file: gapic_v1.method.wrap_method(
                self.import_adaptive_mt_file,
                default_timeout=None,
                client_info=client_info,
            ),
            self.list_adaptive_mt_files: gapic_v1.method.wrap_method(
                self.list_adaptive_mt_files,
                default_timeout=None,
                client_info=client_info,
            ),
            self.list_adaptive_mt_sentences: gapic_v1.method.wrap_method(
                self.list_adaptive_mt_sentences,
                default_timeout=None,
                client_info=client_info,
            ),
        }

    def close(self):
        """Closes resources associated with the transport.

        .. warning::
             Only call this method if the transport is NOT shared
             with other clients - this may cause errors in other clients!
        """
        raise NotImplementedError()

    @property
    def operations_client(self):
        """Return the client designed to process long-running operations."""
        raise NotImplementedError()

    @property
    def translate_text(
        self,
    ) -> Callable[
        [translation_service.TranslateTextRequest],
        Union[
            translation_service.TranslateTextResponse,
            Awaitable[translation_service.TranslateTextResponse],
        ],
    ]:
        raise NotImplementedError()

    @property
    def detect_language(
        self,
    ) -> Callable[
        [translation_service.DetectLanguageRequest],
        Union[
            translation_service.DetectLanguageResponse,
            Awaitable[translation_service.DetectLanguageResponse],
        ],
    ]:
        raise NotImplementedError()

    @property
    def get_supported_languages(
        self,
    ) -> Callable[
        [translation_service.GetSupportedLanguagesRequest],
        Union[
            translation_service.SupportedLanguages,
            Awaitable[translation_service.SupportedLanguages],
        ],
    ]:
        raise NotImplementedError()

    @property
    def translate_document(
        self,
    ) -> Callable[
        [translation_service.TranslateDocumentRequest],
        Union[
            translation_service.TranslateDocumentResponse,
            Awaitable[translation_service.TranslateDocumentResponse],
        ],
    ]:
        raise NotImplementedError()

    @property
    def batch_translate_text(
        self,
    ) -> Callable[
        [translation_service.BatchTranslateTextRequest],
        Union[operations_pb2.Operation, Awaitable[operations_pb2.Operation]],
    ]:
        raise NotImplementedError()

    @property
    def batch_translate_document(
        self,
    ) -> Callable[
        [translation_service.BatchTranslateDocumentRequest],
        Union[operations_pb2.Operation, Awaitable[operations_pb2.Operation]],
    ]:
        raise NotImplementedError()

    @property
    def create_glossary(
        self,
    ) -> Callable[
        [translation_service.CreateGlossaryRequest],
        Union[operations_pb2.Operation, Awaitable[operations_pb2.Operation]],
    ]:
        raise NotImplementedError()

    @property
    def list_glossaries(
        self,
    ) -> Callable[
        [translation_service.ListGlossariesRequest],
        Union[
            translation_service.ListGlossariesResponse,
            Awaitable[translation_service.ListGlossariesResponse],
        ],
    ]:
        raise NotImplementedError()

    @property
    def get_glossary(
        self,
    ) -> Callable[
        [translation_service.GetGlossaryRequest],
        Union[translation_service.Glossary, Awaitable[translation_service.Glossary]],
    ]:
        raise NotImplementedError()

    @property
    def delete_glossary(
        self,
    ) -> Callable[
        [translation_service.DeleteGlossaryRequest],
        Union[operations_pb2.Operation, Awaitable[operations_pb2.Operation]],
    ]:
        raise NotImplementedError()

    @property
    def create_adaptive_mt_dataset(
        self,
    ) -> Callable[
        [adaptive_mt.CreateAdaptiveMtDatasetRequest],
        Union[adaptive_mt.AdaptiveMtDataset, Awaitable[adaptive_mt.AdaptiveMtDataset]],
    ]:
        raise NotImplementedError()

    @property
    def delete_adaptive_mt_dataset(
        self,
    ) -> Callable[
        [adaptive_mt.DeleteAdaptiveMtDatasetRequest],
        Union[empty_pb2.Empty, Awaitable[empty_pb2.Empty]],
    ]:
        raise NotImplementedError()

    @property
    def get_adaptive_mt_dataset(
        self,
    ) -> Callable[
        [adaptive_mt.GetAdaptiveMtDatasetRequest],
        Union[adaptive_mt.AdaptiveMtDataset, Awaitable[adaptive_mt.AdaptiveMtDataset]],
    ]:
        raise NotImplementedError()

    @property
    def list_adaptive_mt_datasets(
        self,
    ) -> Callable[
        [adaptive_mt.ListAdaptiveMtDatasetsRequest],
        Union[
            adaptive_mt.ListAdaptiveMtDatasetsResponse,
            Awaitable[adaptive_mt.ListAdaptiveMtDatasetsResponse],
        ],
    ]:
        raise NotImplementedError()

    @property
    def adaptive_mt_translate(
        self,
    ) -> Callable[
        [adaptive_mt.AdaptiveMtTranslateRequest],
        Union[
            adaptive_mt.AdaptiveMtTranslateResponse,
            Awaitable[adaptive_mt.AdaptiveMtTranslateResponse],
        ],
    ]:
        raise NotImplementedError()

    @property
    def get_adaptive_mt_file(
        self,
    ) -> Callable[
        [adaptive_mt.GetAdaptiveMtFileRequest],
        Union[adaptive_mt.AdaptiveMtFile, Awaitable[adaptive_mt.AdaptiveMtFile]],
    ]:
        raise NotImplementedError()

    @property
    def delete_adaptive_mt_file(
        self,
    ) -> Callable[
        [adaptive_mt.DeleteAdaptiveMtFileRequest],
        Union[empty_pb2.Empty, Awaitable[empty_pb2.Empty]],
    ]:
        raise NotImplementedError()

    @property
    def import_adaptive_mt_file(
        self,
    ) -> Callable[
        [adaptive_mt.ImportAdaptiveMtFileRequest],
        Union[
            adaptive_mt.ImportAdaptiveMtFileResponse,
            Awaitable[adaptive_mt.ImportAdaptiveMtFileResponse],
        ],
    ]:
        raise NotImplementedError()

    @property
    def list_adaptive_mt_files(
        self,
    ) -> Callable[
        [adaptive_mt.ListAdaptiveMtFilesRequest],
        Union[
            adaptive_mt.ListAdaptiveMtFilesResponse,
            Awaitable[adaptive_mt.ListAdaptiveMtFilesResponse],
        ],
    ]:
        raise NotImplementedError()

    @property
    def list_adaptive_mt_sentences(
        self,
    ) -> Callable[
        [adaptive_mt.ListAdaptiveMtSentencesRequest],
        Union[
            adaptive_mt.ListAdaptiveMtSentencesResponse,
            Awaitable[adaptive_mt.ListAdaptiveMtSentencesResponse],
        ],
    ]:
        raise NotImplementedError()

    @property
    def kind(self) -> str:
        raise NotImplementedError()


__all__ = ("TranslationServiceTransport",)
