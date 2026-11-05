# Incomplete Report on Distributed Computing Systems

## Abstract
This report summarizes distributed consensus protocols and their throughput under network partitions.

## Introduction
Distributed systems require robust consensus mechanisms to maintain data integrity in the presence of node failures and network latency.

## Results
Raft achieved 1200 operations per second under low network latency. When packet loss rose above 10%, throughput dropped to 450 operations per second.

## References
1. Ongaro, D., and Ousterhout, J. (2014). In Search of an Understandable Consensus Algorithm. USENIX ATC, 10.5555/atc2014.
