from random import choice as rand_choice
from requests import get
from socket import SOCK_DGRAM, SOCK_STREAM, AF_INET, socket
from time import sleep, time
from icmplib import ping as Ping
from yarl import URL
from contextlib import suppress
from itertools import cycle
from sys import argv


colors = cycle([30, 31, 32, 33, 34, 35, 36, 90, 91, 92, 93, 94, 95, 96])

class Utils:
    percent = lambda part, whole: 100 * float(part) / float(whole)
    
    @staticmethod
    def ping_sizer(lists):
        return (min(lists, key=int), max(lists, key=int), round(sum(lists) / len(lists), 2)) if lists else (0, 0, 0)

    @staticmethod
    def status(request, method):
        if method == "HTTP":
            s = str(request[1])
        elif method == "UDP":
            s = "LOAD OR FILTER"
        elif request[1]:
            s = "LOAD"
        else: 
            s = "OVERLOAD"
            sleep(5)
        return s
    
def c(TYP, TXT):
    return str("\033["+str(TXT)+";"+str(TYP)+";40m")

non = c(1, 0)


class Pinger:
    @staticmethod
    def ICMP(IP, PORT):
        try:
            r = Ping(IP, count=1, timeout=5)
            return round(r.avg_rtt, 2), r.is_alive
        except:
            return 0, False

    @staticmethod
    def HTTP(URL, PORT):
        try:
            r = get(URL, timeout=5)
            r.close()
            return round(r.elapsed.total_seconds() * 1000, 2), r.status_code
        except Exception as e:
            return 5000, 408

    @staticmethod
    def TCP(IP, PORT):
        ts = time()
        try:
            s = socket(AF_INET, SOCK_STREAM)
            s.settimeout(5)
            s.connect((str(IP), int(PORT)))
            s.close()
            return round((time() - ts) * 1000, 2), True
        except:
            return round((time() - ts) * 1000, 2), False
        
    @staticmethod
    def UDP(IP, PORT):
        ts = time()
        try:
            s = socket(AF_INET, SOCK_DGRAM)
            s.settimeout(5)
            s.sendto(b"ping", (str(IP), int(PORT)))
            s.recvfrom(1)
            s.close()
            return round((time() - ts) * 1000, 2), True
        except:
            return round((time() - ts) * 1000, 2), False


    @staticmethod
    def select(TXT):
        if TXT == "TCP": return Pinger.TCP
        elif TXT == "UDP": return Pinger.UDP
        elif TXT == "ICMP": return Pinger.ICMP
        elif TXT == "HTTP": return Pinger.HTTP
        else: return None
    

def main():
    bad = 0
    counter = 0
    pings = []
    
    method = argv[1].upper()
    target = URL(("http://" + argv[2]) if not argv[2].startswith("http://") else argv[2])
    pinger = Pinger.select(method)

    if not pinger:
        exit(method + " not found use [ICMP, TCP, UDP, HTTP]")
    
    address = target.human_repr() if method == "HTTP" else target.host
    port = target.port or 80

    with suppress(KeyboardInterrupt):
        while True:
            request = pinger(address, port)

            if not request[1]: bad += 1

            counter += 1

            sleep(0.5)
            pings.append(request[0])
            
            rnd = c(1, next(colors))

            print("[{5}{7}{6}] Reply from {5}{0}{6}{1}status {5}{3}{6} protocol {5}{4}{6} time: {5}{2}ms{6}".format(
                address,
                f" port {rnd}{port}{non} " if method not in ["ICMP", "DNS"] else " ",
                request[0],
                Utils.status(request, method),
                method,
                rnd,
                non,
                counter))

        return
    print(("\n%s Check statistics for %s:\n" \
          "     Packets: Total = %d, Good = %d, Lost = %d (%d%% loss)") %
           (method.upper(),
           address,
           counter,
           max(counter - bad, 0) ,
           bad,
           Utils.percent(bad, counter)
           ))

    pv = Utils.ping_sizer(pings)
    exit("Approximate round trip times in milli-seconds:\n"\
         "     Minimum = %dms, Maximum = %dms, Average = %dms" % (pv[0], pv[1], pv[2]))

if __name__ == "__main__":
    if len(argv) != 3:
        exit(c(1, 0) + "Usge: python " +argv[0] + " icmp https://google.com")

    print(c(1, 31) + "███████████████████████████" + non)
    print(c(1, 33) + "███████████████████████████" + non)
    print(c(1, 93) + "███████████████████████████" + non)
    print(c(1, 32) + "████████LGBT Pinger████████" + non)
    print(c(1, 36) + "███████████████████████████" + non)
    print(c(1, 34) + "███████████████████████████" + non)
    print(c(1, 35) + "███████████████████████████\n" + non)
    main()