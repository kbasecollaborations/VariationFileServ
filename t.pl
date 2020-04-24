
use strict;
my $val = `(docker ps -a -q)`;
my @v = split ("\n", $val);
print $v[0];
my $ix = `(docker logs $v[0])`;
print $ix;
