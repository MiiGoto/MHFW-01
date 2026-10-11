/* Independent MHFW-01 virtual I/O, Windows loopback only. No control logic. */
/* SECTION includes */
#define BOOL MH_WIN_BOOL
#define _NO_BOOL_TYPEDEF
#define INT MH_WIN_INT
#define UINT MH_WIN_UINT
#define DATE MH_WIN_DATE
#define BYTE MH_WIN_BYTE
#define WORD MH_WIN_WORD
#define DWORD MH_WIN_DWORD
#include <winsock2.h>
#undef BOOL
#undef INT
#undef UINT
#undef DATE
#undef BYTE
#undef WORD
#undef DWORD
#include <stdint.h>
#include <string.h>
#include <math.h>
/* SECTION globals */
typedef struct { char magic[4]; uint32_t sequence; float values[64]; } MHFrame;
static SOCKET mh_socket=INVALID_SOCKET;
static struct sockaddr_in mh_peer;
static MHFrame frame, reply;
static uint32_t mh_last=0;
static int mh_have=0, mh_pending=0;
static unsigned short mh_owner_port=0;
/* SECTION initFunction */
WSADATA wd; u_long nonblock=1;
struct sockaddr_in addr;
if(WSAStartup(MAKEWORD(2,2),&wd)!=0) return -1;
mh_socket=socket(AF_INET,SOCK_DGRAM,IPPROTO_UDP);
memset(&addr,0,sizeof(addr)); addr.sin_family=AF_INET; addr.sin_port=htons(15020); addr.sin_addr.s_addr=htonl(INADDR_LOOPBACK);
if(mh_socket==INVALID_SOCKET || bind(mh_socket,(struct sockaddr*)&addr,sizeof(addr))!=0) return -1;
ioctlsocket(mh_socket,FIONBIO,&nonblock);
mh_have=0; mh_pending=0; mh_owner_port=0; I_CommAge=0;
/* SECTION cleanUpFunction */
if(mh_socket!=INVALID_SOCKET) closesocket(mh_socket);
mh_socket=INVALID_SOCKET; WSACleanup();
/* SECTION retrieveFunction */
int peerlen=sizeof(mh_peer), n, valid=1;
MHFrame incoming;
I_Fresh=0; I_CommAge+=0.02f; mh_pending=0;
n=recvfrom(mh_socket,(char*)&incoming,sizeof(incoming),0,(struct sockaddr*)&mh_peer,&peerlen);
if(n==sizeof(incoming) && memcmp(incoming.magic,"MHF1",4)==0) {
    for(int j=0;j<64;j++) if(!isfinite(incoming.values[j])) valid=0;
    /* A replacement client may claim this local adapter only after the old
       client timed out. PLC alarm/reset semantics still govern restart. */
    if(valid && mh_peer.sin_port!=mh_owner_port && I_CommAge>0.5f) mh_have=0;
    if(valid && (!mh_have || incoming.sequence>mh_last)) {
        frame=incoming; mh_last=frame.sequence; mh_have=1; mh_owner_port=mh_peer.sin_port;
        INPUT_ASSIGNMENTS
        I_Fresh=1; I_CommAge=0; mh_pending=1;
    } else if(valid && mh_have && incoming.sequence==mh_last) {
        /* Keep sequence idempotent, but publish current watchdog/stop state. */
        OUTPUT_ASSIGNMENTS
        sendto(mh_socket,(char*)&reply,sizeof(reply),0,(struct sockaddr*)&mh_peer,sizeof(mh_peer));
    }
}
/* SECTION publishFunction */
if(mh_pending) {
    memset(&reply,0,sizeof(reply)); memcpy(reply.magic,"MHF1",4); reply.sequence=mh_last;
    OUTPUT_ASSIGNMENTS
    sendto(mh_socket,(char*)&reply,sizeof(reply),0,(struct sockaddr*)&mh_peer,sizeof(mh_peer));
}
