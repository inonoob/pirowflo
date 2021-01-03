# ---------------------------------------------------------------------------
# Original code from the FortiusANT Repo
# https://github.com/WouterJD/FortiusANT
# ---------------------------------------------------------------------------
#

# Ref: https://docs.python.org/2/library/struct.html
# I hope that struct did not provide these constants already...
#
#                   Character  #  Byte order             Size        Alignment
native              ='@'       #  native                 native      native
no_alignment        ='='       #  native                 standard    none             no byte alignment
little_endian       ='<'       #  little-endian          standard    none
big_endian          ='>'       #  big-endian             standard    none
network             ='!'       #  network (= big-endian) standard    none


#                   Format        C Type                 Python type         Standard size   Notes
pad                 ='x'       #  pad byte               no value
char                ='c'       #  char                   string of length    1               (1)
signed_char         ='b'       #  signed char            integer             1               (3)
unsigned_char       ='B'       #  unsigned char          integer             1               (3)
boolean             ='?'       #  _Bool                  bool                1               (1)
short               ='h'       #  short                  integer             2               (3)
unsigned_short      ='H'       #  unsigned short         integer             2               (3)
int                 ='i'       #  int                    integer             4               (3)
unsigned_int        ='I'       #  unsigned int           integer             4               (3)
long                ='l'       #  long                   integer             4               (3)
unsigned_long       ='L'       #  unsigned long          integer             4               (3)
long_long           ='q'       #  long long              integer             8               (2), (3)
unsigned_long_long  ='Q'       #  unsigned long long     integer             8               (2), (3)
float               ='f'       #  float                  float               4               (4)
double              ='d'       #  double                 float               8               (4)
char_array          ='s'       #  char[]                 string
char_array2         ='p'       #  char[]                 string
void_ptr            ='P'       #  void *                 integer                             (5), (3)