 A ntrack tracker
================
http://repo.cat-v.org/atrack/

Memcached namespaces:
- 'T': Keys / info_hashes -> 'Compact' style string of binary encoded ip+ports
- 'K': Keys / info_hashes -> String of | delimited peer-hashes DEPRECATED
- 'I': peer-hash -> Metadata string: 'ip|port' DEPRECATED
- 'P': peer-hash -> Anything 'true'. TODO: Should be a 'ref count'.
- 'S': "%s!%s" (Keys/info_hash, param) -> Integer
- 'D': Debug data

A peer hash is: md5("%s/%d" % (ip, port)).hexdigest()[:16]

This allows peer info to be shared and decay by itself, we will delete
references to peer from the key namespace lazily.
