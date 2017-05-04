# AWS Reserved vs OD

The Script helps to identified all the reserved instance purchased vs Running machines across multiple accounts
and gives the Type and Count of machines running under OnDemand. Instances which are running under spot lifecycle are
not considered.

1. Enable multiple session in aws credentials file if no session are mentioned consider 'default' session. .