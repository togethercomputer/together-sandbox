# Changelog

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
