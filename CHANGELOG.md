# Changelog

## [1.7.2](https://github.com/togethercomputer/together-sandbox/compare/together-sandbox-v1.7.1...together-sandbox-v1.7.2) (2026-05-04)


### Bug Fixes

* Fix createSnapshot enum issue ([d2df7e7](https://github.com/togethercomputer/together-sandbox/commit/d2df7e79e2b640b7469611db814c02bfede4ae39))

## [1.7.1](https://github.com/togethercomputer/together-sandbox/compare/together-sandbox-v1.7.0...together-sandbox-v1.7.1) (2026-05-04)


### Bug Fixes

* fix create snapshot issue ([76234ae](https://github.com/togethercomputer/together-sandbox/commit/76234ae5c090b8175f73061a3ec2036ca2aa0d8d))
* remove _unwrap_or_raise from alias call in _build_and_register; add context-based alias unit test ([5dcb451](https://github.com/togethercomputer/together-sandbox/commit/5dcb4511128b12a999c3433522e7f9d6cc306fef))

## [1.7.0](https://github.com/togethercomputer/together-sandbox/compare/together-sandbox-v1.6.0...together-sandbox-v1.7.0) (2026-04-28)


### Features

* add wait_for_sandbox to start, hibernate and shutdown ([853c132](https://github.com/togethercomputer/together-sandbox/commit/853c132a667ff8ffc826a9ad2c387b52295fff5c))
* add wait_for_sandbox to start, hibernate and shutdown ([2f39d14](https://github.com/togethercomputer/together-sandbox/commit/2f39d1445767626a4d1c1a1dc4948d345ccae71a))
* Use the new credentials endpoint in Bartender for registry authorization ([79bc542](https://github.com/togethercomputer/together-sandbox/commit/79bc5426864520f655589a5ce24a17f139cafeed))


### Bug Fixes

* adjust to new field names ([18b04a0](https://github.com/togethercomputer/together-sandbox/commit/18b04a079ff02f188f483fa5a927ff765638f6d1))
* centralize error handling with _unwrap_or_raise helper and extend to all facade methods ([9307a46](https://github.com/togethercomputer/together-sandbox/commit/9307a469d8ef273ad6b22f68f91e7293a422e7e2))
* handle errors for sandbox operation by raising exceptions to be caught by sdk clients ([d040276](https://github.com/togethercomputer/together-sandbox/commit/d04027675ce74946320aa3c1b04ec41a5c95ef4b))

## [1.6.0](https://github.com/togethercomputer/together-sandbox/compare/together-sandbox-v1.5.2...together-sandbox-v1.6.0) (2026-04-24)


### Features

* api docs ([d877d5d](https://github.com/togethercomputer/together-sandbox/commit/d877d5dda2539fb4282961d9f7327d66aa2ab5af))
* api docs ([ca38f61](https://github.com/togethercomputer/together-sandbox/commit/ca38f61124e97d88914de6f9f398f1ec862c549a))
* Fix harbor integration issues ([75e1ae2](https://github.com/togethercomputer/together-sandbox/commit/75e1ae21b5b162f94384d458838d82e5203f2f25))

## [1.5.2](https://github.com/togethercomputer/together-sandbox/compare/together-sandbox-v1.5.1...together-sandbox-v1.5.2) (2026-04-24)


### Bug Fixes

* fix start sandbox param issue ([649e07e](https://github.com/togethercomputer/together-sandbox/commit/649e07eca701a063d2d75d80bb5bed6213bda2b8))

## [1.5.1](https://github.com/togethercomputer/together-sandbox/compare/together-sandbox-v1.5.0...together-sandbox-v1.5.1) (2026-04-23)


### Bug Fixes

* Fix harbor integration issues ([aabaf39](https://github.com/togethercomputer/together-sandbox/commit/aabaf3968efeea0298b7c021cf7670cbce891cf9))

## [1.5.0](https://github.com/togethercomputer/together-sandbox/compare/together-sandbox-v1.4.1...together-sandbox-v1.5.0) (2026-04-23)


### Features

* add alias snapshot feature, also fixes a type for get_by_id ([38393e4](https://github.com/togethercomputer/together-sandbox/commit/38393e4ca4d32a9f1e8d473724185e3a874eefeb))
* add delete snapshot methods ([0a8eec3](https://github.com/togethercomputer/together-sandbox/commit/0a8eec314a9c68bbf66d69b4b40f9e60e1c23df6))
* Add get, alias, list and delete snapshot methods ([205ec97](https://github.com/togethercomputer/together-sandbox/commit/205ec97ec04ea1a40ef996d9c59cb7177c0cedad))
* add snapshot list ([4b8f643](https://github.com/togethercomputer/together-sandbox/commit/4b8f643e24ca8038b32111ec46a7c01dbb3f0e25))
* Add snapshots getByAlias and get ([1759f6d](https://github.com/togethercomputer/together-sandbox/commit/1759f6da768e2144d820bd4bcad9785507649ed8))


### Bug Fixes

* fix api responses handling ([7bdebad](https://github.com/togethercomputer/together-sandbox/commit/7bdebad84de23d18bee1edd0c24f0cfdfba415f9))

## [1.4.1](https://github.com/togethercomputer/together-sandbox/compare/together-sandbox-v1.4.0...together-sandbox-v1.4.1) (2026-04-23)


### Bug Fixes

* Remove tasks from SDK surface ([4da2283](https://github.com/togethercomputer/together-sandbox/commit/4da22833ce75d342dd71e9a1e019193c7a3910c5))

## [1.4.0](https://github.com/togethercomputer/together-sandbox/compare/together-sandbox-v1.3.0...together-sandbox-v1.4.0) (2026-04-22)


### Features

* add get snapshot by alias api ([69a0e4e](https://github.com/togethercomputer/together-sandbox/commit/69a0e4e37fab4cb0a28d231c2be08f903b4b46a4))

## [1.3.0](https://github.com/togethercomputer/together-sandbox/compare/together-sandbox-v1.2.0...together-sandbox-v1.3.0) (2026-04-22)


### Features

* Change to create signature for sdks and cli ([fe9f89c](https://github.com/togethercomputer/together-sandbox/commit/fe9f89c56ca56a50e7b244c1f3c744694e5aaef5))
* move to create signature for CLI and TS SDK ([0c710ba](https://github.com/togethercomputer/together-sandbox/commit/0c710bad698e27c4fc136c30999f70fec2714f13))
* python SDK create signature ([f23811e](https://github.com/togethercomputer/together-sandbox/commit/f23811e06979b968d6e6e78d778ef80db5a9878d))


### Bug Fixes

* return generated code ([5b30bf2](https://github.com/togethercomputer/together-sandbox/commit/5b30bf2cb7d72159b14d72013a13b739eedd37c4))
* use camel case typing and options for TypeScript SDK ([4d07e38](https://github.com/togethercomputer/together-sandbox/commit/4d07e38113be7c480a71c416897f3250a1e8d0cc))
* use camel case typing and options for TypeScript SDK ([94bae2c](https://github.com/togethercomputer/together-sandbox/commit/94bae2c5d2536a64baac2392d68b1f6cf9d2b573))

## [1.2.0](https://github.com/togethercomputer/together-sandbox/compare/together-sandbox-v1.1.1...together-sandbox-v1.2.0) (2026-04-20)


### Features

* add python docker logic ([8e472a7](https://github.com/togethercomputer/together-sandbox/commit/8e472a7721054cfd654e7cec3ab11371b5d3242e))
* adjust to bartender api and normalize return types ([2635bde](https://github.com/togethercomputer/together-sandbox/commit/2635bde7d2728c927b86fd1d77d80a801587c5b6))
* docs updates and sandbox creation ([f87824f](https://github.com/togethercomputer/together-sandbox/commit/f87824fd8c65c63ed9ca7f4c03f7c161b57f4d7a))
* normalize return types ([17882a7](https://github.com/togethercomputer/together-sandbox/commit/17882a76e8bb7753aa35c68cd49837a9646a05f2))
* Normalize return types and use Bartender for api ([b0f9b58](https://github.com/togethercomputer/together-sandbox/commit/b0f9b5896b5d2b489346fa3645dca03313aa5f2e))
* snapshot creation TS SDK, used by CLI ([f44d509](https://github.com/togethercomputer/together-sandbox/commit/f44d509ce9f035d87115513662d83c9cd53aa755))


### Bug Fixes

* adjust to from_build and from_image ([bee8477](https://github.com/togethercomputer/together-sandbox/commit/bee8477103538e5bc786fa4f3e3e4a4402f164f6))
* Make python facade consistent ([e45460a](https://github.com/togethercomputer/together-sandbox/commit/e45460ae772c5e81dc75b94409450a5af0bb31a1))
* no build on from_image ([bce3d39](https://github.com/togethercomputer/together-sandbox/commit/bce3d3932d160802c70316dac4cc8a98d757246e))

## [1.1.1](https://github.com/togethercomputer/together-sandbox/compare/together-sandbox-v1.1.0...together-sandbox-v1.1.1) (2026-04-09)


### Bug Fixes

* bundle correctly for esm vs cjs ([001accd](https://github.com/togethercomputer/together-sandbox/commit/001accd83e5e03868f7faa07124a9e78e469ca67))
* bundle correctly for esm vs cjs ([2b984fc](https://github.com/togethercomputer/together-sandbox/commit/2b984fcd8122d6495b63ec89ddf24874448e30db))
* merge test deps into dev extra for simpler onboarding ([ed2dbca](https://github.com/togethercomputer/together-sandbox/commit/ed2dbca163e32bb7be316f17f9bd42ab9d3ca094))
* remove hibernate_by_id and shutdown_by_id from Sandbox facade ([f6e7ab5](https://github.com/togethercomputer/together-sandbox/commit/f6e7ab5789d6056eb347a12a94a3b5d1a46705be))
* Remove hibernate_by_id and shutdown_by_id, and improve python development onboarding ([6bc03d5](https://github.com/togethercomputer/together-sandbox/commit/6bc03d5d908c77713528b17b4479bd11bd8ab479))
* remove preview-hosts ([5155ad0](https://github.com/togethercomputer/together-sandbox/commit/5155ad058c13b3fd26e50ce035acf36ccd2230de))
* remove preview-hosts ([33892b9](https://github.com/togethercomputer/together-sandbox/commit/33892b932110f8bcc7ee5b1509dfaa2138b5c7eb))

## [1.1.0](https://github.com/togethercomputer/together-sandbox/compare/together-sandbox-v1.0.0...together-sandbox-v1.1.0) (2026-04-07)


### Features

* add private installation instructions for SDKs ([183fc02](https://github.com/togethercomputer/together-sandbox/commit/183fc0261fba4ba1cc89484b5bb3aa533114b9ca))
* add private installation instructions for SDKs ([0f813ef](https://github.com/togethercomputer/together-sandbox/commit/0f813eff7c3d0bc0e53b384ee37dbd2d763b5a6a))
* add unified TogetherSandbox facade for TypeScript and Python ([683acad](https://github.com/togethercomputer/together-sandbox/commit/683acadd7c0f8a558bfd9932b43d41c54c3a3451))
* add unified TogetherSandbox facade for TypeScript and Python ([46b059f](https://github.com/togethercomputer/together-sandbox/commit/46b059f0cd0ec775935f0fcfc74fc2f0d21bfb3c))
* add updated release workflow as ..github for manual rename ([b58a336](https://github.com/togethercomputer/together-sandbox/commit/b58a33614fe8fb98e11febe679dd818ca5ddd8f4))
* migrate code generator from pyopenapi-gen to openapi-python-client ([9ff2796](https://github.com/togethercomputer/together-sandbox/commit/9ff2796f7ce605a71932b54e9ef0a0e843d3a566))
* migrate facade.py call-sites to openapi-python-client module functions ([c9444be](https://github.com/togethercomputer/together-sandbox/commit/c9444be4fc52e1098fe817db2e47553d3b08a199))
* migrate facade.py to openapi-python-client AuthenticatedClient ([c5f1a90](https://github.com/togethercomputer/together-sandbox/commit/c5f1a908698d64d9af8d81aec8b84ec86b49cfa2))
* migrate facade.py to openapi-python-client AuthenticatedClient ([e33b397](https://github.com/togethercomputer/together-sandbox/commit/e33b397a915bc73460fda50275df46bbd0f2ce8c))
* migrate facade.py to openapi-python-client AuthenticatedClient ([08e7258](https://github.com/togethercomputer/together-sandbox/commit/08e7258c2eef4c0f802aff3b3f9751d978c10418))
* Migrate Python SDK Generator — `pyopenapi-gen` → `openapi-python-client` ([2f30422](https://github.com/togethercomputer/together-sandbox/commit/2f3042256576675125d9bda7ba7de77c1a3b5f9f))
* redesign SDK API surface for consistency across TypeScript and Python ([8652cf3](https://github.com/togethercomputer/together-sandbox/commit/8652cf370beec5e162305fcc34eddc65ebc6fb04))
* redesign SDK API surface for consistency across TypeScript and Python ([5882c4a](https://github.com/togethercomputer/together-sandbox/commit/5882c4aec43fd31baf9b8383b628727649fc19d7))


### Bug Fixes

* add missing cattrs dependency to pyproject.toml ([b196b14](https://github.com/togethercomputer/together-sandbox/commit/b196b14768dd815cf686fbed0502201fa3c4c849))
* add missing cattrs runtime dependency to pyproject.toml ([d7a73d9](https://github.com/togethercomputer/together-sandbox/commit/d7a73d9dd682d13e2305bafa8caaf0d286cdfbd4))
* add missing Error101 exception class to core module ([01618a8](https://github.com/togethercomputer/together-sandbox/commit/01618a874b451d2a6afdc19cd9797463dfc856b6))
* add missing Error101 exception class to core module ([ac9de68](https://github.com/togethercomputer/together-sandbox/commit/ac9de6897d3511de977488d894301d9f4e09a6c0))
* correct CLI entry point to main.ts and fix release-please dry-run bootstrap ([2054457](https://github.com/togethercomputer/together-sandbox/commit/20544574e054f342885d2b0f2000963709d3c4fc))
* correct workflow path from ..github to .github ([7d41c8a](https://github.com/togethercomputer/together-sandbox/commit/7d41c8a8b980a246ea8e9170f39e5c5fad060e79))
* create together_sandbox dir before python client generation ([e87d9ec](https://github.com/togethercomputer/together-sandbox/commit/e87d9ec102ded7c5a774370c6eb2cc308da4adfe))
* delete kanban file ([3546598](https://github.com/togethercomputer/together-sandbox/commit/3546598d70220cb0d890145366e7d094fb4a7fde))
* fix deps install for python tests ([6a00422](https://github.com/togethercomputer/together-sandbox/commit/6a0042209b862e2b96cf0305e59f8fc948ff3c1a))
* fix deps install for python tests ([389a170](https://github.com/togethercomputer/together-sandbox/commit/389a170166b6ff98fa57e7b9386652383f7a9361))
* lower minimum Python version from 3.12 to 3.10 ([307caed](https://github.com/togethercomputer/together-sandbox/commit/307caedf652e08257ea252aad4d3dfdb2776a6a3))
* replace release-please CLI dry-run with local config validation ([70fe573](https://github.com/togethercomputer/together-sandbox/commit/70fe5735a30b63a7a86d159ee7932741f230b69c))
* restore manually-written Python facade and narrow gitignore ([c4a1a9b](https://github.com/togethercomputer/together-sandbox/commit/c4a1a9bbc9c980d1be9016061c354fa8dc9c0fad))
* **tests:** update test_facade.py for openapi-python-client migration ([0f00cf0](https://github.com/togethercomputer/together-sandbox/commit/0f00cf0b176ba39c317fb4795a85a84e49c83656))
* **tests:** update test_facade.py for openapi-python-client migration ([f88cc60](https://github.com/togethercomputer/together-sandbox/commit/f88cc6093af00b5507d3487d31223a520d16eb0e))
* update broken facade tests to match refactored facade classes ([271a013](https://github.com/togethercomputer/together-sandbox/commit/271a0134361eae73d969dcebd13deceaad6294d4))
* update broken facade tests to match refactored facade classes ([b64a847](https://github.com/togethercomputer/together-sandbox/commit/b64a847cd5d07d823aa9ab26889d50564a0376a5))
* use python3 -m openapi_python_client instead of bare CLI command ([c426e12](https://github.com/togethercomputer/together-sandbox/commit/c426e12826d8cd8a6eb8fe7c0729db2de160ff05))
