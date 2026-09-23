/* Project-authored bounded memory bridge for Mark Adler's unmodified blast.c. */
#include <stddef.h>
#include <string.h>
#include "blast.h"
typedef struct { const unsigned char *src; unsigned n; unsigned char *dst; unsigned cap, used; } Buffer;
static unsigned input(void *ctx, unsigned char **buf) { Buffer *b=ctx; unsigned n=b->n; *buf=(unsigned char *)b->src; b->n=0; return n; }
static int output(void *ctx, unsigned char *buf, unsigned len) { Buffer *b=ctx; if (len>b->cap-b->used) return 1; memcpy(b->dst+b->used,buf,len); b->used+=len; return 0; }
int blast_memory(const unsigned char *src, unsigned n, unsigned char *dst, unsigned cap) { Buffer b={src,n,dst,cap,0}; int r=blast(input,&b,output,&b,0,0); return r ? r : (b.used==cap ? 0 : -99); }
