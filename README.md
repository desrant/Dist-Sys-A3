# Distributed Systems Assignment 2

## Prerequisites

- **docker**: latest version


## Setup


1. Setting up Load Balancer:
   ```
   make
   ```

2. Cleaning up resources:
   ```
   clean
   ```


## Analysis

### A-1: 6 Servers, 4 Shards, 3 Replicas

![write(a1)](https://github.com/Rohan-18102001/Dist-Sys-A2/assets/61150756/e3ffbb2c-dc37-4c15-b1c9-fdaac78e8a13)


![read(a1)](https://github.com/Rohan-18102001/Dist-Sys-A2/assets/61150756/d0b2ac92-734d-439f-80b6-863e31f6227e)


### A-2: 10 Servers, 6 Shards, 8 Replicas

![write(a2)](https://github.com/Rohan-18102001/Dist-Sys-A2/assets/61150756/54c04f39-6cc1-4270-a749-b9587555ecc7)


![read(a2)](https://github.com/Rohan-18102001/Dist-Sys-A2/assets/61150756/2c05422e-9445-42e6-a051-aa9d8491a6b2)


Write speedup of a2 from a1 - 0.34094

Read speedup of a2 from a1 - 0.97184

