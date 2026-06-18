# Changelog

## [3.0.0](https://github.com/togethercomputer/together-sandbox/compare/together-sandbox-workspace-v2.0.0...together-sandbox-workspace-v3.0.0) (2026-06-18)


### ⚠ BREAKING CHANGES

* **CSB-1547:** `snapshots.list()` now returns a paginated `Page` of snapshots (TypeScript `Page<Snapshot>`, Python `Page[Snapshot]`) instead of a plain `Snapshot[]` / `list[Snapshot]`.

### Features

* **CSB-1547:** add cursor pagination to list endpoints ([1ee1d1d](https://github.com/togethercomputer/together-sandbox/commit/1ee1d1d3be89ecb0932049e8c40ecfa8223ca133))

## [2.0.0](https://github.com/togethercomputer/together-sandbox/compare/together-sandbox-workspace-v1.12.0...together-sandbox-workspace-v2.0.0) (2026-06-02)


### ⚠ BREAKING CHANGES

* **CSB-1514:** default management API base URL changed from https://api.bartender.codesandbox.stream to https://api.bartender.codesandbox.io. Set TOGETHER_BASE_URL or pass base_url/baseUrl explicitly to override.

### Features

* **CSB-1514:** default SDK base URL to api.bartender.codesandbox.io ([0b47efb](https://github.com/togethercomputer/together-sandbox/commit/0b47efb385846f7e1c190c30831d7f4f96449ac7))


### Bug Fixes

* do not throw on non failing retries ([d06e41f](https://github.com/togethercomputer/together-sandbox/commit/d06e41fa8a4901e13ee2d24d6fd560633831258a))
* do not throw on non failing retries ([311e11c](https://github.com/togethercomputer/together-sandbox/commit/311e11c6a7408330d99657d4b2f4417bc81ae4b9))
* fix e2e tests prep ([94dbf58](https://github.com/togethercomputer/together-sandbox/commit/94dbf587e698b39642abee45a10be944d9eae035))
* fix e2e tests prep ([6400072](https://github.com/togethercomputer/together-sandbox/commit/640007217be1e08e75b4a602257ea80ce9846a3a))
* handle valid exceptions for continued wait for the build ([3b52af1](https://github.com/togethercomputer/together-sandbox/commit/3b52af123b21d649391d65aa521a5eff4efef926))
* **python:** remove stray `return result` fragment from RetryConfig docstring ([49019cc](https://github.com/togethercomputer/together-sandbox/commit/49019cc63152a06fa0909ba8bb038fc2cb301585))
* remove duplicate ([f7353ee](https://github.com/togethercomputer/together-sandbox/commit/f7353eea4440b958f255b355e7e294ab32cdd6e6))

## [1.12.0](https://github.com/togethercomputer/together-sandbox/compare/together-sandbox-workspace-v1.11.0...together-sandbox-workspace-v1.12.0) (2026-05-29)


### Features

* include docs in SDKs ([4ff7b45](https://github.com/togethercomputer/together-sandbox/commit/4ff7b45529b2f378feb11248c0672a48cf2c4238))
* include docs in SDKs ([b2752e0](https://github.com/togethercomputer/together-sandbox/commit/b2752e0d78d85d7ad2184778ca160e30a69d4f67))


### Bug Fixes

* fix api generation for the CLI publish ([795757b](https://github.com/togethercomputer/together-sandbox/commit/795757b23cf01c600fb3ccb6ef47bb6f12400add))
* fix api generation for the CLI publish ([93fe985](https://github.com/togethercomputer/together-sandbox/commit/93fe98523b74e24cd194503aaf9272929a7fa1b0))

## [1.11.0](https://github.com/togethercomputer/together-sandbox/compare/together-sandbox-workspace-v1.10.0...together-sandbox-workspace-v1.11.0) (2026-05-28)


### Features

* add alias snapshot feature, also fixes a type for get_by_id ([38393e4](https://github.com/togethercomputer/together-sandbox/commit/38393e4ca4d32a9f1e8d473724185e3a874eefeb))
* add delete snapshot methods ([0a8eec3](https://github.com/togethercomputer/together-sandbox/commit/0a8eec314a9c68bbf66d69b4b40f9e60e1c23df6))
* add e2e test skeleton for python sdk ([b276203](https://github.com/togethercomputer/together-sandbox/commit/b2762038a3ee4431c11300d3734578143b4f76d4))
* add exec methods to run commands in a more accessible way ([2c4bcee](https://github.com/togethercomputer/together-sandbox/commit/2c4bcee7cdfb56081d26e2db0ffcbe1b8ee479da))
* add exec methods to run commands in a more accessible way ([5b0537f](https://github.com/togethercomputer/together-sandbox/commit/5b0537faa7fd9450e59352cc3eadc71817031cc8))
* add get snapshot by alias api ([69a0e4e](https://github.com/togethercomputer/together-sandbox/commit/69a0e4e37fab4cb0a28d231c2be08f903b4b46a4))
* Add get, alias, list and delete snapshot methods ([205ec97](https://github.com/togethercomputer/together-sandbox/commit/205ec97ec04ea1a40ef996d9c59cb7177c0cedad))
* add private installation instructions for SDKs ([183fc02](https://github.com/togethercomputer/together-sandbox/commit/183fc0261fba4ba1cc89484b5bb3aa533114b9ca))
* add private installation instructions for SDKs ([0f813ef](https://github.com/togethercomputer/together-sandbox/commit/0f813eff7c3d0bc0e53b384ee37dbd2d763b5a6a))
* add python docker logic ([8e472a7](https://github.com/togethercomputer/together-sandbox/commit/8e472a7721054cfd654e7cec3ab11371b5d3242e))
* add snapshot list ([4b8f643](https://github.com/togethercomputer/together-sandbox/commit/4b8f643e24ca8038b32111ec46a7c01dbb3f0e25))
* Add snapshots getByAlias and get ([1759f6d](https://github.com/togethercomputer/together-sandbox/commit/1759f6da768e2144d820bd4bcad9785507649ed8))
* add unified TogetherSandbox facade for TypeScript and Python ([683acad](https://github.com/togethercomputer/together-sandbox/commit/683acadd7c0f8a558bfd9932b43d41c54c3a3451))
* add unified TogetherSandbox facade for TypeScript and Python ([46b059f](https://github.com/togethercomputer/together-sandbox/commit/46b059f0cd0ec775935f0fcfc74fc2f0d21bfb3c))
* add updated release workflow as ..github for manual rename ([b58a336](https://github.com/togethercomputer/together-sandbox/commit/b58a33614fe8fb98e11febe679dd818ca5ddd8f4))
* add wait_for_sandbox to start, hibernate and shutdown ([853c132](https://github.com/togethercomputer/together-sandbox/commit/853c132a667ff8ffc826a9ad2c387b52295fff5c))
* add wait_for_sandbox to start, hibernate and shutdown ([2f39d14](https://github.com/togethercomputer/together-sandbox/commit/2f39d1445767626a4d1c1a1dc4948d345ccae71a))
* adjust to bartender api and normalize return types ([2635bde](https://github.com/togethercomputer/together-sandbox/commit/2635bde7d2728c927b86fd1d77d80a801587c5b6))
* api docs ([d877d5d](https://github.com/togethercomputer/together-sandbox/commit/d877d5dda2539fb4282961d9f7327d66aa2ab5af))
* api docs ([ca38f61](https://github.com/togethercomputer/together-sandbox/commit/ca38f61124e97d88914de6f9f398f1ec862c549a))
* Build image snapshots in remote builder ([ccd4606](https://github.com/togethercomputer/together-sandbox/commit/ccd46066897b5b6cd7e36f4d710dd2b66a77e2b3))
* Change to create signature for sdks and cli ([fe9f89c](https://github.com/togethercomputer/together-sandbox/commit/fe9f89c56ca56a50e7b244c1f3c744694e5aaef5))
* docs updates and sandbox creation ([f87824f](https://github.com/togethercomputer/together-sandbox/commit/f87824fd8c65c63ed9ca7f4c03f7c161b57f4d7a))
* enhanced error handling and descriptions ([b52322a](https://github.com/togethercomputer/together-sandbox/commit/b52322a0dd2669bdeac09b2f6069c38ca11e9aea))
* enhanced error handling and descriptions ([1e4e28b](https://github.com/togethercomputer/together-sandbox/commit/1e4e28ba31e30c31024fc7aea8815a0f42510f28))
* Fix harbor integration issues ([75e1ae2](https://github.com/togethercomputer/together-sandbox/commit/75e1ae21b5b162f94384d458838d82e5203f2f25))
* Handle ctrl+c job deletion ([86c77ce](https://github.com/togethercomputer/together-sandbox/commit/86c77ce18a87d49191aeab5f8d71ecb4470ea908))
* log from remote builder to build emitter ([91411bb](https://github.com/togethercomputer/together-sandbox/commit/91411bb5de7383c4d645edd63cb143f726e2ce1e))
* migrate code generator from pyopenapi-gen to openapi-python-client ([9ff2796](https://github.com/togethercomputer/together-sandbox/commit/9ff2796f7ce605a71932b54e9ef0a0e843d3a566))
* migrate facade.py call-sites to openapi-python-client module functions ([c9444be](https://github.com/togethercomputer/together-sandbox/commit/c9444be4fc52e1098fe817db2e47553d3b08a199))
* migrate facade.py to openapi-python-client AuthenticatedClient ([c5f1a90](https://github.com/togethercomputer/together-sandbox/commit/c5f1a908698d64d9af8d81aec8b84ec86b49cfa2))
* migrate facade.py to openapi-python-client AuthenticatedClient ([e33b397](https://github.com/togethercomputer/together-sandbox/commit/e33b397a915bc73460fda50275df46bbd0f2ce8c))
* migrate facade.py to openapi-python-client AuthenticatedClient ([08e7258](https://github.com/togethercomputer/together-sandbox/commit/08e7258c2eef4c0f802aff3b3f9751d978c10418))
* Migrate Python SDK Generator — `pyopenapi-gen` → `openapi-python-client` ([2f30422](https://github.com/togethercomputer/together-sandbox/commit/2f3042256576675125d9bda7ba7de77c1a3b5f9f))
* move to create signature for CLI and TS SDK ([0c710ba](https://github.com/togethercomputer/together-sandbox/commit/0c710bad698e27c4fc136c30999f70fec2714f13))
* normalize return types ([17882a7](https://github.com/togethercomputer/together-sandbox/commit/17882a76e8bb7753aa35c68cd49837a9646a05f2))
* Normalize return types and use Bartender for api ([b0f9b58](https://github.com/togethercomputer/together-sandbox/commit/b0f9b5896b5d2b489346fa3645dca03313aa5f2e))
* normalize the surface interface of Python SDK ([8a7e59a](https://github.com/togethercomputer/together-sandbox/commit/8a7e59a970c03cc69215270e557960f6ba1740d8))
* normalize the surface interface of Python SDK ([9a41bff](https://github.com/togethercomputer/together-sandbox/commit/9a41bff82c217cdabbd0cba8df99e2a4620c826d))
* python SDK create signature ([f23811e](https://github.com/togethercomputer/together-sandbox/commit/f23811e06979b968d6e6e78d778ef80db5a9878d))
* redesign SDK API surface for consistency across TypeScript and Python ([8652cf3](https://github.com/togethercomputer/together-sandbox/commit/8652cf370beec5e162305fcc34eddc65ebc6fb04))
* redesign SDK API surface for consistency across TypeScript and Python ([5882c4a](https://github.com/togethercomputer/together-sandbox/commit/5882c4aec43fd31baf9b8383b628727649fc19d7))
* release packages ([4c598f8](https://github.com/togethercomputer/together-sandbox/commit/4c598f86baef37bd875d225308f94ad7b6ed822a))
* release packages ([f08b282](https://github.com/togethercomputer/together-sandbox/commit/f08b282308411dfac6fc5c5a8c9710ec9d5ff3c5))
* remote build ([7a2e7b0](https://github.com/togethercomputer/together-sandbox/commit/7a2e7b08151072e6966f38d77b84be1fadbb8246))
* remote build for Python sdk ([593c030](https://github.com/togethercomputer/together-sandbox/commit/593c03038eac5b29ee47eb5e95def9b826b467e8))
* remote image builder for the TypeScript SDK with SIGINT cancellation and unified retry policy ([50a3fb9](https://github.com/togethercomputer/together-sandbox/commit/50a3fb928cdb23002243b5deecef8501730b093d))
* Rename get_snapshot to get_by_alias and add get ([c826e85](https://github.com/togethercomputer/together-sandbox/commit/c826e8558579f2e7e4db685f527d5da63ce8d8e1))
* retry mechanism for known status codes ([e2e3949](https://github.com/togethercomputer/together-sandbox/commit/e2e394955e3ae1b2df6639cd9f0dc6cdadea245a))
* retry mechanism for known status codes ([3fd504a](https://github.com/togethercomputer/together-sandbox/commit/3fd504a9294601911f3f2c34eb4c79a0389b40e8))
* snapshot creation TS SDK, used by CLI ([f44d509](https://github.com/togethercomputer/together-sandbox/commit/f44d509ce9f035d87115513662d83c9cd53aa755))
* Standardize on TOGETHER_* environment variables and default machine config ([32cf4de](https://github.com/togethercomputer/together-sandbox/commit/32cf4de93a6b781924db3c485582dd202250ac7c))
* use same retry status codes for remote build and reduce retry time and tries ([43efb68](https://github.com/togethercomputer/together-sandbox/commit/43efb681b9dc95176ff844ada1ce262196c0d090))
* Use the new credentials endpoint in Bartender for registry authorization ([79bc542](https://github.com/togethercomputer/together-sandbox/commit/79bc5426864520f655589a5ce24a17f139cafeed))
* Use the new credentials endpoint in Bartender for registry authorization ([6209dbc](https://github.com/togethercomputer/together-sandbox/commit/6209dbcdb0dcbed55d9943b6a0a3cb1e230354e5))


### Bug Fixes

* add missing cattrs dependency to pyproject.toml ([b196b14](https://github.com/togethercomputer/together-sandbox/commit/b196b14768dd815cf686fbed0502201fa3c4c849))
* add missing cattrs runtime dependency to pyproject.toml ([d7a73d9](https://github.com/togethercomputer/together-sandbox/commit/d7a73d9dd682d13e2305bafa8caaf0d286cdfbd4))
* add missing Error101 exception class to core module ([01618a8](https://github.com/togethercomputer/together-sandbox/commit/01618a874b451d2a6afdc19cd9797463dfc856b6))
* add missing Error101 exception class to core module ([ac9de68](https://github.com/togethercomputer/together-sandbox/commit/ac9de6897d3511de977488d894301d9f4e09a6c0))
* adjust missing fixes to e2e tests ([4eabc5a](https://github.com/togethercomputer/together-sandbox/commit/4eabc5a1355f262ef00ba6057599e6dd0c8cd926))
* adjust to from_build and from_image ([bee8477](https://github.com/togethercomputer/together-sandbox/commit/bee8477103538e5bc786fa4f3e3e4a4402f164f6))
* adjust to new autostart, start endpoint and user+group ID option ([4a26cf0](https://github.com/togethercomputer/together-sandbox/commit/4a26cf06814fb444e3ff330953690b5acffea371))
* adjust to new autostart, start endpoint and user+group ID option ([29f339a](https://github.com/togethercomputer/together-sandbox/commit/29f339ad831e9754b8abcf5edf2580eec160e57e))
* adjust to new field names ([18b04a0](https://github.com/togethercomputer/together-sandbox/commit/18b04a079ff02f188f483fa5a927ff765638f6d1))
* adjust to new field names ([d54f104](https://github.com/togethercomputer/together-sandbox/commit/d54f104958a8f4f5bcf830cd73f7e80a0ee5c8b1))
* bad import ([4dd9600](https://github.com/togethercomputer/together-sandbox/commit/4dd96009c4957fcac0f9728de9b6d198087486a6))
* bundle correctly for esm vs cjs ([001accd](https://github.com/togethercomputer/together-sandbox/commit/001accd83e5e03868f7faa07124a9e78e469ca67))
* bundle correctly for esm vs cjs ([2b984fc](https://github.com/togethercomputer/together-sandbox/commit/2b984fcd8122d6495b63ec89ddf24874448e30db))
* centralize error handling with _unwrap_or_raise helper and extend to all facade methods ([9307a46](https://github.com/togethercomputer/together-sandbox/commit/9307a469d8ef273ad6b22f68f91e7293a422e7e2))
* correct CLI entry point to main.ts and fix release-please dry-run bootstrap ([2054457](https://github.com/togethercomputer/together-sandbox/commit/20544574e054f342885d2b0f2000963709d3c4fc))
* correct workflow path from ..github to .github ([7d41c8a](https://github.com/togethercomputer/together-sandbox/commit/7d41c8a8b980a246ea8e9170f39e5c5fad060e79))
* create together_sandbox dir before python client generation ([e87d9ec](https://github.com/togethercomputer/together-sandbox/commit/e87d9ec102ded7c5a774370c6eb2cc308da4adfe))
* delete kanban file ([3546598](https://github.com/togethercomputer/together-sandbox/commit/3546598d70220cb0d890145366e7d094fb4a7fde))
* fix api responses handling ([7bdebad](https://github.com/togethercomputer/together-sandbox/commit/7bdebad84de23d18bee1edd0c24f0cfdfba415f9))
* fix ci testing ([eaef2c1](https://github.com/togethercomputer/together-sandbox/commit/eaef2c18f0ade5c8ac2510b1cd1e81479de9b31a))
* fix ci testing ([5f24986](https://github.com/togethercomputer/together-sandbox/commit/5f24986cd69a17de7d85f10a1cd2e46a992977a4))
* fix create file api request param issue ([ad21e51](https://github.com/togethercomputer/together-sandbox/commit/ad21e51410abbb2f5d2949fa53403ef1d7e20af0))
* fix create snapshot issue ([76234ae](https://github.com/togethercomputer/together-sandbox/commit/76234ae5c090b8175f73061a3ec2036ca2aa0d8d))
* Fix createSnapshot enum issue ([d2df7e7](https://github.com/togethercomputer/together-sandbox/commit/d2df7e79e2b640b7469611db814c02bfede4ae39))
* fix deps install for python tests ([6a00422](https://github.com/togethercomputer/together-sandbox/commit/6a0042209b862e2b96cf0305e59f8fc948ff3c1a))
* fix deps install for python tests ([389a170](https://github.com/togethercomputer/together-sandbox/commit/389a170166b6ff98fa57e7b9386652383f7a9361))
* fix exec output response issue ([a6ed6fc](https://github.com/togethercomputer/together-sandbox/commit/a6ed6fcec88921a2cb54fb37e127509150d4b553))
* Fix get exec output api wrong response format ([3d629d4](https://github.com/togethercomputer/together-sandbox/commit/3d629d4ce36b005e3f98f6911923d0dfea4bee40))
* Fix harbor integration issues ([aabaf39](https://github.com/togethercomputer/together-sandbox/commit/aabaf3968efeea0298b7c021cf7670cbce891cf9))
* fix start sandbox param issue ([649e07e](https://github.com/togethercomputer/together-sandbox/commit/649e07eca701a063d2d75d80bb5bed6213bda2b8))
* guarantee snapshot id output in CLI with --ci flag ([c05220e](https://github.com/togethercomputer/together-sandbox/commit/c05220e5d1199687b90149521493313d8320db70))
* handle errors for sandbox operation by raising exceptions to be caught by sdk clients ([d040276](https://github.com/togethercomputer/together-sandbox/commit/d04027675ce74946320aa3c1b04ec41a5c95ef4b))
* lower minimum Python version from 3.12 to 3.10 ([307caed](https://github.com/togethercomputer/together-sandbox/commit/307caedf652e08257ea252aad4d3dfdb2776a6a3))
* Make python facade consistent ([e45460a](https://github.com/togethercomputer/together-sandbox/commit/e45460ae772c5e81dc75b94409450a5af0bb31a1))
* merge test deps into dev extra for simpler onboarding ([ed2dbca](https://github.com/togethercomputer/together-sandbox/commit/ed2dbca163e32bb7be316f17f9bd42ab9d3ca094))
* no build on from_image ([bce3d39](https://github.com/togethercomputer/together-sandbox/commit/bce3d3932d160802c70316dac4cc8a98d757246e))
* normalize HTTP error types across sdks and retry docker push ([fdc523f](https://github.com/togethercomputer/together-sandbox/commit/fdc523f30165ddca86f3b89c0aecf176707455f6))
* normalize HTTP error types across sdks and retry docker push ([50f2bba](https://github.com/togethercomputer/together-sandbox/commit/50f2bba505017e08129b31ad8fab84307b4fb370))
* remove _unwrap_or_raise from alias call in _build_and_register; add context-based alias unit test ([5dcb451](https://github.com/togethercomputer/together-sandbox/commit/5dcb4511128b12a999c3433522e7f9d6cc306fef))
* remove hibernate_by_id and shutdown_by_id from Sandbox facade ([f6e7ab5](https://github.com/togethercomputer/together-sandbox/commit/f6e7ab5789d6056eb347a12a94a3b5d1a46705be))
* Remove hibernate_by_id and shutdown_by_id, and improve python development onboarding ([6bc03d5](https://github.com/togethercomputer/together-sandbox/commit/6bc03d5d908c77713528b17b4479bd11bd8ab479))
* remove preview-hosts ([5155ad0](https://github.com/togethercomputer/together-sandbox/commit/5155ad058c13b3fd26e50ce035acf36ccd2230de))
* remove preview-hosts ([33892b9](https://github.com/togethercomputer/together-sandbox/commit/33892b932110f8bcc7ee5b1509dfaa2138b5c7eb))
* Remove tasks from SDK surface ([4da2283](https://github.com/togethercomputer/together-sandbox/commit/4da22833ce75d342dd71e9a1e019193c7a3910c5))
* Remove tasks from SDK surface ([72d55c8](https://github.com/togethercomputer/together-sandbox/commit/72d55c867793df38a6724797b38c76706783200d))
* replace release-please CLI dry-run with local config validation ([70fe573](https://github.com/togethercomputer/together-sandbox/commit/70fe5735a30b63a7a86d159ee7932741f230b69c))
* restore manually-written Python facade and narrow gitignore ([c4a1a9b](https://github.com/togethercomputer/together-sandbox/commit/c4a1a9bbc9c980d1be9016061c354fa8dc9c0fad))
* return generated code ([5b30bf2](https://github.com/togethercomputer/together-sandbox/commit/5b30bf2cb7d72159b14d72013a13b739eedd37c4))
* **snapshots:** correct delete_snapshot_by_alias op name typo ([2a3b64c](https://github.com/togethercomputer/together-sandbox/commit/2a3b64c9b3b8361397a4beff7cb87e9b068d8848))
* **tests:** update test_facade.py for openapi-python-client migration ([0f00cf0](https://github.com/togethercomputer/together-sandbox/commit/0f00cf0b176ba39c317fb4795a85a84e49c83656))
* **tests:** update test_facade.py for openapi-python-client migration ([f88cc60](https://github.com/togethercomputer/together-sandbox/commit/f88cc6093af00b5507d3487d31223a520d16eb0e))
* update broken facade tests to match refactored facade classes ([271a013](https://github.com/togethercomputer/together-sandbox/commit/271a0134361eae73d969dcebd13deceaad6294d4))
* update broken facade tests to match refactored facade classes ([b64a847](https://github.com/togethercomputer/together-sandbox/commit/b64a847cd5d07d823aa9ab26889d50564a0376a5))
* use camel case typing and options for TypeScript SDK ([4d07e38](https://github.com/togethercomputer/together-sandbox/commit/4d07e38113be7c480a71c416897f3250a1e8d0cc))
* use camel case typing and options for TypeScript SDK ([94bae2c](https://github.com/togethercomputer/together-sandbox/commit/94bae2c5d2536a64baac2392d68b1f6cf9d2b573))
* use python3 -m openapi_python_client instead of bare CLI command ([c426e12](https://github.com/togethercomputer/together-sandbox/commit/c426e12826d8cd8a6eb8fe7c0729db2de160ff05))

## [1.10.0](https://github.com/togethercomputer/together-sandbox/compare/together-sandbox-v1.9.0...together-sandbox-v1.10.0) (2026-05-26)


### Features

* enhanced error handling and descriptions ([b52322a](https://github.com/togethercomputer/together-sandbox/commit/b52322a0dd2669bdeac09b2f6069c38ca11e9aea))


### Bug Fixes

* fix ci testing ([eaef2c1](https://github.com/togethercomputer/together-sandbox/commit/eaef2c18f0ade5c8ac2510b1cd1e81479de9b31a))
* fix ci testing ([5f24986](https://github.com/togethercomputer/together-sandbox/commit/5f24986cd69a17de7d85f10a1cd2e46a992977a4))
* **snapshots:** correct delete_snapshot_by_alias op name typo ([2a3b64c](https://github.com/togethercomputer/together-sandbox/commit/2a3b64c9b3b8361397a4beff7cb87e9b068d8848))

## [1.9.0](https://github.com/togethercomputer/together-sandbox/compare/together-sandbox-v1.8.0...together-sandbox-v1.9.0) (2026-05-22)


### Features

* add exec methods to run commands in a more accessible way ([2c4bcee](https://github.com/togethercomputer/together-sandbox/commit/2c4bcee7cdfb56081d26e2db0ffcbe1b8ee479da))
* add exec methods to run commands in a more accessible way ([5b0537f](https://github.com/togethercomputer/together-sandbox/commit/5b0537faa7fd9450e59352cc3eadc71817031cc8))
* Build image snapshots in remote builder ([ccd4606](https://github.com/togethercomputer/together-sandbox/commit/ccd46066897b5b6cd7e36f4d710dd2b66a77e2b3))
* Handle ctrl+c job deletion ([86c77ce](https://github.com/togethercomputer/together-sandbox/commit/86c77ce18a87d49191aeab5f8d71ecb4470ea908))
* remote image builder for the TypeScript SDK with SIGINT cancellation and unified retry policy ([50a3fb9](https://github.com/togethercomputer/together-sandbox/commit/50a3fb928cdb23002243b5deecef8501730b093d))
* use same retry status codes for remote build and reduce retry time and tries ([43efb68](https://github.com/togethercomputer/together-sandbox/commit/43efb681b9dc95176ff844ada1ce262196c0d090))


### Bug Fixes

* adjust to new autostart, start endpoint and user+group ID option ([4a26cf0](https://github.com/togethercomputer/together-sandbox/commit/4a26cf06814fb444e3ff330953690b5acffea371))
* adjust to new autostart, start endpoint and user+group ID option ([29f339a](https://github.com/togethercomputer/together-sandbox/commit/29f339ad831e9754b8abcf5edf2580eec160e57e))

## [1.8.0](https://github.com/togethercomputer/together-sandbox/compare/together-sandbox-v1.7.5...together-sandbox-v1.8.0) (2026-05-12)


### Features

* add e2e test skeleton for python sdk ([b276203](https://github.com/togethercomputer/together-sandbox/commit/b2762038a3ee4431c11300d3734578143b4f76d4))
* log from remote builder to build emitter ([91411bb](https://github.com/togethercomputer/together-sandbox/commit/91411bb5de7383c4d645edd63cb143f726e2ce1e))
* normalize the surface interface of Python SDK ([8a7e59a](https://github.com/togethercomputer/together-sandbox/commit/8a7e59a970c03cc69215270e557960f6ba1740d8))
* normalize the surface interface of Python SDK ([9a41bff](https://github.com/togethercomputer/together-sandbox/commit/9a41bff82c217cdabbd0cba8df99e2a4620c826d))
* remote build ([7a2e7b0](https://github.com/togethercomputer/together-sandbox/commit/7a2e7b08151072e6966f38d77b84be1fadbb8246))
* remote build for Python sdk ([593c030](https://github.com/togethercomputer/together-sandbox/commit/593c03038eac5b29ee47eb5e95def9b826b467e8))
* retry mechanism for known status codes ([e2e3949](https://github.com/togethercomputer/together-sandbox/commit/e2e394955e3ae1b2df6639cd9f0dc6cdadea245a))
* retry mechanism for known status codes ([3fd504a](https://github.com/togethercomputer/together-sandbox/commit/3fd504a9294601911f3f2c34eb4c79a0389b40e8))
* Standardize on TOGETHER_* environment variables and default machine config ([32cf4de](https://github.com/togethercomputer/together-sandbox/commit/32cf4de93a6b781924db3c485582dd202250ac7c))


### Bug Fixes

* adjust missing fixes to e2e tests ([4eabc5a](https://github.com/togethercomputer/together-sandbox/commit/4eabc5a1355f262ef00ba6057599e6dd0c8cd926))
* guarantee snapshot id output in CLI with --ci flag ([c05220e](https://github.com/togethercomputer/together-sandbox/commit/c05220e5d1199687b90149521493313d8320db70))
* normalize HTTP error types across sdks and retry docker push ([fdc523f](https://github.com/togethercomputer/together-sandbox/commit/fdc523f30165ddca86f3b89c0aecf176707455f6))
* normalize HTTP error types across sdks and retry docker push ([50f2bba](https://github.com/togethercomputer/together-sandbox/commit/50f2bba505017e08129b31ad8fab84307b4fb370))

## [1.7.5](https://github.com/togethercomputer/together-sandbox/compare/together-sandbox-v1.7.4...together-sandbox-v1.7.5) (2026-05-06)


### Bug Fixes

* fix create file api request param issue ([ad21e51](https://github.com/togethercomputer/together-sandbox/commit/ad21e51410abbb2f5d2949fa53403ef1d7e20af0))

## [1.7.4](https://github.com/togethercomputer/together-sandbox/compare/together-sandbox-v1.7.3...together-sandbox-v1.7.4) (2026-05-05)


### Bug Fixes

* Fix get exec output api wrong response format ([3d629d4](https://github.com/togethercomputer/together-sandbox/commit/3d629d4ce36b005e3f98f6911923d0dfea4bee40))

## [1.7.3](https://github.com/togethercomputer/together-sandbox/compare/together-sandbox-v1.7.2...together-sandbox-v1.7.3) (2026-05-04)


### Bug Fixes

* fix exec output response issue ([a6ed6fc](https://github.com/togethercomputer/together-sandbox/commit/a6ed6fcec88921a2cb54fb37e127509150d4b553))

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
