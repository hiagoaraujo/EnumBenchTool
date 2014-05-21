EnumBenchTool
=============

EnumBenchTool is a test management tool for benchmarking of ENUM servers developed by the Network Computer Lab (NCL) of the Federal University of Uberlandia. This tool has been developed to automate, standardize, validate the tests and to facilitate the achievement of results.
                    
At the current stage of development, EnumBenchTool admits the servers BIND, MyDNS-NG, NSD and PowerDNS. This tool is not responsible for the benchmarking test itself, but it packs several other existing tools, simplifies the benchmarking management and makes configuration, synchronization and validation processes transparent to user. Among these packed tools, we highlight DNSPerf, which is a software developed by Nominum, widely used to analyze the performance of authoritative DNS servers. EnumBenchTool is responsible for triggering each DNSPerf test step, setting the number of emulated clients, the runtime, the query file and other parameters. In addition, EnumBenchTool is responsible for processing the results from DNSPerf. 
