#
#  fasta_get_seq_length.pl  -  a script for extracting sequence lengths
#
#  Version 0.1.0 (June 27, 2012)
#
#  Copyright (c) 2012 Kirill Kryukov
#
#  This software is provided 'as-is', without any express or implied
#  warranty. In no event will the authors be held liable for any damages
#  arising from the use of this software.
#
#  Permission is granted to anyone to use this software for any purpose,
#  including commercial applications, and to alter it and redistribute it
#  freely, subject to the following restrictions:
#
#  1. The origin of this software must not be misrepresented; you must not
#     claim that you wrote the original software. If you use this software
#     in a product, an acknowledgment in the product documentation would be
#     appreciated but is not required.
#  2. Altered source versions must be plainly marked as such, and must not be
#     misrepresented as being the original software.
#  3. This notice may not be removed or altered from any source distribution.
#

use strict;

my $seq = '';
my $chr = '';

while (<STDIN>)
{
    chomp;

    if (/^>/)
    {
        if ($seq ne '') { print $chr, " ", length($seq), "\n"; $seq = ''; }
        my @splited =  split(' ', substr($_,1));
	$chr = @splited[0];
        next;
    }

    $seq .= $_;
}

if ($seq ne '') { print $chr, " ", length($seq), "\n"; }
