#pragma once
struct WebAsset { const char* path; const char* mime; const unsigned char* data; unsigned size; bool gzip; };
extern const WebAsset kWebAssets[];
extern const unsigned kWebAssetCount;
